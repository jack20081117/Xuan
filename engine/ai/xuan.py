import copy,torch, json,logging
from ai.datacenter import DataCenter
from config import GLOBAL_DICT as gl
from src.go import Go
from src.tools import *

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
        self.modelPathConfig=gl.get('modelPath',None)
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
        dataDict=json.loads(data)#收到的数据转json
        if dataDict['operator']=='run':#引擎分析
            self.parseStepData(dataDict)
            goban=dataDict['goban']
            legalMoves,probas,winner,string,board=self.doAnalyze(goban)
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
            goban=json.loads(goban)#棋谱是单独的json,需要再解析一次
            parsedSgf=self.go.parseGoban2Sgf(goban)['sgf']
            additional=self.go.parseAdditionalSgf(parsedSgf)
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

    def analyze(self,state)->tuple:#分析数据结构
        featureMaps=self.feature(state.clone().detach())
        winner=self.value(featureMaps)
        probas=self.policy(featureMaps)
        return probas,winner

    @staticmethod
    def transferAnalyze2List(probas,winner):#将引擎分析的内容转换为前端可读的数据
        probas=probas.tolist()
        probas=probas[0]#因为获取的是[[]],所以拿第一个
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
        self.board,self.string,self.robX,self.robY,boardList=self.getStringAndBoardFromFront(goban=goban)
        state=self.getPredictData(boardList=boardList)
        #分析,然后获取合法的落子点
        probas,winner=self.analyze(state=state)
        resultList=self.transferAnalyze2List(probas=probas,winner=winner)
        legalMoves=self.getLegalMoves(allMoves=resultList)
        return legalMoves,probas,winner,self.string,self.board

    def getLegalMoves(self,allMoves,threshold=0):#获取allMoves中合法的落子点,默认取10个
        if not threshold:
            threshold=int(self.aiConfig['THRESHOLD'])
        legals=[]#合法落子点
        illegals=[]#非法落子点
        legalNum=0
        for i in range(len(allMoves)):
            if legalNum>=threshold:
                break
            singleMove=allMoves[i]
            x,y=singleMove['x'],singleMove['y']
            #初始化Go
            self.go.board=copy.deepcopy(self.board)
            self.go.string=copy.deepcopy(self.string)
            self.go.robX=self.robX
            self.go.robY=self.robY
            success,board,string,robX,robY=self.go.GoLogic(x=x,y=y,color=self.color)#检查下(x,y)是否符合围棋逻辑
            if success:#符合围棋逻辑,是合法的落子点
                legals.append({'x':x,'y':y})
                legalNum+=1
            else:#不符合围棋逻辑,是非法的落子点
                illegals.append({'x':x,'y':y})
        logging.info("本次获取的非法落子点 :>> %s"%illegals)
        logging.info("非法落子点数量:%d"%len(illegals))
        return legals

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