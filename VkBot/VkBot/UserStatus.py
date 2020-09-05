class UserStatus:
    def __init__(self):
        self.currentEvent = ""
        self.eventQuestions = []
        self.userAnswers = []
        self.currentEventRegisrationStep = 0

    def addAnswer(self, answer):
        self.userAnswers.append(answer)

    def changeRegistrationStep(self):
        self.currentEventRegisrationStep += 1

    def fixPreviousStep(self):
        if(self.currentEventRegisrationStep > 0):
            self.currentEventRegisrationStep -= 1
            return self.userAnswers.pop()
        return ""

    def getAnswers(self):
        return self.userAnswers

    def getCurrentEvent(self):
        return self.currentEvent

    def getCurrentQuestion(self):
        return self.eventQuestions[self.currentEventRegisrationStep]

    def interviewEnded(self):
        if(self.currentEventRegisrationStep + 1 == len(self.eventQuestions)):
            return True;
        return False;


