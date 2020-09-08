import vk_api
import json
import VkKeyboard
import re
from datetime import timedelta, datetime
from threading import Thread
import threading
import UserStatus
import GoogleSheet
import Event
from vk_api.longpoll import VkLongPoll, VkEventType

class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token = "bc869b29041d5059d84fdb9bb230c55faafbfa6bfd210361a62e33d212dc7b0c90f393187a92f0f6a1803")
        self.session_api = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

        try:
            self.googleSheet = GoogleSheet.GoogleSheet()
        except Exception as e:
            self.sender(200552768, "Что-то не вышло с гугл файлами, вот текст исключения: " + str(e) + "\nЯ, кстати, упал", None)

        self.keyboard = VkKeyboard.Keyboard()
        self.eventsList = self.googleSheet.getEventsList()

        self.controlKeyBoard = self.keyboard.getControlKeyBoard()
        self.eventKeyBoard = self.keyboard.getEventsKeyBoard(self.eventsList)

        #adminPart
        self.testPassword = "zdarova2"
        self.adminId = -1
        self.mailingEvent = ""
        self.mailingText = ""
        self.adminActions = {
            'установить текст рассылки': self.setMailing,
            'сменить текст рассылки': self.setMailing,
            'просмотреть количество зарегистрированных участников': self.showRegisteredUsers
            }
        #adminPart

        self.userSessions = {}
        self.confirmationList = {}

        nightTime = self.getNightDatetime()
        self.createConfirmationMailing()
        self.inactiveUserDeleter = threading.Timer(self.getSecondsToDate(nightTime), self.deleteInactiveUsers)
        self.inactiveUserDeleter.start()

    def createConfirmationMailing(self):
        eventsList = self.googleSheet.getEventsList()

        for eventName in eventsList:
            event = self.googleSheet.getEvent(eventName)
            eventConfirmation = event.getConfirmation()

            if(eventConfirmation == 'с подтверждением'):
                eventDate = event.getEventDate()
                eventDatetime = datetime.strptime(eventDate, '%d/%m/%y %H:%M')
                beforeEventDateTime = (eventDatetime - timedelta(days = 1)).replace(minute = 0, hour = 9)
                secondsToEventConfirmation = self.getSecondsToDate(beforeEventDateTime)

                if(secondsToEventConfirmation <= 0):
                    secondsToEventConfirmation = 0

                threading.Timer(secondsToEventConfirmation, self.startEventMailing, [eventName]).start()
                

    def getNightDatetime(self):
        now = datetime.now()
        nextUpdateTime = (now + timedelta(days = 1)).replace(minute = 0, hour = 4)
        return nextUpdateTime

    def startEventMailing(self, eventName):
        usersForConfirmationMailing = self.googleSheet.getUsersForMailing(eventName)
        Thread(target = self.startConfirmation, args = (usersForConfirmationMailing, eventName,)).start()

    def startConfirmation(self, usersForConfirmationMailing, eventName):
        for userId in usersForConfirmationMailing:
            self.sender(userId, "Подвердите участие на мероприятии: " + eventName + "\n Отправив в ответ да/нет", None)
            self.confirmationList[int(userId)] = eventName

    def startMailing(self, usersId):
        for userId in usersId:
            self.sender(userId, self.mailingText, None)

    def setMailing(self, adminId, textMailing):
        self.mailingText = textMailing

    def showRegisteredUsers(self, adminId, uselessParam):
        info = self.googleSheet.getEventsUsersCount()
        sender(adminId, info, None)

    def getSecondsToDate(self, eventConfirmationTime):
        now = datetime.now()
        delta = eventConfirmationTime - now
        return delta.total_seconds()

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

        nextUpdateTime = self.getNightDatetime()
        t = threading.Timer(self.getSecondsToDate(nextUpdateTime), self.deleteInactiveUsers)
        t.start()

    def validateAdminCommand(self, adminId, adminCommand):
        words = adminCommand.split('\n')
        if(len(words) < 4):
            self.sender(adminId, "Сообщение не удовлетворяет формату", None)
            return False

        password = words[0].rstrip()
        if(password != self.testPassword):
            self.sender(adminId, "Неверный пароль", None)
            return False

        eventName = words[1].rstrip().lower()
        if(eventName not in self.eventsList):
            self.sender(adminId, "Мероприятие не найдено", None)
            return False

        action = words[2].rstrip().lower()
        if action not in self.adminActions:
            self.sender(adminId, "Действие не найдено", None)
            return False

        del words[0:3]

        mailingText = '\n'.join(words)
        self.adminActions[action](adminId, mailingText)
        self.mailingEvent = eventName
        self.adminId = adminId
        return True

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
                    self.userSessions[id] = userStatus

                elif(msg == self.keyboard.get_regButtonText().lower()):
                    self.sender(id, 'Выберите мероприятие', self.eventKeyBoard)

                elif(msg == self.keyboard.get_eventButtonText().lower()):
                    userEventsThread = Thread(target = self.showUserEvents, args = (id, ))
                    userEventsThread.start()

                elif(originalMessage == "SECRET_MESSAGE_TO_UPDATE_EVENT_LIST"):
                    updateEventsThread = Thread(target = self.googleSheet.createEventsTable, args = ())
                    updateEventsThread.start()
                    self.sender(id, "Выполнил", None)
 
                elif(self.testPassword in msg):
                    validated = self.validateAdminCommand(id, originalMessage)
                    if(validated):
                        self.sender(id, "Подтвердите начало рассылки уведомления:\n" + self.mailingText + "\n участникам мероприятия: " + self.mailingEvent
                               + "\n отправив в ответ да/нет", None)

                elif((id in self.confirmationList) and (msg == "да" or msg == "нет")):
                    eventName = self.confirmationList[id]
                    confirmationThread = Thread(target = self.googleSheet.addUserConfirmationStatus, args = (eventName, self.makeVkLink(id), msg ))
                    confirmationThread.start()
                    del self.confirmationList[id]
                    self.sender(id, "Ответ внесён", None)

                elif(id == self.adminId and (msg == "да" or msg == "нет")):
                    if(len(self.mailingText) != 0 and self.adminId != 0):
                        mailingUsers = self.googleSheet.getUsersForMailing(self.mailingEvent)
                        mailingThread = Thread(target = self.startMailing, args = (mailingUsers, ))
                        mailingThread.start()

                        self.adminId = -1
                        self.mailingEvent = ""
                    else:
                        self.sender(id, "Я не понял", self.controlKeyBoard)


                else:
                    if msg in self.eventsList: #если пользователь выбрал какое-то мероприятие
                        userRegisterThread = Thread(target = self.registerUser, args = (id, msg, ))
                        userRegisterThread.start()

                    elif(id in self.userSessions):#этапы регистрации пользователя на мероприятие
                        userStatus = self.userSessions[id]
                        userStatus.regDate = self.getCurrentDatetime()

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
                            answers.append('-')
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
                            self.sender(id, questionText, None)
                    else:
                        self.sender(id, "Я не понял", self.controlKeyBoard)
