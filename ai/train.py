import json,os,logging
logging.basicConfig(level=logging.INFO)
from tqdm import tqdm
from src.go import Go
from src.utils import *
from ai.datacenter import DataCenter
import random
import tensorflow as tf
import numpy as np
import platform
from keras.models import load_model,Sequential
from config import GLOBAL_DICT as gl
from config import CONFIG as config
from ai.policy import Policy
from ai.value import Value

os_type=platform.system()

logFileName='./saved_model/train_data.txt'

batchSize=int(config['ai'].get('BATCHSIZE',32))

check_point=0
go=Go()

# 模型文件地址
Path=config['model'].get('')
policyPath=config['model'].get('policy')
valuePath=config['model'].get('value')

# 获取数据集
def getDataSet()->list:

    datacenter=DataCenter()

    allData=datacenter.getAllDataSet()
    return allData


# 如何组成训练数据
def collate_fn(example:list) -> tuple:
    state=[]
    winnerList=[]
    probasList=[]

    for i in tqdm(range(len(example))):
        single=example[i][0]

        goban,winner,parsedSgf,stringList=go.parseSgf2NetworkData(single)
        for j in range(len(goban)-1):
            # 随机取棋盘的一块值
            rand=j

            winnerList.append(winner)

            currentDict=parsedSgf[rand]

            # 计算出下一手的位置
            next_dict=parsedSgf[rand+1]
            nextBoard=getEmptyBoard()
            next_x=next_dict['x']
            next_y=next_dict['y']
            nextBoard[next_x][next_y]=1

            currentString=stringList[rand]
            color=currentDict['color']

            currentBoard=goban[rand]
            # 上一手是黑下 那么引擎要关注白的局面，反之也是
            if color=='white':
                colorSetNum=0
                currentColor=-1
                oppoColor=1
            else:
                colorSetNum=1
                currentColor=1
                oppoColor=-1
            # myselfBoard, oppoBoard, my_1, my_2, my_3, oppo_1, oppo_2, oppo_3 \
            #     = go.getBoard_additional(board=goban[rand], string=currentString, color=color)
            myLast,oppoLast=go.getLastBoard(goban,j,1,1)
            # 取了当前局面

            # 将原生的棋盘数据 抽成 将来落子方的棋盘 对手方的棋盘，其他位置全0处理
            myselfBoard,oppoBoard=go.getMyOppoBoard(currentBoard,currentColor,oppoColor)

            colorBoard=go.getCurrentColorBoard(colorSetNum)
            #
            # my_res = [myselfBoard]
            # my_res.extend(myLast)
            # my_res.append(my_1)
            # my_res.append(my_2)
            # my_res.append(my_3)
            # oppo_res = [oppoBoard]
            # oppo_res.extend(oppoLast)
            # oppo_res.append(oppo_1)
            # oppo_res.append(oppo_2)
            # oppo_res.append(oppo_3)
            #
            # my_res.extend(oppo_res)
            # my_res.append(colorBoard)

            myRes=[myselfBoard,oppoBoard,colorBoard]
            myRes.extend(myLast)
            myRes.extend(oppoLast)

            state.append(np.array(myRes))
            # 预测的结果 其他全是0 只有下一手的位置是1
            probasList.append(nextBoard.reshape(-1))
    state=np.array(state)
    state=np.transpose(state,(0,2,3,1))
    winnerList=np.array(winnerList)
    probasList=np.array(probasList)
    logging.info('state shape:%s'%str(state.shape))
    logging.info('winner shape:%s'%str(winnerList.shape))
    logging.info('probas shape:%s'%str(probasList.shape))

    return state,winnerList,probasList


# 加载模型 或者重建
def loadModel(inplane,outplane) -> tuple:
    try:
        policy=load_model(policyPath)
        value=load_model(valuePath)
        print("从权重文件读取网络成功")

    except Exception as e:
        print("重建神经网络 原因 ->",e)
        policy=Policy(inplane,outplane).model
        value=Value(inplane).model
        saveModel(policy,value)
    policy.summary()
    value.summary()
    return policy,value


# 保存模型
def saveModel(policy,value):
    try:
        time=getDatetime()['timestr']
        os.mkdir('../saved_model/'+time)
        print("保存policy网络...")
        policy.save('../saved_model/'+time+'/policy.h5')
        print("保存value网络...")
        value.save('../saved_model/'+time+'/value.h5')
        # 一定要保存一个最新的 不然每次都……
        print("保存最新policy网络...")
        policy.save(policyPath)
        print("保存最新value网络...")
        value.save(valuePath)
    except Exception as e:
        # 保存到目录失败 那就只存最新的
        print("保存神经网络失败->",e)
        print("保存policy网络...")
        policy.save(policyPath)
        print("保存value网络...")
        value.save(valuePath)


# 训练的主函数
def train(trainData,testData):
    # 获取CNN的通道数 记得一定要转成int
    inplane=int(config['ai'].get('inplane'))
    outplane=int(config['ai'].get('outplane'))
    EPOCH=int(config['ai'].get('EPOCH'))

    # 不是win10 就跑3个epoch 时间也得花很多了
    # Mac跑一个epoch大概2小时
    if os_type!='Windows' and EPOCH>4:
        EPOCH=4

    policy,value=loadModel(inplane,outplane)
    
    state,winnerList,probasList=collate_fn(trainData)
    
    # 开始训练
    logging.info("共{}个epoch".format(EPOCH))
    try:
        logging.info('policy训练中......')
        policy.fit(
            state,
            probasList,
            batch_size=max(batchSize,1),
            epochs=EPOCH,
            validation_split=0.2
        )

        logging.info('value训练中......')
        value.fit(
            state,
            winnerList,
            batch_size=max(batchSize,1),
            epochs=EPOCH,
            validation_split=0.2
        )
    except Exception as e:
        logging.error(e)
    finally:
        saveModel(policy=policy,value=value)


# 测试模块
def test(testData):
    pass


if __name__=='__main__':
    begin=getDatetime()['timeformat']
    print("训练开始时间 ->",begin)
    data=getDataSet()
    trainData=data[0:int(batchSize*100)]


    # 随便搞点测试数据
    # 可以单独搞个测试函数去使用

    # 10盘棋足够了
    testData=data[int(batchSize*105):int(batchSize*105)+5]
    # test(test_data)
    logging.info("共{}个batch".format(int(len(trainData)/batchSize)))
    train(trainData,testData)
    print("正常训练完毕")
    end=getDatetime()['timeformat']

    print("训练结束时间->{}".format(end))
