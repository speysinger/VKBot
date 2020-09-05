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

        self.eventsWorkSheets = []

        workSheetsList = self.questionsSpreadSheet.worksheets() #список всех листов в таблице с вопросами
        for workSheet in workSheetsList:
            workSheetTitle = workSheet.title
            eventWorkSheet = self.eventsSpreadSheet.worksheet(workSheetTitle)
            self.eventsWorkSheets.append(eventWorkSheet)

        self.events = Events.Events()


        #убедиться в наличии файла vkEvents
    def createEventsTable(self):
        workSheetsList = self.questionsSpreadSheet.worksheets()
        for workSheet in workSheetsList:

            workSheetTitle = workSheet.title
            questionsList = workSheet.col_values(1)
            hintsList = workSheet.col_values(2)
            regularsList = workSheet.col_values(3)

            try:
                existedWorkSheet = self.eventsSpreadSheet.worksheet(workSheetTitle) #существует ли данный ивент в таблице ответов на вопросы
            except Exception:
                eventWorkSheet = self.eventsSpreadSheet.add_worksheet(title = workSheetTitle, rows = "500", cols = len(questionsList) + 2 )
                questionsList.append("Ссылка на Вконтакте")
                eventWorkSheet.append_row(questionsList)

            self.events.addEvent(workSheetTitle, questionsList, hintsList, regularsList)
        self.events.addServiceButtons()
        
    def getUserEvents(self, userLink):
        start = time.time()
        userEvents = []
        for workSheet in self.eventsWorkSheets:
            workSheetTitle = workSheet.title
            col_count = workSheet.col_count
            valuesInCol = workSheet.col_values(col_count)
        
            if userLink in valuesInCol:
                userEvents.append(workSheetTitle)
            else:
                continue 
        end = time.time()
        print(end-start)
        return userEvents
        #userEvents = []
       # for workSheet in workSheetsList:
        #    workSheetTitle = workSheet.title
        #    if(workSheetTitle == "лист1"):
        #        continue
        #    eventWorkSheet = self.eventsSpreadSheet.worksheet(workSheetTitle)
        #    col_count = eventWorkSheet.col_count
        #    valuesInCol = eventWorkSheet.col_values(col_count)
        #
        #    if userLink in valuesInCol:
        #        userEvents.append(workSheetTitle)
        #    else:
        #        continue 
        #return userEvents

    def insertAnswers(self, event, answers):
        eventWorkSheet = self.eventsSpreadSheet.worksheet(event)
        eventWorkSheet.append_row(answers)

    def getEventsList(self):
        return self.events.getEvents()

    def getEventQuestions(self, eventName):
        return self.events.getEventsQuestions(eventName)
