

class SonaEvent:
    def __init__(self, sona_study_name, date, time, participant, location, researcher):
        self.sona_study_name = sona_study_name
        self.date_time = date + ' ' + time
        self.participant = participant
        self.location = location
        self.researcher = researcher
        self.calendar_study_name = self.sona_study_name

    def summary(self):
        return self.calendar_study_name + ' on ' + self.date_time + ' at ' + self.location

    def calendar_title(self):
        return self.calendar_study_name + ' / ' + self.researcher.split()[0] + ' (' + self.participant + ')'

    def __str__(self):
        return self.calendar_study_name + \
               '\n\tSONA study name: ' + self.sona_study_name + \
               '\n\tTimeslot: ' + self.date_time + \
               '\n\tParticipant: ' + self.participant + \
               '\n\tLocation: ' + self.location + \
               '\n\tResearcher: ' + self.researcher
