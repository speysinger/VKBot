import Question
class Event(object):
    def __init__(self, questions, eventDate, needConfirmation):
        self.questions = questions
        self.eventDate = eventDate
        self.needConfirmation = needConfirmation.lower()

    def getEventDate(self):
        return self.eventDate
    def getQuestions(self):
        return self.questions
    def getConfirmation(self):
        return self.needConfirmation
        


