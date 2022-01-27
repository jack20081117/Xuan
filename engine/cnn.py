import torch.nn as nn
import torch.nn.functional as functional
from torch.nn.modules.module import Module
from torch.utils.data import DataLoader
import torch,torchvision
import torch.optim as optim
import logging
from config import *

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
config=CONFIG
EPOCH=config['ai']['EPOCH']
NEPOCH=3
BATCHSIZETRAIN=100
BATCHSIZETEST=1000

MOMENTUM=0.5
LR=0.01

LOG_INTERNAL=10
RANDOM_SEED=1

torch.manual_seed(RANDOM_SEED)

class CNN(Module):
    def __init__(self):
        super(CNN,self).__init__()
        self.conv1=nn.Conv2d(1,10,kernel_size=5,padding=2)
        self.conv2=nn.Conv2d(10,20,kernel_size=5,padding=2)

        self.fc1=nn.Linear(20*28*28,500)
        self.fc2=nn.Linear(500,10)

    def forward(self,x):
        size=x.size(0)
        x=functional.relu(self.conv1(x))
        x=functional.relu(self.conv2(x))
        x=x.view(size,-1)
        x=self.fc1(x)
        x=self.fc2(x)
        x=functional.log_softmax(x,dim=1)
        return x

def train(model,device,trainLoader,optimizer,epoch):
    logging.info("开始训练")
    model.train()
    for batchIdx,(data,target) in enumerate(trainLoader):
        data,target=data.to(device),target.to(device)
        optimizer.zero_grad()
        output=model(data)
        loss=functional.cross_entropy(output,target)
        loss.backward()
        optimizer.step()
        if(batchIdx+1)%30==0:
            logging.info('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'
                         .format(epoch,batchIdx*len(data),len(trainLoader.dataset),
                         100.*batchIdx/len(trainLoader),loss.item()))

def test(model,device,testLoader):
    model.eval()
    testLoss=0
    correct=0
    with torch.no_grad():
        for data,target in testLoader:
            data,target=data.to(device),target.to(device)
            output=model(data)

            testLoss+=functional.nll_loss(output,target,reduction='sum')  # 将一批的损失相加
            pred=output.max(1,keepdim=True)[1]  # 找到概率最大的下标
            correct+=pred.eq(target.view_as(pred)).sum().item()
    testLoss/=len(testLoader.dataset)
    logging.info("\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%) \n"
                 .format(testLoss,correct,len(testLoader.dataset),
                 100.*correct/len(testLoader.dataset)))

if __name__ == '__main__':
    trainLoader=DataLoader(torchvision.datasets.MNIST('./mnist/',train=True,download=False,
                                                      transform=torchvision.transforms.Compose([
                                                          torchvision.transforms.ToTensor(),
                                                          torchvision.transforms.Normalize((0.1307,),(0.3081,))
                                                      ])),batch_size=BATCHSIZETRAIN,shuffle=True)
    testLoader=DataLoader(torchvision.datasets.MNIST('./mnist/',train=False,download=False,
                                                      transform=torchvision.transforms.Compose([
                                                          torchvision.transforms.ToTensor(),
                                                          torchvision.transforms.Normalize((0.1307,),(0.3081,))
                                                      ])),batch_size=BATCHSIZETEST,shuffle=True)
    examples=enumerate(testLoader)
    batchIdx,(exampleData,exampleTargets)=next(examples)
    network=CNN()
    model=network.to(DEVICE)
    optimizer=optim.SGD(model.parameters(),lr=LR,momentum=MOMENTUM)

    trainLosses=[]
    trainCounter=[]
    testLosses=[]

    for epoch in range(1,EPOCH+1):
        train(model,DEVICE,trainLoader,optimizer,epoch)
        test(model,DEVICE,testLoader)