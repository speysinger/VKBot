from datetime import datetime
class UserStatus:
    def __init__(self):
        self.currentEvent = ""
        self.eventQuestions = []
        self.userAnswers = []
        self.currentEventRegisrationStep = 0
        self.regDate = datetime

    def addAnswer(self, answer):
        self.userAnswers.append(answer)

    def changeRegistrationStep(self):
        self.currentEventRegisrationStep += 1

    def fixPreviousStep(self):
        if(self.currentEventRegisrationStep > 0 and len(self.userAnswers)):
            self.currentEventRegisrationStep -= 1
            return self.userAnswers.pop()
        return ""

    def getAnswers(self):
        return self.userAnswers

    def getCurrentEvent(self):
        return self.currentEvent

    def getCurrentQuestion(self):
        return self.eventQuestions[self.currentEventRegisrationStep]

    def firstQuestion(self):
        if(self.currentEventRegisrationStep == 0):
            return True;
        return False;

    def lastQuestion(self):
        if(self.currentEventRegisrationStep + 1 == len(self.eventQuestions)):
            return True;
        return False;


