#绘制训练结果

import json,os,numpy,logging
import matplotlib.pyplot as plt
from src.tools import *
from config import *

readFileName='./savedModel/trainData.txt'

config=CONFIG
LR=config['ai']['LR']
BATCHSIZE=config['ai']['BATCHSIZE']

def paint(allData):
    epochWinner=[]
    loss=[]
    accuracy=[]
    epoch=0
    lossMean=[]
    for i in range(len(allData)):
        singleData=allData[i]
        try:
            parsedData=json.loads(singleData)
        except Exception as e:
            logging.error("第%d行不是需要的数据，错误原因->%s"%(i+1,e))
            continue
        dataType=parsedData['type']
        data=parsedData['data']
        if dataType=='loss':
            loss.extend(data)
            lossMean.append(numpy.mean(data))
            epoch+=1
        elif dataType=='epochWinner':
            epochWinner.extend(data)
        elif dataType=='accuracy':
            for j in range(len(data)):
                singleData=data[j]
                percent=singleData['percent']
                accuracy.append(percent)

    plt.plot(loss)
    plt.ylabel('allLoss')
    plt.xlabel('LR={},BATCHSIZE={},epoch={}'.format(LR,BATCHSIZE,epoch))
    plt.show()
    plt.plot(lossMean)
    plt.ylabel('lossMean')
    plt.xlabel('LR={},BATCHSIZE={},epoch={}'.format(LR,BATCHSIZE,epoch))
    plt.show()
    plt.plot(epochWinner)
    plt.ylabel('allWinner')
    plt.xlabel('LR={},BATCHSIZE={},epoch={}'.format(LR,BATCHSIZE,epoch))
    plt.show()
    plt.plot(accuracy)
    plt.ylabel('allAccuracy')
    plt.xlabel('LR={},BATCHSIZE={},epoch={}'.format(LR,BATCHSIZE,epoch))
    plt.show()

    logging.info('allLoss :>> %s'%lossMean)
    decrease=[]
    for i in range(len(lossMean)-1):
        a,b=lossMean[i],lossMean[i+1]
        decrease.append(a-b)

    plt.plot(decrease)
    plt.ylabel('decrease')
    plt.xlabel('LR={},BATCHSIZE={},epoch={}'.format(LR,BATCHSIZE,epoch))
    plt.show()

if __name__ == '__main__':
    with open(readFileName,encoding='utf-8',mode='r') as f:
        allData=f.read()
        allData=allData.split('\n')
        paint(allData)