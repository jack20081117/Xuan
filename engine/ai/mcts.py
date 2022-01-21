#蒙特卡洛树搜索模块
#Monte Carlo Tree Search,简称MCTS

import copy,logging
from src.go import Go
from ai.xuan import Xuan

class Node(object):
    def __init__(self,string,board,legalMoves,probas,parent=None):
        self.string=string
        self.board=board
        self.legalMoves=legalMoves
        self.probas=probas
        self.parent=parent#父节点
        self.son=[]#子树集合
        self.num=0#便利的次数

    def isLeaf(self):
        return len(self.son)==0

    def getSon(self):
        return self.son

    def expand(self,string,board,legalMoves,probas):
        self.son.append(Node(string=string,board=board,legalMoves=legalMoves,probas=probas,parent=self))

class MCTS(object):
    engine=None

    def __init__(self):
        self.root=None
        self.engine=Xuan()

    def analyze(self,goban):
        rootLegalMoves,rootProbas,rootWinner=self.engine.doAnalyze(goban=goban)
        rootString,rootBoard=self.engine.string,self.engine.board
        self.root=Node(string=rootString,board=rootBoard,legalMoves=rootLegalMoves,probas=rootProbas)
        color=1 if len(goban)==0 else Go.reverseColor(goban[-1]['color'])
        logging.info('上一步的合法落子点为 rootLegalMoves=%s'%rootLegalMoves)
        #把这步棋模拟的内容加上
        for i in range(len(rootLegalMoves)):
            singleMove=rootLegalMoves[i]
            x,y=singleMove['x'],singleMove['y']
            backupGoban=copy.deepcopy(goban)
            backupGoban.append({
                'x':x,
                'y':y,
                'color':color
            })
            colorText=Go.getColorTextByNum(color)
            success,board,string,robX,robY=self.engine.go.GoLogic(x,y,colorText)
            legalMoves,probas,winner=self.engine.doAnalyze(backupGoban)
            analyzeString,analyzeBoard=self.engine.string,self.engine.board
            logging.info('扩展的合法落子点 legalMoves:%s'%legalMoves)
            self.root.expand(string=string,board=board,legalMoves=legalMoves,probas=probas)

    def mctExpand(self):
        pass