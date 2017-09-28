#
# SONA Event class
# Author: Meng Du
# August 2017
#

from datetime import datetime
from dateutil import tz, parser


class SonaEvent:
    def __init__(self, slot_id, sona_study_name, date, time, participant, location, researcher):
        self.id = slot_id
        self.sona_study_name = sona_study_name
        self.participant = participant
        self.location = location
        self.researcher = researcher
        self.calendar_study_name = self.sona_study_name
        self.start_time, self.end_time = self.string2time(date + ' ' + time)

    @classmethod
    def string2time(cls, string):
        if len(string) == 0:
            return datetime.max
        divide = string.index(' - ')
        string1 = string[:divide]
        string2 = string[divide:]
        time1 = datetime.strptime(string1, '%A, %B %d, %Y %I:%M %p')
        time1 = time1.replace(tzinfo=tz.tzlocal())
        time2 = datetime.strptime(string2, ' - %I:%M %p')
        time2 = time2.replace(year=time1.year, month=time1.month, day=time1.day, tzinfo=tz.tzlocal())
        return time1, time2

    def __str__(self):
        return self.calendar_study_name + ' (id: ' + self.id + ')' + \
               '\n\tSONA study name: ' + self.sona_study_name + \
               '\n\tTimeslot: ' + self.start_time + \
               '\n\tParticipant: ' + self.participant + \
               '\n\tLocation: ' + self.location + \
               '\n\tResearcher: ' + self.researcher

    def __eq__(self, other):
        if isinstance(other, SonaEvent):
            return self.id == other.id and self.start_time == other.start_time and self.end_time == other.end_time and \
                   self.participant == other.participant
        if isinstance(other, dict):
            # a Google Calendar event dict
            try:
                start_time = parser.parse(other['start']['dateTime'])
                end_time = parser.parse(other['end']['dateTime'])
                same = ('description' not in other or self.id == other['description']) and \
                       self.start_time == start_time and \
                       self.end_time == end_time and \
                       self.participant in other['summary'] and \
                       self.researcher.split()[0] in other['summary'] and \
                       other['summary'].startswith(self.calendar_study_name)
                return same
            except KeyError:
                return False
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else (not result)

    def quick_add_summary(self):
        return self.calendar_study_name + ' on ' + str(self.start_time) + ' at ' + self.location

    def calendar_summary(self):
        return self.calendar_study_name + ' / ' + self.researcher.split()[0] + ' (' + self.participant + ')'

    def insert2calendar(self, service, google_calendar_id, color_id='1'):
        return service.events().insert(calendarId=google_calendar_id, body={
            'summary': self.calendar_summary(),
            'location': self.location,
            'description': self.id,
            'start': {
                'dateTime': self.start_time.isoformat()
            },
            'end': {
                'dateTime': self.end_time.isoformat()
            },
            'colorId': color_id
        }).execute()

    def match_keywords(self, keywords):
        # check if every word in the keyword string can be found in the event information
        for keyword in keywords.split():
            if keyword in self.sona_study_name or keyword in self.calendar_study_name or \
               keyword in self.participant or keyword in self.location or keyword in self.researcher:
                continue
            else:
                return False
        return True
