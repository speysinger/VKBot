import vk_api
from vk_api.keyboard import VkKeyboard

class Keyboard:
    def __init__(self):
        self.controlKeyboard = VkKeyboard(one_time=False, inline=False)
        self.eventsKeyboard = VkKeyboard(one_time=False, inline=False)
        self.buttonsColor = "positive"

    def getControlKeyBoard(self):
        self.registrationButtonText = "Регистрация на мероприятие"
        self.eventButtonText = "Мои мероприятия"

        self.controlKeyboard.add_button(self.registrationButtonText, self.buttonsColor)
        self.controlKeyboard.add_line()
        self.controlKeyboard.add_button(self.eventButtonText, self.buttonsColor)
        return self.controlKeyboard.get_keyboard()

    def getEventsKeyBoard(self, events):#костыль со строками под кнопками
        first = True
        for event in events:
            if(not first):
                self.eventsKeyboard.add_line()
            self.eventsKeyboard.add_button(event, self.buttonsColor)
            if(first):
                first = False
        return self.eventsKeyboard.get_keyboard()
    
    def get_regButtonText(self):
        return self.registrationButtonText

    def get_eventButtonText(self):
        return self.eventButtonText


