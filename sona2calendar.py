from __future__ import print_function
import httplib2
import os

from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from base64 import b64decode

from constants import *

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sona2calendar-python.json
SCOPES = 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Sona Reminder to Calendar Event'


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

def listMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
    """
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages


if __name__ == '__main__':
    try:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        # Create a Gmail API service object and search for the last email with the search term
        gmail_service = discovery.build('gmail', 'v1', http=http)
        results = gmail_service.users().messages().list(userId='me', q=query_term).execute()
        if 'messages' not in results or len(results['messages']) == 0: 
            raise RuntimeError('No SONA reminder email found')
        msg_id = results['messages'][0]['id']
        msg = gmail_service.users().messages().get(userId='me', id=msg_id).execute()
        msg_body = b64decode(msg['payload']['parts'][0]['body']['data'])
        # parse message body to event information
        lines = msg_body.split('\r\n')
        events = []
        for line in lines:
            if line.startswith(line_beginnings[0]):
                event_name = alternative_study_name if len(alternative_study_name) > 0 \
                             else line[len(line_beginnings[0]):]  # study name
            elif line.startswith(line_beginnings[1]):
                info = ' on ' + line[len(line_beginnings[1]):]  # date
            elif line.startswith(line_beginnings[2]):
                info += ' at ' + line[len(line_beginnings[2]):]  # location
            elif line.startswith(line_beginnings[3]):
                event_name += ' (' + line[len(line_beginnings[3]):] + ')'  # participant name
                events.append({'name': event_name, 'info': info})

        # Create a Google Calendar API service object and add the events to calendar
        calen_service = discovery.build('calendar', 'v3', http=http)
        for event in events:
            # quick add to calendar
            created_event = calen_service.events().quickAdd(
                calendarId=google_calendar_id,
                text=event['name'] + event['info']).execute()
            # change the event name to a shorter one
            created_event['summary'] = event['name']
            updated_event = calen_service.events().update(calendarId=google_calendar_id,
                eventId=created_event['id'],
                body=created_event).execute()
            if updated_event:
                print('Event "' + event['name'] + '" added to calendar\n')

    except (errors.HttpError, RuntimeError) as error:
        print('An error occurred: %s' % error)
