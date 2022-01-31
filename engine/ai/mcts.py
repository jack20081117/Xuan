#蒙特卡洛树搜索模块
#Monte Carlo Tree Search,简称MCTS

import copy,logging,cmath,math
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
        self.times=0#遍历的次数
        self.value=0#累计评分

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
        self.rootNode=None
        self.engine=Xuan()

    def analyze(self,goban):#蒙特卡洛树搜索 分析
        rootLegalMoves,rootProbas,rootWinner,rootString,rootBoard=self.engine.doAnalyze(goban=goban)
        self.rootNode=Node(string=rootString,board=rootBoard,legalMoves=rootLegalMoves,probas=rootProbas)
        colorNum=1 if len(goban)==0 else Go.reverseColor(goban[-1]['color'])
        logging.info('这一步的合法落子点为 rootLegalMoves=%s'%rootLegalMoves)
        #把这步棋模拟的内容加上
        for i in range(len(rootLegalMoves)):
            singleMove=rootLegalMoves[i]
            x,y=singleMove['x'],singleMove['y']
            tempGoban=copy.deepcopy(goban)
            tempGoban.append({
                'x':x,
                'y':y,
                'color':colorNum
            })
            colorText=Go.getColorTextByNum(num=colorNum)
            success,board,string,robX,robY=self.engine.go.GoLogic(x=x,y=y,color=colorText)
            legalMoves,probas,winner,analyzeString,analyzeBoard=self.engine.doAnalyze(goban=tempGoban)
            logging.info('扩展的合法落子点 legalMoves:%s'%legalMoves)
            self.rootNode.expand(string=string,board=board,legalMoves=legalMoves,probas=probas)

    def backward(self,node:Node,times:int,value:int):#蒙特卡洛树搜索 回溯
        node.times+=times
        node.value+=value
        if isinstance(node.parent,Node):
            parent=node.parent
            self.backward(node=parent,times=times,value=value)