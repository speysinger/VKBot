import vk_api
from vk_api.keyboard import VkKeyboard

class Keyboard:
    def __init__(self):
        self.controlKeyboard = VkKeyboard(one_time=False, inline=False)
        self.eventsKeyboard = VkKeyboard(one_time=False, inline=False)
        self.yesKeyBoard = VkKeyboard(one_time = False, inline = False)
        self.confirmationKeyboard = VkKeyboard(one_time = False, inline = False)
        self.buttonsColor = "positive"
        self.serviceButtonsColor = 'negative'

    def getConfirmationKeyboard(self):
        self.confirmationKeyboard.add_button("Да", self.buttonsColor)
        self.confirmationKeyboard.add_button("Нет", self.buttonsColor)
        return self.confirmationKeyboard.get_keyboard()

    def getYesKeyBoard(self):
        self.yesKeyBoard.add_button("Да", self.buttonsColor)
        self.yesKeyBoard.add_button('Назад', self.serviceButtonsColor)
        return self.yesKeyBoard.get_keyboard()

    def getControlKeyBoard(self):
        self.registrationButtonText = "Регистрация на мероприятие"
        self.eventButtonText = "Мои мероприятия"

        self.controlKeyboard.add_button(self.registrationButtonText, 'primary')
        self.controlKeyboard.add_line()
        self.controlKeyboard.add_button(self.eventButtonText, 'primary')
        return self.controlKeyboard.get_keyboard()

    def getEventsKeyBoard(self, events):
        self.eventsKeyboard = VkKeyboard(one_time=False, inline=False)
        index = 0
        eventsLen = len(events)
        even = True if eventsLen % 2 == 0 else False

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
        self.eventsKeyboard.add_button('Назад', self.serviceButtonsColor)

    def get_regButtonText(self):
        return self.registrationButtonText

    def get_eventButtonText(self):
        return self.eventButtonText


