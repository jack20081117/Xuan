import copy,torch, json,logging

from ai.datacenter import DataCenter
from config import GLOBAL_DICT as gl
from src.go import Go
from src.tools import *

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Xuan(object):
    board=[]
    color=None
    string={}
    robX=None
    robY=None
    go=None
    datacenter=None
    models=None
    feature=None
    policy=None
    value=None
    device=None
    aiConfig=None
    modelPathConfig=None
    inplanes=None

    def __init__(self):
        self.go=Go()
        self.datacenter=DataCenter()
        self.board=getEmptyBoard()
        self.string=getEmptyString()
        self.device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.getModel()

    def getModel(self):
        logging.info('DEVICE=%s'%DEVICE)
        self.aiConfig=gl.get('ai',None)
        self.modelPathConfig=gl.get('model_path',None)
        self.inplanes=int(self.aiConfig['inplane'])
        featurePath=self.modelPathConfig['feature']
        policyPath=self.modelPathConfig['policy']
        valuePath=self.modelPathConfig['value']
        self.feature=torch.load(featurePath,map_location=DEVICE)
        self.policy=torch.load(policyPath,map_location=DEVICE)
        self.value=torch.load(valuePath,map_location=DEVICE)
        logging.info("获取神经网络权重成功")

    def parseBoard2Tensor(self,option):
        return torch.tensor(self.board,dtype=torch.float if option=='float' else torch.int)

    def parseStepData(self,rawData):
        self.board=rawData['board']
        self.color=rawData['color']

    def parseOperator(self,data):
        dataDict=json.loads(data)
        if dataDict['operator']=='run':
            self.parseStepData(dataDict)
            goban=dataDict['goban']
            legalMoves,probas,winner=self.doAnalyze(goban)
            return {
                'code':0,
                'message':'success',
                'data':legalMoves
            }
        elif dataDict['operator']=='saveGoban':
            goban=dataDict['goban']
            logging.info('收到的棋谱为%s'%goban)
            if len(goban)==0:
                return {
                    'code':-1,
                    'message':"空棋谱不进行处理"
                }
            goban=json.loads(goban)
            parsedSgf=self.go.parseGoban2Sgf(goban)
            additional=self.go.parseAdditionalSgf(goban)
            result=self.datacenter.saveGoban(parsedSgf,additional)
            return result

    def getPredictData(self,boardList):
        self.go.__init__()
        board=self.board
        color=self.color
        state=[]
        colorNum,myColor,oppoColor=(1,1,-1) if color=='black' else (0,0,1)
        myLast,oppoLast=self.go.getLastBoard(boardList,len(boardList)-1,1,1)
        myBoard,oppoBoard=self.go.getMyOppoBoard(board,myColor,oppoColor)
        colorBoard=self.go.getCurrentColorBoard(myColor)
        myList=[myBoard];myList.extend(myLast)
        oppoList=[oppoBoard];oppoList.extend(oppoLast)
        myList.extend(oppoList)
        myList.append(colorBoard)
        state.append(myList)
        state=torch.tensor(state,dtype=torch.float,device=DEVICE)
        state=state.reshape(1,self.inplanes,19,19)
        return state

    def analyze(self,state):
        featureMaps=self.feature(state.clone().detach())
        winner=self.value(featureMaps)
        probas=self.policy(featureMaps)
        return probas,winner

    @staticmethod
    def transferAnalyze2List(probas,winner):
        probas=probas.tolist()
        probas=probas[0]
        winner=winner.tolist()
        resultList=[]
        for i in range(len(probas)):
            x=i%19
            y=int(i/19)
            singleProbas=probas[i]
            resultList.append({
                'x':x,
                'y':y,
                'probas':singleProbas
            })
        resultList=sorted(resultList,reverse=True,key=lambda e:e.__getitem__('probas'))
        return resultList

    def doAnalyze(self,goban):
        self.board,self.string,self.robX,self.robY,boardList=self.getStringAndBoardFromFront(goban=goban)
        state=self.getPredictData(boardList)
        probas,winner=self.analyze(state)
        resultList=self.transferAnalyze2List(probas,winner)
        legalMoves=self.getLegalMoves(resultList)
        return legalMoves,probas,winner

    def getLegalMoves(self,allMoves,threshold=5):
        result=[]
        nums=0
        illegals=[]
        for i in range(len(allMoves)):
            if nums>=threshold:
                break
            singleMove=allMoves[i]
            x=singleMove['x']
            y=singleMove['y']
            self.go.board=copy.deepcopy(self.board)
            self.go.string=copy.deepcopy(self.string)
            self.go.robX=self.robX
            self.go.robY=self.robY
            success,board,string,robX,robY=self.go.GoLogic(x,y,color=self.color)
            if success:
                result.append({
                    'x':x,
                    'y':y
                })
                nums+=1
            else:
                illegals.append({
                    'x':x,
                    'y':y
                })
        logging.warning("非法落子点数量:%d"%len(illegals))
        return result

    def getStringAndBoardFromFront(self,goban):
        self.go.__init__()
        board=None
        string=None
        robX=None
        robY=None
        boardList=[]
        if len(goban)==0:
            return getEmptyBoard(),getEmptyString(),None,None,boardList
        for i in range(len(goban)):
            step=goban[i]
            x=step['x']
            y=step['y']
            color=step['color']
            colorText=self.go.getColorTextByNum(color)
            success,board,string,robX,robY=self.go.GoLogic(x,y,colorText)
            boardList.append(board)
            if success is not True:
                logging.info("step=%s,x=%d,y=%d,color=%d"%(step,x,y,color))
                raise RuntimeError("组成围棋逻辑出现问题")
        return board,string,robX,robY,boardList