import gspread
import Events
import asyncio
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

        self.events = Events.Events()

        #создать словарь с ключом в виде названия ивента и значением = объектом workSheet

        #убедиться в наличии файла vkEvents
        #для каждого листа проверить соответствие в events
    def createEventsTable(self):
        workSheetsList = self.questionsSpreadSheet.worksheets() #список всех листов в таблице с вопросами
        eventWorkSheetsList = self.eventsSpreadSheet.worksheets() #список всех листов в таблице с ответами на вопросы
        for workSheet in workSheetsList:
            workSheetTitle = workSheet.title
            try:
                existedWorkSheet = eventWorkSheetsList.worksheet(workSheetTitle) #существует ли данный ивент в таблице ответов на вопросы
            except Exception:
                questionsList = workSheet.col_values(1)
                hintsList = workSheet.col_values(2)
                regularsList = workSheet.col_values(3)
                eventWorkSheet = self.eventsSpreadSheet.add_worksheet(title = workSheetTitle, rows = "500", cols = len(questionsList) + 2 )

                self.events.addEvent(workSheetTitle, questionsList, hintsList, regularsList)
                eventWorkSheet.append_row(questionsList)

        self.events.addServiceButtons()
