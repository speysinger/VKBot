import gspread
import Events
import asyncio
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
 
        self.eventsSpreadSheet = self.gc.open('VkEvents') #exception mozet bitb
        self.questionsSpreadSheet = self.gc.open('VkEventQuestions') #exception mozet bitb

        self.eventsWorkSheets = {}
        self.events = Events.Events()

        self.createEventsTable()

        workSheetsList = self.questionsSpreadSheet.worksheets() #список всех листов в таблице с вопросами
        for workSheet in workSheetsList:
            workSheetTitle = workSheet.title
            eventWorkSheet = self.eventsSpreadSheet.worksheet(workSheetTitle)
            self.eventsWorkSheets[workSheetTitle] = eventWorkSheet


        #убедиться в наличии файла vkEvents
    def createEventsTable(self):

        self.events.clearDictionaries()
        workSheetsList = self.questionsSpreadSheet.worksheets()
        for workSheet in workSheetsList:

            workSheetTitle = workSheet.title
            questionsList = workSheet.col_values(1)
            hintsList = workSheet.col_values(2)
            regularsList = workSheet.col_values(3)
            eventDate = workSheet.cell(1,6).value

            self.events.addEventDate(workSheetTitle, eventDate)
            try:
                existedWorkSheet = self.eventsSpreadSheet.worksheet(workSheetTitle) #существует ли данный ивент в таблице ответов на вопросы
            except Exception:
                eventWorkSheet = self.eventsSpreadSheet.add_worksheet(title = workSheetTitle, rows = "500", cols = len(questionsList))
                questionsList.append("Ссылка на Вконтакте")
                eventWorkSheet.append_row(questionsList)

            self.events.addEvent(workSheetTitle, questionsList, hintsList, regularsList)
        self.events.addServiceButtons()
    
    def userAlreadyRegistered(self, event, userLink):
        eventWorkSheet = self.eventsWorkSheets[event]
        col_count = eventWorkSheet.col_count
        valuesInCol = eventWorkSheet.col_values(col_count)
        if userLink in valuesInCol:
            return True
        else:
            return False

    def getUserEvents(self, userLink):
        start = time.time()
        userEvents = []
        for workSheetTitle in self.eventsWorkSheets:

            eventWorkSheet = self.eventsWorkSheets[workSheetTitle]
            col_count = eventWorkSheet.col_count
            valuesInCol = eventWorkSheet.col_values(col_count)
        
            if userLink in valuesInCol:
                eventStr = workSheetTitle + " - " + str(self.events.getEventDate(workSheetTitle))
                userEvents.append(eventStr)
            else:
                continue 
        end = time.time()
        print(end-start)
        return userEvents

    def insertAnswers(self, event, answers):
        eventWorkSheet = self.eventsWorkSheets[event]
        eventWorkSheet.append_row(answers)


    def getEventsList(self):
        return self.events.getEvents()

    def getEventQuestions(self, eventName):
        return self.events.getEventsQuestions(eventName)
