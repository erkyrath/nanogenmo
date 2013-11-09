#!/usr/bin/env python

import sys
import random

class Streamer:
    def __init__(self):
        outfl = sys.stdout.write
        self.curstate = 'BEGIN'
        self.revflag = False
        self.revstack = []
        self.curspeaker = None

    def close(self):
        outfl = sys.stdout.write

    def pushquery(self, query):
        assert (self.curspeaker is not None)
        newflag = (self.curspeaker != query.asker)
        self.revstack.append(self.revflag)
        self.revflag = newflag

    def popquery(self):
        self.revflag = self.revstack.pop()

    def writeline(self, func, asker=False, height=None):
        self.curspeaker = asker
        outfl = sys.stdout.write
        outfl('B: ' if asker else 'A: ')
        outfl('(?) ' if height is None else ('(%d) ' % (height,)))
        outfl('"')
        func(self)
        if (self.curstate != 'BEGIN'):
            if self.curstate in ['STOPQ']:
                outfl('?"\n')
            else:
                outfl('."\n')
        self.curstate = 'BEGIN'
        self.curspeaker = None
        assert (not self.revstack)
        assert (not self.revflag)

    def write(self, *ls):
        outfl = sys.stdout.write

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
                    if val == 'I':
                        val = 'I' if not self.revflag else 'you'
                    elif val == 'ME':
                        val = 'me' if not self.revflag else 'you'
                    elif val == 'YOU':
                        val = 'you' if not self.revflag else 'I'
                    elif val == 'OYOU':
                        val = 'you' if not self.revflag else 'me'
                    elif val == 'YOUARE':
                        val = 'you are' if not self.revflag else 'I am'
                    if (docap):
                        outfl(val[0].upper())
                        outfl(val[1:])
                    else:                   
                        outfl(val)
                    self.curstate = 'WORD'
        
    
class Sequence:
    def __init__(self, height):
        self.height = height

    def __repr__(self):
        return '<%s hgt=%d>' % (self.__class__.__name__, self.height)
    
class Question:
    def __init__(self, asker, height=0):
        self.asker = bool(asker)
        self.answerer = not bool(asker)
        self.height = height

    def __repr__(self):
        return '<%s hgt=%d asker=%s>' % (self.__class__.__name__, self.height,
                                         'B' if self.asker else 'A')

    @staticmethod
    def answeryes(strout):
        val = random.choice(['yes', 'yes',
                             'indeed', 'precisely',
                             'unquestionably', 'to a certainty',
                             'never doubt it'])
        strout.write(val)
    
    def generate(self, strout):
        self.generateq(strout)
        self.generatea(strout)

    def generateq(self, strout):
        strout.writeline(self.question, self.asker, self.height)

    def generatea(self, strout):
        strout.writeline(self.answer, self.answerer, self.height)

    def elaborate(self):
        if self.height > 2:
            return self
        #return IBelieveICanAnswerSeq(self)
        return ShallITellYouNowSeq(self)
        #return ShallITellYouWhetherSeq(self)
        #return MayIAskSeq(self)
        #return IHaveAQuestionSeq(self)
        #return HereIsMyAnswerSeq(self)
        #return DoIUnderstandYouToBeAskingSeq(self)

    
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
        
    def qwhether(self, strout):
        strout.write('whether it is safe')
        
    def answer(self, strout):
        self.answeryes(strout)
        
class AltCoreQuestion(Question):
    def question(self, strout):
        strout.write('be', 'I', 'safe')
        strout.write('STOPQ')
        
    def qwhether(self, strout):
        strout.write('whether', 'I', 'be safe')
        
    def answer(self, strout):
        self.answeryes(strout)

        
class IHaveAQuestionSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query

    def generate(self, strout):
        strout.writeline(self.questionplus, self.query.asker, self.height)
        self.query.generatea(strout)

    def questionplus(self, strout):
        strout.write('I have a question:')
        self.query.question(strout)


class HereIsMyAnswerSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query

    def generate(self, strout):
        self.query.generateq(strout)
        strout.writeline(self.answerplus, self.query.asker, self.height)

    def answerplus(self, strout):
        strout.write('Here is my answer:')
        self.query.answer(strout)


class ShallITellYouNowSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query
        self.subnode = ShallITellYouNowQ(query, not query.asker).elaborate()

    def generate(self, strout):
        self.query.generateq(strout)
        self.subnode.generate(strout)
        self.query.generatea(strout)
        
class ShallITellYouNowQ(Question):
    def __init__(self, query, asker):
        Question.__init__(self, asker, query.height+1)
        self.query = query
    
    def question(self, strout):
        strout.write('shall', 'I', 'tell', 'OYOU', 'now')
        strout.write('STOPQ')
        
    def qwhether(self, strout):
        strout.write('whether', 'I', 'shall tell', 'OYOU', 'now')
        
    def answer(self, strout):
        flag = (random.random() < 0.5)
        if flag:
            val = random.choice([
                    ['please do'],
                    ['by all means'],
                    ['I', 'hope for nothing less'],
                    ])
            strout.write(*val)
        else:
            strout.write('by all means tell', 'ME')
            strout.pushquery(self.query)
            self.query.qwhether(strout)
            strout.popquery()


class ShallITellYouWhetherSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query
        self.subnode = ShallITellYouWhetherQ(query, not query.asker).elaborate()

    def generate(self, strout):
        self.query.generateq(strout)
        self.subnode.generate(strout)
        self.query.generatea(strout)
        
class ShallITellYouWhetherQ(Question):
    def __init__(self, query, asker):
        Question.__init__(self, asker, query.height+1)
        self.query = query

    def question(self, strout):
        strout.write('shall', 'I', 'tell', 'OYOU')
        strout.pushquery(self.query)
        self.query.qwhether(strout)
        strout.popquery()
        strout.write('STOPQ')
        
    def qwhether(self, strout):
        strout.write('whether', 'I', 'shall tell', 'OYOU')
        strout.pushquery(self.query)
        self.query.qwhether(strout)
        strout.popquery()
        
    def answer(self, strout):
        val = random.choice([
                ['please do'],
                ['by all means'],
                ['I', 'hope for nothing less'],
                ])
        strout.write(*val)


class DoIUnderstandYouToBeAskingSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query
        self.subnode = DoIUnderstandYouToBeAskingQ(query, not query.asker).elaborate()

    def generate(self, strout):
        self.query.generateq(strout)
        self.subnode.generate(strout)
        self.query.generatea(strout)
        
class DoIUnderstandYouToBeAskingQ(Question):
    def __init__(self, query, asker):
        Question.__init__(self, asker, query.height+1)
        self.query = query

    def question(self, strout):
        strout.write('do', 'I', 'understand', 'OYOU', 'to be asking')
        strout.pushquery(self.query)
        self.query.qwhether(strout)
        strout.popquery()
        strout.write('STOPQ')
        
    def qwhether(self, strout):
        strout.write('whether', 'YOUARE', 'asking')
        strout.pushquery(self.query)
        self.query.qwhether(strout)
        strout.popquery()
        
    def answer(self, strout):
        self.answeryes(strout)


class IBelieveICanAnswerSeq(Sequence):
    def __init__(self, query):
        Sequence.__init__(self, query.height+1)
        self.query = query

    def generate(self, strout):
        self.query.generateq(strout)
        strout.writeline(lambda strout:strout.write('I believe I can answer that'), self.query.answerer, self.height)
        strout.writeline(lambda strout:strout.write('do so, then'), self.query.asker, self.height)
        flag = (random.random() < 0.5)
        if flag:
            strout.writeline(lambda strout:strout.write('I will'), self.query.answerer, self.height)
            strout.writeline(lambda strout:strout.write('then begin'), self.query.asker, self.height)
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
        
    def qwhether(self, strout):
        strout.write('whether I may ask a question')
        
    def answer(self, strout):
        self.answeryes(strout)


streamer = Streamer()

coreseq = CoreSequence()
coreseq.generate(streamer)

streamer.close()
