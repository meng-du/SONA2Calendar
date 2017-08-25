# SONA Reminder to Google Calendar
This script takes the last Upcoming Study Reminder email you get from the SONA system, and adds the studies to a Google calendar.
If you have a server, you can set it to run this script everyday, right after the time you are supposed to get the SONA reminder email.

Note: This script only checks the emails from SONA -- the actual signups may change after SONA sends the email to you, which has to be checked manually in the SONA system.
A solution based on real-time SONA data is being developed.

### Prerequisites
- Google account with Gmail and Google Calendar
- Python 2.6 or greater
- [pip](https://pypi.python.org/pypi/pip)

### Getting Started
- Follow [Step 1 and Step 2 here](https://developers.google.com/gmail/api/quickstart/python) to enable the Gmail API.
  - Note: In Step 1.e, you may want to name your application something like "Sona Reminder to Calendar Event" instead of "Gmail API Quickstart".
    - Line #24 in `sona2calendar.py` should reflect the actual application name in your Google API console ("Product name shown to users").
- Click "ENABLE" on [this page](https://console.developers.google.com/apis/api/calendar-json.googleapis.com) to enable the Google Calendar API
- Download the files in this repository to your working directory, and make sure they are in the same folder with the `client_secret.json` file you got in Step 1.
- Change line #6 in `constants.py` to your Google calendar id
- Change line #9 in `constants.py` to your study name (which you want to display in the calendar)
- Run `python sona2calendar.py`
  - The first time you run it, a webpage should pop up and ask you to grant permission to your Google account
- You should see the events added to your calendar!
