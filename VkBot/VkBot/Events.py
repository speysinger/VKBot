class Events(object):
    def __init__(self):
        self.eventsList = {
            'Мероприятие1' : ['Ваше ФИО', 'Ваш номер телефона'],
            'Мероприятие2' : ['ФИО всех членов команды', 'Номера телефонов всех членов команды', 'Название команды'],
            'Назад': []
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
                


