import Question
class Events(object):
    def __init__(self):
        self.eventsList = {
            'мероприятие1' : [Question.Question('Ваше ФИО', '^[а-яА-ЯёЁ\s]*$', 'Иванов Иван Иванович'),
                             Question.Question('Ваш номер телефона', '\d{11}', '89506534857')],
            'мероприятие2' : [Question.Question('ФИО всех членов команды', '^[а-яА-ЯёЁ\s]*$', 'Иванов Иван Иванович, Степанов Степан Степанович ...'),
                             Question.Question('Номер телефона ответственного', '\d{11}', '89506534857'), 
                             Question.Question('Название команды', '^[а-яА-ЯёЁ\s]*$', 'Крутые бобры')],
            'исправить предыдущий шаг': [],
            'назад': []
            }

    def getEvents(self):
        return self.eventsList.keys()

    def getEventsQuestions(self, eventName):
        return self.eventsList[eventName]

    def recogniseEvent(self, eventName):
        for x in self.eventsList:
            if(self.eventsList[text]):
                return self.eventsList[text]
        return None;
                


