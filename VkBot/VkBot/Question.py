class Question:
    def __init__(self, question, regular, hint):
        self.question = question
        self.regular = regular
        self.hint = hint

    def getQuestion(self):
        return self.question

    def getRegular(self):
        return self.regular

    def getHint(self):
        return self.hint
