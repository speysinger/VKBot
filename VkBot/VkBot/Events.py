import Question
import Event
class Events(object):
    def __init__(self):
        self.eventsList = {}
        self.regularExpressions = {
            'телефон': '\d{11}',
            'почта' : '.+@.+\..+',
            'число': '[0-9]',
            'фио': '(?:[А-Яа-я]+ ){2}[А-Яа-я]+',
            'строка': '^[а-яА-ЯёЁ\s]*$',
            'любое': ''
        }

    def addEvent(self, eventName, eventDate, needConfirmation, questionsList, hintsList, regularsList):
        questionsArray = []
        for question, hint, regular in zip(questionsList, hintsList, regularsList):
            recognisedRegExp = self.regularExpressions.setdefault(regular, '')
            eventQuestion = Question.Question(question, recognisedRegExp, hint)
            questionsArray.append(eventQuestion)

        event = Event.Event(questionsArray, eventDate, needConfirmation)
        self.eventsList[eventName] = event

    def clearDictionaries(self):
        self.eventsList.clear()

    def getEventDate(self, eventName):
        return self.eventsList[eventName].getEventDate()

    def getEvents(self):
        return [*self.eventsList]

    def getEvent(self, eventName):
        return self.eventsList[eventName]

    def getEventsQuestions(self, eventName):
        return self.eventsList[eventName].getQuestions()

                


