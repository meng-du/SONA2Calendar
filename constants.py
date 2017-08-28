# URL of your SONA system
sona_domain = 'https://ucla.sona-systems.com/'
# a file that includes your SONA username (on the 1st line) and password (on the second line)
sona_credentials_file = 'sona_credentials.txt'
# google calendar id (find it in your Calendar Settings -> Calendar Address)
google_calendar_id = 'vvfa71to3uhdij1lkm6ueqkelg@group.calendar.google.com'
# a dictionary that defines the study names to be displayed in the calendar, if different from the study names in SONA
# change this to an empty dictionary if you want the study names to be same as in the SONA system
calendar_study_names = {'"Faces and Decisions" Study': 'Faces Study'}
# color scheme for calendar events: if all words (separated by spaces) in a key string of this dictionary can be
# found in the information of the study, the corresponding color id (value in this dictionary) will be applied
# to the event.
# Example: {'Rm101 Alice': '1', 'Rm102 Alice': '2', 'Rm102 Bob': '3'}
# see https://developers.google.com/google-apps/calendar/v3/reference/colors/get for a reference for event colors
color_scheme = {'Hyon': '2', 'Du': '3'}
