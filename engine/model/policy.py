#策略器

import torch.nn as nn
import torch.nn.functional as functional
from torch.nn.modules.module import Module

class PolicyNet(Module):
    def __init__(self,inplanes,outplanes):
        super(PolicyNet,self).__init__()
        self.outplanes=outplanes
        self.conv=nn.Conv2d(inplanes,1,kernel_size=1)
        self.bn=nn.BatchNorm2d(1)
        self.logsoftmax=nn.LogSoftmax(dim=1)#加快运算效率,防止溢出
        self.fc=nn.Linear(outplanes,outplanes)

    def forward(self,x):#前向传播,求出梯度(这个函数应该是自己重写,torch自动调用)
        x=functional.relu(self.bn(self.conv(x)))
        x=x.view(-1,self.outplanes)
        x=self.fc(x)
        probas=self.logsoftmax(x).exp()
        return probas