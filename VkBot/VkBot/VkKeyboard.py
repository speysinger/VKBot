import vk_api
from vk_api.keyboard import VkKeyboard

class Keyboard:
    def __init__(self):
        self.controlKeyboard = VkKeyboard(one_time=False, inline=False)
        self.eventsKeyboard = VkKeyboard(one_time=False, inline=False)
        self.buttonsColor = "positive"
        self.serviceButtonsColor = 'negative'

    def getControlKeyBoard(self):
        self.registrationButtonText = "Регистрация на мероприятие"
        self.eventButtonText = "Мои мероприятия"

        self.controlKeyboard.add_button(self.registrationButtonText, 'primary')
        self.controlKeyboard.add_line()
        self.controlKeyboard.add_button(self.eventButtonText, 'primary')
        return self.controlKeyboard.get_keyboard()

    def getEventsKeyBoard(self, events):
        index = 0
        eventsLen = len(events)
        even = False

        if(eventsLen % 2 == 0):
            even = True

        for event in events:
            if(index != 0 and (index % 2 == 0 or (not even and index == eventsLen))):
                self.eventsKeyboard.add_line()

            self.eventsKeyboard.add_button(event, self.buttonsColor)

            index += 1
        self.addServiceButtons()
        return self.eventsKeyboard.get_keyboard()
    
    def addServiceButtons(self):
        self.eventsKeyboard.add_line()
        self.eventsKeyboard.add_button('исправить предыдущий шаг', self.serviceButtonsColor)
        self.eventsKeyboard.add_button('отмена регистрации', self.serviceButtonsColor)


    def get_regButtonText(self):
        return self.registrationButtonText

    def get_eventButtonText(self):
        return self.eventButtonText


