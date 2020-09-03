import vk_api
import json
import VkKeyboard
import Events
import asyncio
import re
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

#regDictionary = {
#            'email': '.+@.+\..+',
 #           'телефон': '\d{11}',
 #           '': '^[а-яА-ЯёЁ\s]*$' #всегда должно быть последним в словаре регулярных выражений
 #           }

def validateMessage(pattren, msg):
    for key in regDictionary:
        if(re.search(key, question) != None):
            regular = re.compile(regDictionary[key])
            status = regular.match(msg)
            if(status == None):
                return False;
            else:
                return True;
    return True;

def sender(id, text, keyboard):
    session_api.messages.send(user_id = id, message = text, random_id = 0, keyboard = keyboard)
 
#класс. для каждого вопроса добавить экземпляр класса(вопрос, регулярка, пример ответа)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        originalMessage = event.text
        msg = originalMessage.lower()
        id = event.user_id

        if(msg == "начать"):
            sender(id, "Выберите действие", controlKeyBoard)
        elif(msg == "назад"):
            userSessions.pop(id, None)
            sender(id, "Выберите действие", controlKeyBoard)
        elif(msg == 'исправить предыдущий шаг'):
            userStatus = userSessions[id]
            previousAnswer = userStatus.fixPreviousStep()
            sender(id, "Ваш предыдущий ответ:" + previousAnswer + "\nВведите ответ:", None)
            userSessions[id] = userStatus
        elif(msg == keyboard.get_regButtonText().lower()):
            sender(id, 'Выберите мероприятие', eventKeyBoard)
        elif(msg == keyboard.get_eventButtonText().lower()):
            sender(id, 'Мероприятий нет', controlKeyBoard)
        else:
            if msg in eventsList: #если пользователь выбрал какое-то мероприятие
                userStatus = UserStatus.UserStatus()
                userStatus.currentEvent = msg
                userStatus.eventQuestions = Events.Events().getEventsQuestions(msg)

                userSessions[id] = userStatus
                question = userStatus.getCurrentQuestion().getQuestionText()
                sender(id,question, None)
            elif(id in userSessions):#этапы регистрации пользователя на мероприятие
                userStatus = userSessions[id]

                question = userStatus.getCurrentQuestion()
                questionText = question.getQuestionText()
                pattern = question.getRegular()

                answerValidated = validateMessage(pattern, msg)

                if(not answerValidated): 
                    sender(id, "Некорретный формат сообщения", None)
                    continue
            
                if(userStatus.interviewEnded()):
                    userStatus.addAnswer(msg)
                    print(userStatus)
                    sender(id, "KONEC", controlKeyBoard)
                    userSessions.pop(id, None)
                    regInDb();
                else:
                    userStatus.changeRegistrationStep()
                    question = userStatus.getCurrentQuestion()
                    userStatus.addAnswer(msg)
                    userSessions[id] = userStatus
                    sender(id,question, None)
            else:
                sender(id, "Я не понял", controlKeyBoard)