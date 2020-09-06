import Question
class Events(object):
    def __init__(self):
        self.eventsList = {}
        self.eventsDate = {}

    def addEvent(self, event, questionsList, hintsList, regularsList):
        questionsArray = []
        for question, hint, regular in zip(questionsList, hintsList, regularsList):
            eventQuestion = Question.Question(question, regular, hint)
            questionsArray.append(eventQuestion)
        self.eventsList[event] = questionsArray

    def addEventDate(self, event, date):
        self.eventsDate[event] = date

    def clearDictionaries(self):
        self.eventsList.clear()
        self.eventsDate.clear()

    def getEventDate(self, event):
        return self.eventsDate[event]

    def addServiceButtons(self):
        self.eventsList['исправить предыдущий шаг'] = []
        self.eventsList['отмена регистрации'] = []

    def getEvents(self):
        return self.eventsList.keys()

    def getEventsQuestions(self, eventName):
        return self.eventsList[eventName]

                


