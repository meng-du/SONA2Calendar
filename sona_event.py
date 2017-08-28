

class SonaEvent:
    def __init__(self, sona_study_name, date, time, participant, location, researcher):
        self.sona_study_name = sona_study_name
        self.date_time = date + ' ' + time
        self.participant = participant
        self.location = location
        self.researcher = researcher
        self.calendar_study_name = self.sona_study_name

    def __str__(self):
        return self.calendar_study_name + \
               '\n\tSONA study name: ' + self.sona_study_name + \
               '\n\tTimeslot: ' + self.date_time + \
               '\n\tParticipant: ' + self.participant + \
               '\n\tLocation: ' + self.location + \
               '\n\tResearcher: ' + self.researcher

    def summary(self):
        return self.calendar_study_name + ' on ' + self.date_time + ' at ' + self.location

    def calendar_title(self):
        return self.calendar_study_name + ' / ' + self.researcher.split()[0] + ' (' + self.participant + ')'

    def match(self, keywords):
        # check if every word in the keyword string can be found in the event information
        for keyword in keywords.split():
            if keyword in self.sona_study_name or keyword in self.calendar_study_name or keyword in self.date_time or \
               keyword in self.participant or keyword in self.location or keyword in self.researcher:
                continue
            else:
                return False
        return True
