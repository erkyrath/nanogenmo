#!/usr/bin/env python

def printline(txt, speaker):
    prefix = 'B: ' if speaker else 'A: '
    print prefix + '"' + txt + '"'

class Sequence:
    def __init__(self, height):
        self.height = height
    
class Question:
    def __init__(self, asker, height=0):
        self.asker = asker
        self.answerer = not asker
        self.height = height

    def generate(self):
        self.generateq()
        self.generatea()

    def generateq(self):
        printline(self.question(), self.asker)

    def generatea(self):
        printline(self.answer(), self.answerer)

    def elaborate(self):
        if self.height > 0:
            return self
        return ShallITellYouSeq(self)

class CoreSequence(Sequence):
    def __init__(self):
        Sequence.__init__(self, 0)
        self.node = CoreQuestion(False, self.height).elaborate()
        
    def generate(self):
        self.node.generate()
        
class CoreQuestion(Question):
    def question(self):
        return 'is it safe?'
    def answer(self):
        return 'yes.'

class ShallITellYouSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query
        self.subnode = ShallITellYouQ(not query.asker, self.height).elaborate()

    def generate(self):
        self.query.generateq()
        self.subnode.generate()
        self.query.generatea()
        
class ShallITellYouQ(Question):
    def question(self):
        return 'shall I tell you?'
    def answer(self):
        return 'please do.'

    
coreseq = CoreSequence()
coreseq.generate()
