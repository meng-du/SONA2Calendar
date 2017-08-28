# SONA Studies to Google Calendar
This script scrapes the SONA system to find your upcoming study timeslots, and adds the timeslots to a Google calendar.
If you have a server, you can set it to run this script every few hours to get the timeslots synced to your Google calendar as often as you want.

### TODO
- Remove previous timeslots

### Prerequisites
- A Google account with Google Calendar enabled
- Python 2.6 or greater
- [pip](https://pypi.python.org/pypi/pip)

### Getting Started
- Follow [Step 1 and Step 2 here](https://developers.google.com/google-apps/calendar/quickstart/python) to enable the Google Calendar API.
  - Note: In Step 1.e, you may want to name your application something like "Sona Studies to Calendar Event" instead of "Google Calendar API Quickstart".
    - [Line #27 in `sona2calendar.py`](https://github.com/MetaD/sona2calendar/blob/master/sona2calendar.py#L27) should reflect the actual application name in your Google API console ("Product name shown to users").
- Download the files in this repository to your working directory, and make sure they are in the same folder with the `client_secret.json` file you got in Step 1.
- Open a terminal and navigate to your working directory. Install the required python packages with `pip install -r requirements.txt`
    - Remember to activate your virtualenv (if you have one) before installing packages
- Create a new file in the same directory and name it `sona_credentials.txt`
    - Put your SONA username and password on two separate lines in this file
- Change line [#6 in `constants.py`](https://github.com/MetaD/sona2calendar/blob/master/constants.py#L6) to reflect your Google calendar id (find it in your Calendar Settings -> Calendar Address)
- Change other things in [`constants.py`](https://github.com/MetaD/sona2calendar/blob/master/constants.py) as you want
- Run `python sona2calendar.py`
  - The first time you run it, a webpage should pop up and ask you to grant permissions to your Google account
- You should see the events added to your calendar!
