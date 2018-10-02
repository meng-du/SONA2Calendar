# SONA Studies to Google Calendar
This script scrapes the SONA system to find your upcoming study timeslots, and adds the timeslots to a Google calendar.
If you have a server, you can set it to run this script as often as you want to get the timeslots synced to your Google calendar (e.g. with [something like this](https://github.com/MetaD/sona2calendar/blob/master/auto_run.sh)).

This has only been tested with a SONA researcher account.

### Prerequisites
- A Google account with Google Calendar enabled
- Python 2.6 or greater
- [pip](https://pypi.python.org/pypi/pip)

### Getting Started
- Follow [Step 1 and Step 2 here](https://developers.google.com/google-apps/calendar/quickstart/python) to enable the Google Calendar API.
- Download the files in this repository to your working directory, and make sure you also put the `credentials.json` file you got in Step 1 in the same folder.
- Open a terminal and navigate to your working directory. Install the required python packages with `pip install -r requirements.txt`
    - Remember to activate your virtualenv (if you have one) before installing packages
- Create a new file in the same directory and name it `sona_credentials.txt`
    - On two separate lines in this file, write down your SONA username (1st line) and password (2nd line)
- Change [line #9 in `constants.py`](https://github.com/MetaD/sona2calendar/blob/master/constants.py#L9) to reflect your Google calendar id (find it in your Calendar Settings -> Calendar ID)
- Change other things in [`constants.py`](https://github.com/MetaD/sona2calendar/blob/master/constants.py) as you want
- Run `python sona2calendar.py`
  - The first time you run it, a webpage should pop up and ask you to grant permissions to your Google account
- You should see the events added to your calendar!
