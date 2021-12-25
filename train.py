import configparser,copy,json,os,logging
from config import *
from src.net import Server
from database.db import Database
from config import GLOBAL_DICT as gl
from src.tools import *
from src.go import Go
from ai.datacenter import DataCenter
from ai.dataset import MyDataset
import torch.nn as nn
from torch.utils.data import TensorDataset,DataLoader
import torch,random,numpy,platform

from model.loss import Loss
from model.policy import PolicyNet
from model.value import ValueNet
from model.feature import Extractor
from ai.engine import Xuan

osType=platform.system()

log_fileName='./savedModel/trainData.txt'

filePath='./config.ini'
config=configparser.ConfigParser()
config.read(filePath,encoding='utf-8')
gl['modelPath']=config['model']
gl['ai']=config['ai']
DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info("DEVICE=%s"%DEVICE)
batchSize=int(config['ai']['BATCHSIZE'])
checkPoint=0
go=Go()

featurePath=config['model']['feature']
policyPath=config['model']['policy']
valuePath=config['model']['value']

def getDataSet():
    dbpath=os.path.dirname(os.path.realpath(__file__))
    gl['logpath']=dbpath

    old=os.path.join(dbpath,config['db'].get('old',None))
    current=os.path.join(dbpath,config['db'].get('current',None))
    ai=os.path.join(dbpath,config['db'].get('ai',None))
    Jack=os.path.join(dbpath,config['db'].get('Jack',None))

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
        goban,winner,parsedSgf,stringList=go.parseSingleData(singleData)

        for j in range(len(goban)-1):
            rand=j
            winnerList.append(winner)
            currentDict=parsedSgf[rand]
            nextDict=parsedSgf[rand+1]
            nextX,nextY=nextDict['x'],nextDict['y']
            nextBoard=getEmptyBoard()
            nextBoard[nextX][nextY]=1
            currentString=stringList[rand]
            currentColor=currentDict['color']
            currentBoard=goban[rand]

            if currentColor=='white':
                colorSetNum=0
                myColor=-1
                oppoColor=1
            else:
                colorSetNum=1
                myColor=1
                oppoColor=-1
            myLast,oppoLast=go.getLastBoard(goban,j,1,1)
            myBoard,oppoBoard=go.getMyOppoBoard(currentBoard,myColor,oppoColor)
            colorBoard=go.getCurrentColorBoard(colorSetNum)
            my=[myBoard]
            my.extend(myLast)
            oppo=[oppoBoard]
            oppo.extend(oppoLast)
            my.extend(oppo)
            my.append(colorBoard)
            state.append(my)
            probasList.append(nextBoard)

    return state,winnerList,probasList

def loadModel(inplane,outplane,outplaneMap,block):
    try:
        feature=torch.load(featurePath,map_location=DEVICE)
        policy=torch.load(policyPath,map_location=DEVICE)
        value=torch.load(valuePath,map_location=DEVICE)
        logging.info("从权重文件读取网络成功")
    except Exception as e:
        logging.error("重建神经网络 原因-> %s", e)
        feature=Extractor(inplane,outplaneMap,block).to(DEVICE)
        policy=PolicyNet(outplaneMap,outplane).to(DEVICE)
        value=ValueNet(outplaneMap,outplane).to(DEVICE)
        saveModel(feature,policy,value,True)
    return feature,policy,value

def saveModel(feature,policy,value,first=False):
    try:
        if first is True:
            logging.info('保存feature网络...')
            torch.save(feature,featurePath)
            logging.info('保存policy网络...')
            torch.save(policy,policyPath)
            logging.info('保存value网络...')
            torch.save(value,valuePath)
        time=getDatetime()['datestr']
        os.mkdir(os.path.join('./savedModel',time))
        logging.info('保存feature网络...')
        torch.save(feature,os.path.join('./savedModel',time,'feature.bin'))
        logging.info('保存policy网络...')
        torch.save(policy,os.path.join('./savedModel',time,'policy.bin'))
        logging.info('保存value网络...')
        torch.save(value,os.path.join('./savedModel',time,'value.bin'))

        logging.info('保存最新的feature网络...')
        torch.save(feature,featurePath)
        logging.info('保存最新的policy网络...')
        torch.save(policy,policyPath)
        logging.info('保存最新的value网络...')
        torch.save(value,valuePath)

    except Exception as e:
        logging.error("保存神经网络失败 原因-> %s",e)
        logging.info('保存feature网络...')
        torch.save(feature,featurePath)
        logging.info('保存policy网络...')
        torch.save(policy,policyPath)
        logging.info('保存value网络...')
        torch.save(value,valuePath)

def test(dataSet):
    engine=Xuan()
    accuracy=[]
    for i in range(len(dataSet)):
        sgf=dataSet[i]['sgf']
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
    with open(log_fileName,encoding='utf-8',mode='a+') as f:
        f.write(json.dumps({
            'type':'accuracy',
            'data':accuracy
        }))
        f.write('\n')
    logging.info('保存数据成功')

def train(dataSet:MyDataset,time:int,testDataSet:list):
    lr=float(config['ai'].get('LR',None))

    inplane=int(config['ai'].get('inplane',None))
    outplane=int(config['ai'].get('outplane',None))
    outPlaneMap=int(config['ai'].get('outPlaneMap',None))
    block=int(config['ai'].get('BLOCK',None))
    ADAM=int(config['ai'].get('ADAM',None))
    L2_REG=float(config['ai'].get('L2_REG',None))
    MOMENTUM=float(config['ai'].get('MOMENTUM',None))
    EPOCH=float(config['ai'].get('EPOCH',None))

    if osType!='Windows' and EPOCH>4:
        EPOCH=4

    criterion=Loss()
    feature,policy,value=loadModel(inplane,outplane,outPlaneMap,block)
    dataLoader=DataLoader(dataSet,batch_size=batchSize,collate_fn=collateFn,shuffle=True,num_workers=5,drop_last=True)
    jointParams=list(feature.parameters())+list(policy.parameters())+list(value.parameters())

    optimizer=torch.optim.Adam(jointParams,lr=lr) if ADAM ==1 else torch.optim.SGD(jointParams,lr=lr,weight_decay=L2_REG,momentum=MOMENTUM)

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
            logging.info( "当前epoch=[%d] 共[%d]个,index=[%d] 到[%d]结束训练 批次loss=%d,time=%d"
                          %(i+1,EPOCH,batchID+1,time,numpy.mean(singleLoss),getDatetime()['timeformat']))
        logging.info("训练完一个epoch,开始测试")
        try:
            test(testDataSet)
        except Exception as e:
            logging.error("测试出现错误->%s"%e)
        logging.info("Average backward pass->{}".format(numpy.mean(batchLoss)))
        epochLoss.append(numpy.mean(batchLoss))
        logging.info("Epoch loss:{}".format(epochLoss))
        with open(log_fileName,encoding='utf-8',mode='a+') as f:
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
    myDataSet=MyDataset(trainData)
    train(myDataSet,int(len(trainData)/batchSize),testData)
    endtime=getDatetime()['timeformat']
    logging.info("训练完毕,开始时间:%s,结束时间:%s"%(begintime,endtime))