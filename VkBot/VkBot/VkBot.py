import vk_api
import json
import VkKeyboard
import Events
import asyncio
import UserStatus
from vk_api.longpoll import VkLongPoll, VkEventType

vk_session = vk_api.VkApi(token = "bc869b29041d5059d84fdb9bb230c55faafbfa6bfd210361a62e33d212dc7b0c90f393187a92f0f6a1803")
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
keyboard = VkKeyboard.Keyboard()
eventsList = Events.Events().getEvents()

controlKeyBoard = keyboard.getControlKeyBoard()
eventKeyBoard = keyboard.getEventsKeyBoard(eventsList)

userSessions = {}

def regInDb():
    return False;

def sender(id, text, keyboard):
    session_api.messages.send(user_id = id, message = text, random_id = 0, keyboard = keyboard)
 
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        msg = event.text.lower()
        id = event.user_id

        if(msg == "начать"):
            sender(id, "Выберите действие", controlKeyBoard)
        elif(msg == "назад"): 
            sender(id, "Выберите действие", controlKeyBoard)
        elif(msg == keyboard.get_regButtonText().lower()):
            sender(id, 'Выберите мероприятие', eventKeyBoard)
        elif(msg == keyboard.get_eventButtonText().lower()):
            sender(id, 'Мероприятий нет', controlKeyBoard)
        else:
            lowerCaseList = eventsList
            lowerCaseList = [eventName.lower() for eventName in lowerCaseList]
            print(msg)
            print(lowerCaseList)
            if msg in lowerCaseList: #если пользователь выбрал какое-то мероприятие
                userStatus = UserStatus.UserStatus()
                userStatus.currentEvent = msg
                userStatus.eventQuestions = Events.Events().getEventsQuestions(msg)
                userSessions[id] = userStatus
                question = userStatus.getCurrentQuestion()
                sender(id,question, None)
            else: #этапы регистрации пользователя на мероприятие
                userStatus = userSessions[id]
                if(userStatus.interviewEnded()):
                    regInDb();
                else:
                    question = userStatus.getCurrentQuestion()
                    sender(id,question, None)