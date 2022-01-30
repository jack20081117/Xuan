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
        self.children=[]#子树集合
        self.num=0#遍历的次数

    def __str__(self):
        return 'Node object,children:%s'%self.children

    __repr__=__str__

    def isLeaf(self):
        return len(self.children)==0

    def getChildren(self):
        return self.children

    def setChildren(self,children:list):
        self.children=children

    def getParent(self):
        return self.parent

    def setParent(self,parent):
        self.parent=parent

    def expand(self,string,board,legalMoves,probas):
        self.children.append(Node(string=string,board=board,legalMoves=legalMoves,probas=probas,parent=self))

class MCTS(object):
    engine=None

    def __init__(self):
        self.root=None
        self.engine=Xuan()

    def analyze(self,goban):
        rootLegalMoves,rootProbas,rootWinner,rootString,rootBoard=self.engine.doAnalyze(goban=goban)
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
            legalMoves,probas,winner,analyzeString,analyzeBoard=self.engine.doAnalyze(backupGoban)
            logging.info('扩展的合法落子点 legalMoves:%s'%legalMoves)
            self.root.expand(string=string,board=board,legalMoves=legalMoves,probas=probas)

    def mctExpand(self):
        pass