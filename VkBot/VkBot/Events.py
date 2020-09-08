import Question
import Event
class Events(object):
    def __init__(self):
        self.eventsList = {}

    def addEvent(self, eventName, eventDate, needConfirmation, questionsList, hintsList, regularsList):
        questionsArray = []
        for question, hint, regular in zip(questionsList, hintsList, regularsList):
            eventQuestion = Question.Question(question, regular, hint)
            questionsArray.append(eventQuestion)

        event = Event.Event(questionsArray, eventDate, needConfirmation)
        self.eventsList[eventName] = event

    def clearDictionaries(self):
        self.eventsList.clear()

    def getEventDate(self, eventName):
        return self.eventsList[eventName].getEventDate()

    def getEvents(self):
        return self.eventsList.keys()

    def getEvent(self, eventName):
        return self.eventsList[eventName]

    def getEventsQuestions(self, eventName):
        return self.eventsList[eventName].getQuestions()

                


