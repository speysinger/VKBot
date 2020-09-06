import vk_api
import json
import VkKeyboard
import re
from datetime import datetime
from threading import Thread
import threading
import UserStatus
import GoogleSheet
from vk_api.longpoll import VkLongPoll, VkEventType

class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token = "bc869b29041d5059d84fdb9bb230c55faafbfa6bfd210361a62e33d212dc7b0c90f393187a92f0f6a1803")
        self.session_api = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

        try:
            self.googleSheet = GoogleSheet.GoogleSheet()
        except Exception as e:
            sender(idKogo-to, "Что-то не вышло с гугл файлами, вот текст исключения: " + str(e))

        self.keyboard = VkKeyboard.Keyboard()
        self.eventsList = self.googleSheet.getEventsList()

        self.controlKeyBoard = self.keyboard.getControlKeyBoard()
        self.eventKeyBoard = self.keyboard.getEventsKeyBoard(self.eventsList)

        self.secondsInDays = 86400

        self.userSessions = {}
        self.inactiveUserDeleter = threading.Timer(self.secondsInDays, self.deleteInactiveUsers)
        self.inactiveUserDeleter.start()

    def getCurrentDatetime(self):
        return datetime.now().__format__("%d/%m/%y %H:%M")

    def deleteInactiveUsers(self):
        nowStr = self.getCurrentDatetime()
        nowDatetime = datetime.strptime(nowStr, "%d/%m/%y %H:%M")

        for k, v in list(self.userSessions.items()):
            regDate = datetime.strptime(v.regDate, "%d/%m/%y %H:%M")
            delta = nowDatetime - regDate
            if(delta.seconds >= self.secondsInDays):
                del self.userSessions[k]

        self.t = threading.Timer(self.secondsInDays, self.deleteInactiveUsers)
        self.t.start()

    def makeVkLink(self, id):
        return "https://vk.com/id" + str(id)

    def showUserEvents(self, id):
        userEvents = self.googleSheet.getUserEvents(self.makeVkLink(id))
        if(len(userEvents) != 0):
            self.sender(id, "Ваши мероприятия:\n" + '\n'.join(userEvents), None)
        else:
            self.sender(id, 'Вы не зарегистрированы ни на одно мероприятие', self.controlKeyBoard)

    def registerUser(self, id, msg):
        registered = self.googleSheet.userAlreadyRegistered(msg, self.makeVkLink(id))
        if(registered):
            self.sender(id, "Вы уже зарегистрированы на это мероприятие", None)
            return

        userStatus = UserStatus.UserStatus()
        userStatus.regDate = self.getCurrentDatetime()
        userStatus.currentEvent = msg
        userStatus.eventQuestions = self.googleSheet.getEventQuestions(msg)

        self.userSessions[id] = userStatus
        question = userStatus.getCurrentQuestion().getQuestionText()
        self.sender(id, question, None)

    def validateMessage(self, pattern, msg):
        regular = re.compile(pattern)
        status = regular.match(msg)
        if(status == None):
            return False
        else:
            return True
        return False

    def sender(self, id, text, keyboard):
        self.session_api.messages.send(user_id = id, message = text, random_id = 0, keyboard = keyboard)

    def startBot(self):
        for event in self.longpoll.listen():
            print(threading.active_count())
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                originalMessage = event.text
                msg = originalMessage.lower()
                id = event.user_id
                if(msg == "начать"):
                    self.sender(id, "Выберите действие", self.controlKeyBoard)

                elif(msg == "отмена регистрации"):
                    self.userSessions.pop(id, None)
                    self.sender(id, "Выберите действие", self.controlKeyBoard)

                elif(msg == 'исправить предыдущий шаг'):
                    if id in self.userSessions:
                        userStatus = self.userSessions[id]
                    else:
                        self.sender(id, "Процесс регистрации не был начат", None)
                        continue
                    previousAnswer = userStatus.fixPreviousStep()
                    previousQuestion = userStatus.getCurrentQuestion().getQuestionText()

                    self.sender(id, "Ваш предыдущий вопрос: " + previousQuestion + "\nВаш предыдущий ответ: " + previousAnswer + "\nВведите ответ: ", None)
                    uself.serSessions[id] = userStatus

                elif(msg == self.keyboard.get_regButtonText().lower()):
                    self.sender(id, 'Выберите мероприятие', self.eventKeyBoard)

                elif(msg == self.keyboard.get_eventButtonText().lower()):
                    userEventsThread = Thread(target = self.showUserEvents, args = (id, ))
                    userEventsThread.start()

                elif(originalMessage == "SECRET_MESSAGE_TO_UPDATE_EVENT_LIST"):
                    self.googleSheet.createEventsTable()
                    self.sender(id, "Выполнил", None)
                else:
                    if msg in self.eventsList: #если пользователь выбрал какое-то мероприятие
                        userRegisterThread = Thread(target = self.registerUser, args = (id, msg, ))
                        userRegisterThread.start()
                    elif(id in self.userSessions):#этапы регистрации пользователя на мероприятие
                        userStatus = self.userSessions[id]
                        userStatus.regDate = getCurrentDatetime()

                        question = userStatus.getCurrentQuestion()
                        questionText = question.getQuestionText()
                        questionHint = question.getHint()
                        pattern = question.getRegular()

                        answerValidated = self.validateMessage(pattern, msg)

                        if(not answerValidated): 
                            self.sender(id, "Некорретный формат сообщения\n" + "Пример ответа: " + questionHint, None)
                            continue
            
                        if(userStatus.interviewEnded()):
                            userStatus.addAnswer(originalMessage)

                            answers = userStatus.getAnswers()
                            answers.append(self.makeVkLink(id))

                            thread = Thread(target = self.googleSheet.insertAnswers, args = (userStatus.getCurrentEvent(), answers,))
                            thread.start()

                            self.sender(id, "Регистрация окончена.\nВы зарегистрированы на: " + userStatus.currentEvent , self.controlKeyBoard)
                            self.userSessions.pop(id, None)
                        else:
                            userStatus.changeRegistrationStep()
                            questionText = userStatus.getCurrentQuestion().getQuestionText()
                            userStatus.addAnswer(originalMessage)

                            self.userSessions[id] = userStatus
                            self.sender(id,questionText, None)
                    else:
                        self.sender(id, "Я не понял", self.controlKeyBoard)
