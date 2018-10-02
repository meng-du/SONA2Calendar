#
# Syncing SONA Studies to Google Calendar
# Author: Meng Du
# October 2018
#

from __future__ import print_function
import httplib2
import os

from apiclient import discovery, errors
from oauth2client import file, client, tools

from bs4 import BeautifulSoup
import requests
import datetime

from constants import *
from sona_event import SonaEvent


# Constants for Google APIs
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sona2calendar-python.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'credentials.json'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    return creds


def scrape_sona_study_timeslots(all_studies_page, session, payload):
    events = {}
    studies = BeautifulSoup(all_studies_page, 'html.parser').find('tbody').findAll('tr')
    empty_slots = set()
    for study in studies:
        study_name = study.find(id=lambda x: x and x.endswith('_HyperlinkNonStudentStudyInfo'))
        if study_name is None:
            print('No active SONA study found')
            return (), ()
        study_name = study_name.get_text()
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
            # get timeslot id
            timeslot_href = timeslot.find(id=lambda x: x and x.endswith('_Submit_Modify')).get('href')
            id_start = timeslot_href.index('id=') + len('id=')
            try:
                timeslot_id = timeslot_href[id_start:timeslot_href.index('&')]
            except ValueError:  # no '&' found
                timeslot_id = timeslot_href[id_start:]
            # check if signed up
            signups = int(timeslot.find(id=lambda x: x and x.endswith('_LabelParticipantSigned')).get_text())
            if signups == 0:
                empty_slots.add(timeslot_id)
                continue
            # timeslot signed up, parse information
            # fields: date, time, participant, location, (researcher)
            field_id_endings = {'_LabelDate': 'date', '_LabelDate2': 'time', '_LabelNoSurvey': 'location'}
            timeslot_info = {field_id_endings[field_id]:
                    str(timeslot.find(id=lambda x: x and x.endswith(field_id)).get_text())
                    for field_id in field_id_endings}
            participants = timeslot.findAll(id=lambda x: x and x.endswith('_LabelStudentTimeSlot'))
            if len(participants) == 1:
                timeslot_info['participant'] = str(participants[0].get_text())
            else:
                timeslot_info['participant'] = ', '.join([str(p.get_text()) for p in participants])
            # researcher may not be there
            html_researcher = timeslot.find(id=lambda x: x and x.endswith('_LabelResearcher'))
            if html_researcher:
                timeslot_info['researcher'] = str(html_researcher.get_text())
            else:
                # get researcher name from study info page
                info_link = sona_domain + 'exp_info.aspx?' + study_link.split('?')[1].split('&')[0]
                r = session.get(info_link, data=payload)
                info = BeautifulSoup(r.text, 'html.parser')
                researcher = info.find(id=lambda x: x and x.endswith('_LabelResearcherName')).get_text()
                timeslot_info['researcher'] = str(researcher)
            if timeslot_info['researcher'] in researcher_names:
                timeslot_info['researcher'] = researcher_names[timeslot_info['researcher']]
            # construct sona event
            sona_event = SonaEvent(timeslot_id, study_name, **timeslot_info)
            if sona_event.sona_study_name in calendar_study_names:
                sona_event.calendar_study_name = calendar_study_names[sona_event.sona_study_name]
            events[timeslot_id] = sona_event
            counter += 1
        print('Found ' + str(counter) + ' upcoming timeslot(s) for ' + study_name)
    return events, empty_slots


def scrape_sona():
    # URLs
    login_page = sona_domain + 'default.aspx'
    all_studies_page = sona_domain + 'all_exp.aspx?personal=1'

    # read sona credentials from file
    with open(sona_credentials_file) as infile:
        sona_credentials = infile.read().splitlines()
    if len(sona_credentials) < 2:
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
        raise RuntimeError('SONA login failed. Please check your SONA domain and credentials.')
    print('Login successful')
    # browse all studies
    print('Fetching study list...')
    r = session.get(all_studies_page, data=payload)
    return scrape_sona_study_timeslots(r.text, session, payload)


def add_events_to_calendar():
    print('Connecting to Google calendar...')
    credentials = get_credentials()
    # Create a Google Calendar API service object
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    # Fetch events from calendar and see if anything changed
    print('Fetching events from Google calendar...')
    page_token = None
    for calendar_id in google_calendar_ids.values():
        while True:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            calevents = service.events().list(calendarId=calendar_id, pageToken=page_token, timeMin=now).execute()
            for calevent in calevents['items']:
                if 'description' in calevent:
                    timeslot_id = calevent['description']
                    event_name = calevent['summary']
                    if timeslot_id in events:  # same timeslot id
                        event = events[calevent['description']]
                        if event != calevent:
                            # update
                            if event.insert2calendar(service, calendar_id, calevent['colorId']):
                                service.events().delete(calendarId=calendar_id, eventId=calevent['id']).execute()
                                print('Event "' + event_name + '" updated')
                        else:
                            # same event
                            print('Event "' + event_name + '" already exists')
                        del events[timeslot_id]
                    elif timeslot_id in empty_slots:
                        # participant cancelled, remove calendar event
                        service.events().delete(calendarId=calendar_id, eventId=calevent['id']).execute()
                        print('Event "' + event_name + '" removed from calendar')
            page_token = calevents.get('nextPageToken')
            if not page_token:
                break
    if len(events) == 0:
        return
    # add the rest of events
    for event in events.values():
        color = '1'  # default color
        for keyword in color_scheme:  # change the event color as specified
            if event.match_keywords(keyword):
                color = color_scheme[keyword]
                break
        calendar_id = google_calendar_ids[event.sona_study_name]
        if event.insert2calendar(service, calendar_id, color):
            print('Event "' + event.calendar_summary() + '" added to calendar')


if __name__ == '__main__':
    try:
        events, empty_slots = scrape_sona()
        if len(events) == 0:
            print('No upcoming events found')
            quit(0)

        add_events_to_calendar()
        print('Done')

    except (errors.HttpError, RuntimeError) as error:
        print('An error occurred: %s' % error)
