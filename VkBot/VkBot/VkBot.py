import vk_api
import json
import VkKeyboard
import re
from datetime import timedelta, datetime
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool
import threading
import UserStatus
import GoogleSheet
import Event
from vk_api.longpoll import VkLongPoll, VkEventType

class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token = "9f9519feae9237afa656cde8dec06d42276b3edc91ff44c8dfe5f5a328b7befac46618f71562abc460a7d")
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
        self.yesKeyBoard = self.keyboard.getYesKeyBoard()

        #adminPart
        self.testPassword = "zdarova2"
        self.clearAdminValues()
        self.adminActions = {
            'начать рассылку': self.confirmationBeforeMailing,
            'разослать запрос на подтверждение': self.startConfirmationMailing,
            'сменить текст рассылки': self.setMailing,
            'просмотреть количество зарегистрированных участников': self.showRegisteredUsers
            }
        #adminPart

        self.userSessions = {}
        self.confirmationList = {}

        self.threadPool = ThreadPool(20)

        nightTime = self.getNightDatetime()
        self.inactiveUserDeleter = threading.Timer(self.getSecondsToDate(nightTime), self.deleteInactiveUsers)
        self.inactiveUserDeleter.start()

    def clearAdminValues(self):
        self.adminId = -1
        self.mailingEvent = ""
        self.mailingText = ""

    def getNightDatetime(self):
        now = datetime.now()
        nextUpdateTime = (now + timedelta(days = 1)).replace(minute = 0, hour = 4)
        return nextUpdateTime

    def updateEventsList(self):
        self.googleSheet.createEventsTable()
        self.eventsList = self.googleSheet.getEventsList()
        self.eventKeyBoard = self.keyboard.getEventsKeyBoard(self.eventsList)
        self.sender(id, "Выполнил", None)

    def preStartMailing(self):
        mailingUsers = self.googleSheet.getUsersForMailing(self.mailingEvent)
        self.threadPool.apply_async(self.startMailing, args = (mailingUsers, ))

    def startConfirmationMailing(self, **params):
        eventName = params['eventName']
        confirmationText = params['confirmationText']
        usersForConfirmationMailing = self.googleSheet.getUsersForMailing(eventName)

        self.threadPool.apply_async(self.startConfirmation, args = (usersForConfirmationMailing, confirmationText,))

    def startConfirmation(self, usersForConfirmationMailing, mailingText):
        for userId in usersForConfirmationMailing:
            self.sender(userId, mailingText, None)
            self.confirmationList[int(userId)] = eventName

    def startMailing(self, usersId):
        for userId in usersId:
            self.sender(userId, self.mailingText, None)
        self.clearAdminValues()

    def setMailing(self, **params):
        textMailing = params['textMailing']
        self.mailingText = textMailing


    def confirmationBeforeMailing(self, **paramsadminId):
        adminId = paramsadminId['adminId']
        self.sender(adminId, "Подтвердите начало рассылки уведомления:\n" + self.mailingText + "\n участникам мероприятия: " + self.mailingEvent
                               + "\n отправив в ответ да/нет", None)
        self.adminId = adminId

    def showRegisteredUsers(self, **paramsadminId):
        adminId = params['adminId']
        info = self.googleSheet.getEventsUsersCount()
        self.sender(adminId, info, None)

    def getSecondsToDate(self, eventConfirmationTime):
        now = datetime.now()
        delta = eventConfirmationTime - now
        return float(delta.total_seconds())

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

        for k, v in list(self.confirmationList.items()):
            if value not in self.eventsList:
                del self.confirmationList[k]

        nextUpdateTime = self.getNightDatetime()
        t = threading.Timer(self.getSecondsToDate(nextUpdateTime), self.deleteInactiveUsers)
        t.start()

    def validateAdminCommand(self, adminId, adminCommand):
        words = adminCommand.split('\n')
        if(len(words) < 4):
            self.sender(adminId, "Сообщение не удовлетворяет формату", None)
            return 0

        password = words[0].rstrip()
        if(password != self.testPassword):
            self.sender(adminId, "Неверный пароль", None)
            return 0

        try:
            eventName = words[1].rstrip().lower()
            trueEventName = next(filter(lambda x: x.lower() == eventName, self.eventsList))
        except Exception:
            self.sender(adminId, "Мероприятие не найдено", None)
            return 0

        action = words[2].rstrip().lower()
        if action not in self.adminActions:
            self.sender(adminId, "Действие не найдено", None)
            return 0

        del words[0:3]

        mailingText = '\n'.join(words)

        if(action != "просмотреть количество зарегистрированных участников"):
            self.mailingEvent = trueEventName
            self.mailingText = mailingText

        self.adminActions[action](adminId = adminId, eventName = trueEventName, confirmationText = mailingText, textMailing = mailingText)
        return 0

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
        self.sender(id, question, self.yesKeyBoard)

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

                elif(msg == "назад"):
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
                    self.threadPool.apply_async(self.showUserEvents, args = (id, ))

                elif(originalMessage == "SECRET_MESSAGE_TO_UPDATE_EVENT_LIST"):
                    self.threadPool.apply_async(self.updateEventsList, args = ())
                    
                elif(self.testPassword in msg):
                    self.validateAdminCommand(id, originalMessage)

                elif((id in self.confirmationList) and (msg == "да" or msg == "нет")):
                    eventName = self.confirmationList[id]
                    self.threadPool.apply_async(self.googleSheet.addUserConfirmationStatus, args = (eventName, self.makeVkLink(id), msg ))
                    del self.confirmationList[id]
                    self.sender(id, "Ответ внесён", None)

                elif(id == self.adminId and (msg == "да" or msg == "нет")):
                    if(msg == "нет"):
                        self.sender(id, "Отказ от начала рассылки принят", self.controlKeyBoard)
                        self.clearAdminValues()
                    elif(msg == "да" and len(self.mailingText) != 0 and self.adminId != 0):
                        self.preStartMailing()
                    else:
                        self.sender(id, "Я не понял", self.controlKeyBoard)


                else:
                    if originalMessage in self.eventsList: #если пользователь выбрал какое-то мероприятие
                        self.threadPool.apply_async(self.registerUser, args = (id, originalMessage, ))

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
            
      
                        if(userStatus.lastQuestion()):
                            userStatus.addAnswer(originalMessage)

                            answers = userStatus.getAnswers()
                            answers.append('ответа нет')
                            answers.append(self.makeVkLink(id))
                            self.threadPool.apply_async(self.googleSheet.insertAnswers, args = (userStatus.getCurrentEvent(), answers,))

                            self.sender(id, "Регистрация закончена.\nВы зарегистрированы на: " + userStatus.currentEvent , self.controlKeyBoard)
                            self.userSessions.pop(id, None)
                        else:
                            if(userStatus.firstQuestion()):
                                if(msg != 'да'):
                                    self.sender(id, "Для продолжения нажмите \"Да\"", None)
                                    continue                        

                            if(userStatus.firstQuestion()):
                                userStatus.changeRegistrationStep()
                                questionText = userStatus.getCurrentQuestion().getQuestionText()
                                self.sender(id, questionText, self.eventKeyBoard)
                            else:
                                userStatus.changeRegistrationStep()
                                userStatus.addAnswer(originalMessage)
                                questionText = userStatus.getCurrentQuestion().getQuestionText()
                                self.userSessions[id] = userStatus
                                self.sender(id, questionText, None)
                    else:
                        self.sender(id, "Я не понял", self.controlKeyBoard)