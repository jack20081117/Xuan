import json,os,logging
from config import *
from config import GLOBAL_DICT as gl
from src.tools import *
from src.go import Go
from ai.datacenter import DataCenter
from ai.dataset import MyDataset
from torch.utils.data import DataLoader
import torch,numpy,platform

from model.loss import Loss
from model.policy import PolicyNet
from model.value import ValueNet
from model.feature import Extractor
from ai.xuan import Xuan

osType=platform.system()

logFileName='./savedModel/trainData.txt'

config=CONFIG
gl['modelPath']=config['model']
gl['ai']=config['ai']
DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info("DEVICE=%s"%DEVICE)
batchSize=int(config['ai']['BATCHSIZE'])
checkPoint=0
go=Go()

featurePath=config['model'].get('feature',None)
policyPath=config['model'].get('policy',None)
valuePath=config['model'].get('value',None)

def getDataSet()->list:
    dbpath=os.path.dirname(os.path.realpath(__file__))
    gl['logpath']=dbpath
    old=os.path.join(dbpath,config['db'].get('old',None))
    current=os.path.join(dbpath,config['db'].get('current',None))
    ai=os.path.join(dbpath,config['db'].get('ai',None))
    Jack=os.path.join(dbpath,config['db'].get('Jack',None))
    dbpath=os.path.join(dbpath,config['db'].get('current',None))
    gl['dbpath']=dbpath

    model={
        'old':old,
        'current':current,
        'ai':ai,
        'Jack':Jack
    }

    gl['model']=model

    dataCenter=DataCenter()
    allData=dataCenter.getAllDataSet()
    return allData

def collateFn(data):
    state=[]
    winnerList=[]
    probasList=[]

    for i in range(len(data)):
        singleData=data[i]
        goban,winner,parsedSgf,stringList=go.parseSgf2NetworkData(singleData)

        for j in range(len(goban)-1):
            #随机取棋盘的一块值
            rand=j
            winnerList.append(winner)
            currentDict=parsedSgf[rand]
            #计算出下一手的位置
            nextDict=parsedSgf[rand+1]
            nextX,nextY=nextDict['x'],nextDict['y']
            nextBoard=getEmptyBoard()
            nextBoard[nextX][nextY]=1
            currentString=stringList[rand]
            currentColor=currentDict['color']
            currentBoard=goban[rand]

            #上一手是黑下,那么引擎要关注白的局面,反之也是
            if currentColor=='black':
                colorSetNum=1
                myColor=1
                oppoColor=-1
            else:
                colorSetNum=0
                myColor=-1
                oppoColor=1
            #获取己方和对手方的最近的7步棋
            myLast7Boards,oppoLast7Boards=go.getLastBoard(goban,j,1,1)
            #将原生的棋盘数据抽成己方的棋盘和对手方的棋盘,其他位置全0处理
            myBoard,oppoBoard=go.getMyOppoBoard(currentBoard,myColor,oppoColor)
            colorBoard=go.getCurrentColorBoard(colorSetNum)
            my=[myBoard]
            my.extend(myLast7Boards)
            oppo=[oppoBoard]
            oppo.extend(oppoLast7Boards)
            my.extend(oppo)
            my.append(colorBoard)
            state.append(my)
            probasList.append(loopFor2D(nextBoard))

    return state,winnerList,probasList

def loadModel(inplane,outplane,outplaneMap,block):
    try:
        feature=torch.load(featurePath,map_location=DEVICE)
        policy=torch.load(policyPath,map_location=DEVICE)
        value=torch.load(valuePath,map_location=DEVICE)
        logging.info("从权重文件读取网络成功")
    except Exception as e:
        logging.error("重建神经网络 原因 :>> %s"%e)
        feature=Extractor(inplane,outplaneMap,block).to(DEVICE)
        policy=PolicyNet(outplaneMap,outplane).to(DEVICE)
        value=ValueNet(outplaneMap,outplane).to(DEVICE)
        saveModel(feature,policy,value,True)
    return feature,policy,value

def saveModel(feature,policy,value,saveFirst=False):
    try:
        if saveFirst is True:
            logging.info('保存feature网络...')
            torch.save(feature,featurePath)
            logging.info('保存policy网络...')
            torch.save(policy,policyPath)
            logging.info('保存value网络...')
            torch.save(value,valuePath)
        time=getDatetime()['timestr']
        os.mkdir(os.path.join('savedModel',time))
        logging.info('保存feature网络...')
        torch.save(feature,os.path.join('savedModel',time,'feature.bin'))
        logging.info('保存policy网络...')
        torch.save(policy,os.path.join('savedModel',time,'policy.bin'))
        logging.info('保存value网络...')
        torch.save(value,os.path.join('savedModel',time,'value.bin'))
        #一定要保存一个最新的
        logging.info('保存最新的feature网络...')
        torch.save(feature,featurePath)
        logging.info('保存最新的policy网络...')
        torch.save(policy,policyPath)
        logging.info('保存最新的value网络...')
        torch.save(value,valuePath)

    except Exception as e:
        logging.error("保存神经网络失败 原因 :>> %s"%e)
        #保存到目录失败 那就只存最新的
        logging.info('保存feature网络...')
        torch.save(feature,featurePath)
        logging.info('保存policy网络...')
        torch.save(policy,policyPath)
        logging.info('保存value网络...')
        torch.save(value,valuePath)

def test(dataSet):#测试模块
    engine=Xuan()
    accuracy=[]#精度
    for i in range(len(dataSet)):
        sgf=dataSet[i]
        goban,winner,parsedSgf,stringList=go.parseSgf2NetworkData(sgf)
        currentGoban=[]

        correct=0

        for j in range(len(goban)-1):
            currentGoban.append(goban[j])
            engine.board=goban[j]
            engine.string=stringList[j]
            engine.color=parsedSgf[j]['color']
            state=engine.getPredictData(currentGoban)
            probas,winner=engine.analyze(state)
            result=engine.transferAnalyze2List(probas,winner)
            legal=engine.getLegalMoves(result,threshold=1)
            best=legal[0]
            sgfChoice=parsedSgf[j+1]
            if best['x']==sgfChoice['x'] and best['y']==sgfChoice['y']:
                correct+=1

        correctPercent=float(correct)/len(goban)
        accuracy.append({
            'correct':correct,
            'num':len(goban),
            'percent':correctPercent
        })
    logging.info('accuracy:%s'%accuracy)
    with open(logFileName,encoding='utf-8',mode='a+') as f:
        f.write(json.dumps({
            'type':'accuracy',
            'data':accuracy
        }))
        f.write('\n')
    logging.info('保存数据成功')

def train(dataSet,times,testDataSet):#训练的主函数
    LR=float(config['ai'].get('LR',None))#获取学习率

    #获取CNN的通道数,记得一定要转成int
    inplane=int(config['ai'].get('inplane',None))
    outplane=int(config['ai'].get('outplane',None))
    outPlaneMap=int(config['ai'].get('outPlaneMap',None))
    block=int(config['ai'].get('BLOCK',None))
    ADAM=int(config['ai'].get('ADAM',None))
    L2_REG=float(config['ai'].get('L2_REG',None))
    MOMENTUM=float(config['ai'].get('MOMENTUM',None))
    EPOCH=int(config['ai'].get('EPOCH',None))

    if osType!='Windows' and EPOCH>4:
        EPOCH=4

    criterion=Loss()
    #决定三个神经网络的出入通道
    feature,policy,value=loadModel(inplane,outplane,outPlaneMap,block)
    dataLoader=DataLoader(dataSet,batch_size=batchSize,collate_fn=collateFn,shuffle=True,num_workers=4,drop_last=True)
    jointParams=list(feature.parameters())+list(policy.parameters())+list(value.parameters())

    optimizer=torch.optim.Adam(jointParams,lr=LR) if ADAM==1 else torch.optim.SGD(jointParams,lr=LR,weight_decay=L2_REG,momentum=MOMENTUM)

    logging.info('共%d个EPOCH'%EPOCH)
    epochLoss=[]
    for i in range(EPOCH):
        batchLoss=[]
        epochWinnerList=[]
        for batchID,(state,winnerList,probasList) in enumerate(dataLoader):
            length=len(state)
            logging.info('这批数据共%d步棋'%length)
            batchWinnerList=[]
            singleLoss=[]
            while length>=batchSize:
                batchState=state[0:batchSize]
                batchWinner=winnerList[0:batchSize]
                batchProbas=probasList[0:batchSize]
                #转张量
                batchState=torch.tensor(batchState,dtype=torch.float,device=DEVICE)
                batchWinner=torch.tensor(batchWinner,dtype=torch.float,device=DEVICE)
                batchProbas=torch.tensor(batchProbas,dtype=torch.float,device=DEVICE)
                batchProbas=torch.reshape(batchProbas,(batchSize,-1))
                optimizer.zero_grad()

                featureMaps=feature(batchState.clone().detach())
                winner=policy(featureMaps)
                probas=value(featureMaps)
                loss=criterion(winner,batchWinner,probas,batchProbas)
                loss.backward()
                optimizer.step()
                singleLoss.append(float(loss))
                state=state[batchSize:length]
                winnerList=winnerList[batchSize:length]
                probasList=probasList[batchSize:length]
                length-=batchSize
                wList=winner.tolist()
                batchWinnerList.append(wList[0])
            batchLoss.append(numpy.mean(singleLoss))
            epochWinnerList.append(numpy.mean(batchWinnerList))
            logging.info("当前epoch=[%s] 共[%s]个,index=[%s] 到[%s]结束训练 批次loss=%s,time=%s"
                         %(i+1,EPOCH,batchID+1,times,numpy.mean(singleLoss),getDatetime()['timeformat']))
        logging.info("训练完一个epoch,开始测试")
        try:
            test(testDataSet)
        except Exception as e:
            logging.error("测试出现错误->%s"%e)
        logging.info("Average backward pass->{}".format(numpy.mean(batchLoss)))
        epochLoss.append(numpy.mean(batchLoss))
        logging.info("Epoch loss:{}".format(epochLoss))
        with open(logFileName,encoding='utf-8',mode='a+') as f:
            f.write(json.dumps({
                'type':'loss',
                'data':batchLoss
            }))
            f.write('\n')
            f.write(json.dumps({
                'type':'epochWinner',
                'data':epochWinnerList
            }))
            f.write('\n')
        saveModel(feature=feature,policy=policy,value=value)

if __name__ == '__main__':
    begintime=getDatetime()['timeformat']
    data=getDataSet()
    trainData=data[0:batchSize*100]

    testData=data[batchSize*105:batchSize*105+5]
    #test(testData)
    logging.info("共%d个batch"%int(len(trainData)/batchSize))
    myDataSet=MyDataset(trainData)
    train(myDataSet,int(len(trainData)/batchSize),testData)
    endtime=getDatetime()['timeformat']
    logging.info("训练完毕,开始时间:%s,结束时间:%s"%(begintime,endtime))