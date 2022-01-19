import copy,torch, json,logging

from engine.ai.datacenter import DataCenter
from engine.config import GLOBAL_DICT as gl
from engine.src.go import Go
from engine.src.tools import *

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Xuan(object):#围棋AI的核心模块
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
        #初始化围棋相关内容
        self.board=getEmptyBoard()
        self.string=getEmptyString()
        self.device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.getModel()

    def getModel(self):#获取神经网络
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

    def parseBoard2Tensor(self,option):#棋盘数据转张量
        return torch.tensor(self.board,dtype=torch.float if option=='float' else torch.int)

    def parseStepData(self,rawData):#获取引擎需要的数据
        self.board=rawData['board']
        self.color=rawData['color']

    def parseOperator(self,data):#对从前端接收到的信息做处理
        dataDict=json.loads(data)
        if dataDict['operator']=='run':#引擎分析
            self.parseStepData(dataDict)
            goban=dataDict['goban']
            legalMoves,probas,winner=self.doAnalyze(goban)
            return {
                'code':0,
                'message':'success',
                'data':legalMoves
            }
        elif dataDict['operator']=='saveGoban':#保存棋谱
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

    def getPredictData(self,boardList):#获取需要神经网络分析的数据结构
        self.go.__init__()
        board=self.board
        color=self.color
        state=[]
        colorNum,myColor,oppoColor=(1,1,-1) if color=='black' else (0,-1,1)
        #这里分别取自己和对手的最近7个棋盘状态
        myLast7Boards,oppoLast7Boards=self.go.getLastBoard(boardList,len(boardList)-1,myColor,oppoColor)
        myBoard,oppoBoard=self.go.getMyOppoBoard(board,myColor,oppoColor)
        colorBoard=self.go.getCurrentColorBoard(colorNum)
        myList=[myBoard]
        myList.extend(myLast7Boards)
        oppoList=[oppoBoard]
        oppoList.extend(oppoLast7Boards)
        myList.extend(oppoList)
        myList.append(colorBoard)
        state.append(myList)
        state=torch.tensor(state,dtype=torch.float,device=DEVICE)
        state=state.reshape(1,self.inplanes,19,19)
        return state

    def analyze(self,state):#分析数据结构
        featureMaps=self.feature(state.clone().detach())
        winner=self.value(featureMaps)
        probas=self.policy(featureMaps)
        return probas,winner

    @staticmethod
    def transferAnalyze2List(probas,winner):#将引擎分析的内容转换为前端可读的数据
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
        resultList=sorted(resultList,reverse=True,key=lambda e:e.__getitem__('probas')) #根据probas从大到小排序(注意reverse=True)
        return resultList

    def doAnalyze(self,goban):
        #棋盘数据转张量,参数int或float,不传默认int
        self.board,self.string,self.robX,self.robY,boardList=self.getStringAndBoardFromFront(goban=goban)
        state=self.getPredictData(boardList)

        #分析,然后获取合法的落子点
        probas,winner=self.analyze(state)
        resultList=self.transferAnalyze2List(probas,winner)
        legalMoves=self.getLegalMoves(resultList)
        return legalMoves,probas,winner

    def getLegalMoves(self,allMoves,threshold=5):#获取合法的落子点,默认取5个
        result=[]
        nums=0
        illegals=[]
        for i in range(len(allMoves)):
            if nums>=threshold:
                break
            singleMove=allMoves[i]
            x=singleMove['x']
            y=singleMove['y']
            #初始化Go
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

    def getStringAndBoardFromFront(self,goban):#根据前端发来的棋谱获取棋盘和棋串
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