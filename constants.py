# URL of your SONA system
sona_domain = 'https://ucla.sona-systems.com/'

# A file that includes your SONA username (on the 1st line) and password (on the second line)
sona_credentials_file = 'sona_credentials.txt'

# Google calendar id (find it in your Calendar Settings -> Calendar Address)
google_calendar_id = 'example@group.calendar.google.com'

# This dictionary defines the study names to be displayed in the calendar, if different from the study names in SONA.
# Example: {"A very long study name being used in the SONA system": "Short Study Name"}
# Change this to an empty dictionary if you want the study names to be same as in the SONA system
calendar_study_names = {'"Faces and Decisions" Study': 'Faces Study'}

# Color scheme for calendar events: if all words (separated by spaces) in a key string of this dictionary can be
# found in the information of a study timeslot, the corresponding color (value in this dictionary) will be applied
# to the calendar event of the study timeslot.
# Example: {'Rm101 Alice': '1', 'Rm102 Alice': '2', 'Rm102 Bob': '3', 'Rm103': '4'}
# See https://developers.google.com/google-apps/calendar/v3/reference/colors/get for a reference of event colors
color_scheme = {'Hyon': '2', 'Du': '3'}
