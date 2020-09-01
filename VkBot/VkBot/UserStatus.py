class UserStatus:
    def __init__(self):
        self.currentEvent = ""
        self.eventQuestions = []
        self.currentEventRegisrationStep = 0

    def changeRegistrationStep(self):
        self.currentEventRegisrationStep += 1

    def getCurrentQuestion(self):
        return self.eventQuestions[self.currentEventRegisrationStep]

    def interviewEnded(self):
        if(self.currentEventRegisrationStep + 1 == len(self.eventQuestions)):
            return True;
        return False;


