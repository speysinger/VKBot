import gspread
import Events
import time
from google.oauth2.service_account import Credentials

class GoogleSheet:

    def __init__(self):
        scopes = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive']

        creds = Credentials.from_service_account_file('creds.json', scopes = scopes)
        self.gc = gspread.authorize(creds)
 
        self.eventsSpreadSheet = self.gc.open('VkEvents')
        self.questionsSpreadSheet = self.gc.open('VkEventQuestions')

        self.eventsWorkSheets = {}
        self.events = Events.Events()

        self.createEventsTable()

    def getColValues(self, eventName):
        eventWorkSheet = self.eventsWorkSheets[eventName]
        col_count = eventWorkSheet.col_count
        return eventWorkSheet.col_values(col_count)
        
    def createEventsTable(self):
        self.events.clearDictionaries()
        workSheetsList = self.questionsSpreadSheet.worksheets()
        for workSheet in workSheetsList:

            workSheetTitle = workSheet.title
            questionsList = workSheet.col_values(1)
            hintsList = workSheet.col_values(2)
            regularsList = workSheet.col_values(3)
            needConfirmation = workSheet.cell(1,4).value.lower()
            eventDate = workSheet.cell(1,6).value

            agreement = questionsList[-1]
            del questionsList[-1]

            try:
                existedWorkSheet = self.eventsSpreadSheet.worksheet(workSheetTitle)
                self.eventsWorkSheets[workSheetTitle] = existedWorkSheet
            except Exception:
                if(needConfirmation == "с подтверждением"):
                    questionsList.append("Будет участвовать")
                else:
                    questionsList.append("Подтверждение не требуется")
                questionsList.append("Ссылка на Вконтакте")

                eventWorkSheet = self.eventsSpreadSheet.add_worksheet(title = workSheetTitle, rows = "500", cols = len(questionsList))
                eventWorkSheet.append_row(questionsList)
                self.eventsWorkSheets[workSheetTitle] = eventWorkSheet

            questionsList.insert(0, agreement)
            hintsList.insert(0, '')
            regularsList.insert(0, '')

            self.events.addEvent(workSheetTitle, eventDate, needConfirmation, questionsList, hintsList, regularsList)
    
    def userAlreadyRegistered(self, eventName, userLink):
        valuesInCol = self.getColValues(eventName)
        if userLink in valuesInCol:
            return True
        else:
            return False

    def getUserEvents(self, userLink):
        start = time.time()
        userEvents = []
        for workSheetTitle in self.eventsWorkSheets:
            valuesInCol = self.getColValues(workSheetTitle)
        
            if userLink in valuesInCol:
                eventStr = workSheetTitle + " - " + str(self.events.getEventDate(workSheetTitle))
                userEvents.append(eventStr)
            else:
                continue 
        end = time.time()
        print(end-start)
        return userEvents

    def insertAnswers(self, eventName, answers):
        eventWorkSheet = self.eventsWorkSheets[eventName]
        eventWorkSheet.append_row(answers)

    def getEventsUsersCount(self):
        eventsInfo = ""
        for workSheetTitle in self.eventsWorkSheets:
           eventWorkSheet = self.eventsWorkSheets[workSheetTitle]
           col_count = eventWorkSheet.col_count
           confirmedStatuses = eventWorkSheet.col_values(col_count - 1)
           confirmed = 0
           rejected = 0
           registeredUsers = 0

           for confirmStatus in confirmedStatuses:
               if(confirmStatus.lower() == "да"):
                   confirmed += 1
                   continue
               if(confirmStatus.lower() == "нет"):
                   rejected += 1
               registeredUsers += 1

           if(registeredUsers != 0):
               registeredUsers -= 1

           eventInfo = workSheetTitle + ": зарегистрировано - " + str(registeredUsers) + ", подтвердили участие - " + str(confirmed) + ", отказались от участия - " + str(rejected) + "\n"
           eventsInfo += eventInfo
        return eventsInfo

    def addUserConfirmationStatus(self, eventName, userLink, confirmationStatus):
        eventWorkSheet = self.eventsWorkSheets[eventName]
        userCell = eventWorkSheet.find(userLink)
        cellCol = userCell.col - 1
        cellRow = userCell.row
        eventWorkSheet.update_cell(cellRow, cellCol, confirmationStatus)

    def getUsersForMailing(self, event):
        onlyId = lambda x: x.partition("https://vk.com/id")[2]

        usersLinks = self.getColValues(event)

        if(len(usersLinks) > 0):
            usersLinks.pop(0)

        usersLinks = [*map(onlyId, usersLinks)]
        return usersLinks

    def getEventsList(self):
        return self.events.getEvents()

    def getEvent(self, eventName):
        return self.events.getEvent(eventName)

    def getEventQuestions(self, eventName):
        return self.events.getEventsQuestions(eventName)
