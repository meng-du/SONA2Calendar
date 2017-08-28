from __future__ import print_function
import httplib2
import os

from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from bs4 import BeautifulSoup
import requests

from constants import *
from sona_event import SonaEvent

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Constants for Google API
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sona2calendar-python.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Sona Studies to Calendar Event'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sona2calendar-python.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def scrape_sona_study_timeslots(all_studies_page, session, payload):
    events = []
    studies = BeautifulSoup(all_studies_page, 'html.parser').find('tbody').findAll('tr')
    for study in studies:
        study_name = study.find(id=lambda x: x and x.endswith('_HyperlinkNonStudentStudyInfo')).get_text()
        study_link = study.find(id=lambda x: x and x.endswith('_HyperlinkTimeSlot')).get('href')
        study_link += '&p_show=U'  # show upcoming timeslots only
        # go to the timeslot page
        print('Fetching timeslots for ' + study_name + '...')
        r = session.get(sona_domain + study_link, data=payload)
        # get timeslots
        timetable = BeautifulSoup(r.text, 'html.parser').find('tbody')
        if not timetable:
            continue
        timeslots = timetable.findAll('tr')
        counter = 0
        for timeslot in timeslots[1:]:
            signed_up = int(timeslot.find(id=lambda x: x and x.endswith('_LabelParticipantSigned')).get_text()) > 0
            if not signed_up:
                continue
            # timeslot signed up, parse information
            # fields: date, time, participant, location, researcher
            field_id_endings = ['_LabelDate', '_LabelDate2', '_LabelStudentTimeSlot', '_LabelNoSurvey',
                                '_LabelResearcher']
            timeslot_info = [str(timeslot.find(id=lambda x: x and x.endswith(field_id)).get_text())
                             for field_id in field_id_endings]
            sona_event = SonaEvent(study_name, *timeslot_info)
            if sona_event.sona_study_name in calendar_study_names:
                sona_event.calendar_study_name = calendar_study_names[sona_event.sona_study_name]
            events.append(sona_event)
            counter += 1
        print('Found ' + str(counter) + ' upcoming timeslots for ' + study_name)
    return events


def scrape_sona():
    # URLs
    login_page = sona_domain + 'default.aspx'
    all_studies_page = sona_domain + 'all_exp.aspx?personal=1'

    # read sona credentials from file
    with open(sona_credentials_file) as infile:
        sona_credentials = infile.read().splitlines()
    if len(sona_credentials) != 2:
        raise RuntimeError('Invalid SONA credentials')
    payload = {
        'ctl00$ContentPlaceHolder1$userid': sona_credentials[0],
        'ctl00$ContentPlaceHolder1$pw': sona_credentials[1],
        'ctl00$ContentPlaceHolder1$default_auth_button': 'Log In'
    }
    # connect to sona website
    print('Connecting to SONA...')
    session = requests.Session()
    r = session.get(sona_domain)
    # get aspnet hidden values
    soup = BeautifulSoup(r.text, 'html.parser')
    aspnet_fields = soup.findAll(type='hidden')
    for field in aspnet_fields:
        field_name = str(field.get('name'))
        if field_name.startswith('__'):
            payload[field_name] = str(field.get('value'))
    # log in
    print('Logging in...')
    r = session.post(login_page, data=payload)
    if 'Login failed' in r.text:
        raise RuntimeError('SONA login failed. Please check your credentials.')
    print('Login successful.')
    # browse all studies
    print('Fetching study list...')
    r = session.get(all_studies_page, data=payload)
    return scrape_sona_study_timeslots(r.text, session, payload)


def add_events_to_calendar(events):
    print('Connecting to Google calendar...')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    # Create a Google Calendar API service object and add the events to calendar
    calen_service = discovery.build('calendar', 'v3', http=http)
    for event in events:
        # quick add to calendar
        created_event = calen_service.events().quickAdd(
            calendarId=google_calendar_id,
            text=event.summary()).execute()
        added = True
        # # check for duplicates
        page_token = None
        while True:
            calevents = calen_service.events().list(
                calendarId=google_calendar_id,
                timeMin=created_event['start']['dateTime'],
                timeMax=created_event['end']['dateTime'], pageToken=page_token).execute()
            for calevent in calevents['items']:
                if calevent['id'] != created_event['id'] and calevent['summary'] == event.calendar_title():
                    calen_service.events().delete(calendarId=google_calendar_id, eventId=created_event['id']).execute()
                    added = False
                    print('Event "' + event.calendar_title() + '" already exists.\n')
                    break
            page_token = calevents.get('nextPageToken')
            if not added or not page_token:
                break
        if added:
            # change the event name to a shorter one
            created_event['summary'] = event.calendar_title()
            updated_event = calen_service.events().update(calendarId=google_calendar_id,
                                                          eventId=created_event['id'],
                                                          body=created_event).execute()
            if updated_event:
                print('Event "' + event.calendar_title() + '" added to calendar.\n')


if __name__ == '__main__':
    try:
        events = scrape_sona()
        if len(events) == 0:
            print('No upcoming events found.')
            quit(0)

        add_events_to_calendar(events)
        print('Done.')

    except (errors.HttpError, RuntimeError) as error:
        print('An error occurred: %s' % error)
