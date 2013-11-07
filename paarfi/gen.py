#!/usr/bin/env python

import sys

class Streamer:
    def __init__(self):
        outfl = sys.stdout.write
        self.curstate = 'BEGIN'

    def close(self):
        outfl = sys.stdout.write

    def writeline(self, func, asker=False, height=None):
        outfl = sys.stdout.write
        outfl('?:' if height is None else ('%d:' % (height,)))
        outfl('B: ' if asker else 'A: ')
        outfl('"')
        func(self)
        if (self.curstate != 'BEGIN'):
            if self.curstate in ['STOPQ']:
                outfl('?"\n')
            else:
                outfl('."\n')
        self.curstate = 'BEGIN'

    def write(self, val):
        outfl = sys.stdout.write

        if type(val) == list:
            ls = val
        else:
            ls = [ val ]

        for val in ls:
            
            if (not val):
                pass
            elif (val == 'JOIN' or val == 'COMMA' or val == 'SEMI' or val == 'STOP' or val == 'STOPQ' or val == 'PARA'):
                # should be max of self.curstate, val
                if (self.curstate != 'BEGIN'):
                    self.curstate = val
            else:
                docap = False
                if (self.curstate == 'BEGIN' or self.curstate == 'STOP' or self.curstate == 'STOPQ' or self.curstate == 'PARA'):
                    if (self.curstate == 'STOP'):
                        outfl('. ')
                    elif (self.curstate == 'STOPQ'):
                        outfl('? ')
                    elif (self.curstate == 'PARA'):
                        outfl('."\n"')
                    docap = True
                elif (self.curstate == 'SEMI'):
                    outfl('; ')
                elif (self.curstate == 'COMMA'):
                    outfl(', ')
                elif (self.curstate == 'JOIN'):
                    pass
                elif (self.curstate == 'JOINCAP'):
                    docap = True
                elif (self.curstate == 'A'):
                    if (val == 'ANFORM' or (val != 'AFORM' and val[0].lower() in 'aeiou')):
                        outfl('n ')
                    else:
                        outfl(' ')
                else:
                    outfl(' ')
                if (val == 'A'):
                    if (docap):
                        outfl('A')
                    else:
                        outfl('a')
                    self.curstate = 'A'
                elif (val == 'AFORM' or val == 'ANFORM'):
                    if (docap):
                        self.curstate = 'JOINCAP'
                    else:
                        self.curstate = 'JOIN'
                else:
                    if (docap):
                        outfl(val[0].upper())
                        outfl(val[1:])
                    else:                   
                        outfl(val)
                    self.curstate = 'WORD'
        
    
class Sequence:
    def __init__(self, height):
        self.height = height
    
class Question:
    def __init__(self, asker, height=0):
        self.asker = bool(asker)
        self.answerer = not bool(asker)
        self.height = height

    def generate(self, strout):
        self.generateq(strout)
        self.generatea(strout)

    def generateq(self, strout):
        strout.writeline(self.question, self.asker, self.height)

    def generatea(self, strout):
        strout.writeline(self.answer, self.answerer, self.height)

    def elaborate(self):
        if self.height > 0:
            return self
        return IBelieveICanAnswerSeq(self)
        #return ShallITellYouSeq(self)
        #return MayIAskSeq(self)

    
class CoreSequence(Sequence):
    def __init__(self):
        Sequence.__init__(self, 0)
        self.node = CoreQuestion(False, self.height).elaborate()
        
    def generate(self, strout):
        self.node.generate(strout)
        
class CoreQuestion(Question):
    def question(self, strout):
        strout.write('is it safe')
        strout.write('STOPQ')
    def answer(self, strout):
        strout.write('yes')

    
class ShallITellYouSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query
        self.subnode = ShallITellYouQ(not query.asker, self.height).elaborate()

    def generate(self, strout):
        self.query.generateq(strout)
        self.subnode.generate(strout)
        self.query.generatea(strout)
        
class ShallITellYouQ(Question):
    def question(self, strout):
        strout.write('shall I tell you')
        strout.write('STOPQ')
    def answer(self, strout):
        strout.write('please do')


class IBelieveICanAnswerSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query

    def generate(self, strout):
        self.query.generateq(strout)
        strout.writeline(lambda strout:strout.write(['I believe I can answer that']), self.query.answerer, self.height)
        strout.writeline(lambda strout:strout.write(['do so, then']), self.query.asker, self.height)
        ### 50% of next pair?
        strout.writeline(lambda strout:strout.write(['I will']), self.query.answerer, self.height)
        strout.writeline(lambda strout:strout.write(['then begin']), self.query.asker, self.height)
        self.query.generatea(strout)
        
        
class MayIAskSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query
        self.subnode = MayIAskQ(query.asker, self.height).elaborate()

    def generate(self, strout):
        self.subnode.generate(strout)
        self.query.generateq(strout)
        self.query.generatea(strout)
        
class MayIAskQ(Question):
    def question(self, strout):
        strout.write('may I ask a question')
        strout.write('STOPQ')
    def answer(self, strout):
        strout.write('yes')


streamer = Streamer()

coreseq = CoreSequence()
coreseq.generate(streamer)

streamer.close()
