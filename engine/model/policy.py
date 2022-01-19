#策略器

import torch.nn as nn
import torch.nn.functional as functional
from torch.nn.modules.module import Module

class PolicyNet(Module):
    def __init__(self,inplanes,outplanes):
        super(PolicyNet,self).__init__()
        self.outplanes=outplanes
        self.conv=nn.Conv2d(inplanes,1,kernel_size=(1,))
        self.bn=nn.BatchNorm2d(1)
        self.logSoftMax=nn.LogSoftmax(dim=1)
        self.fc=nn.Linear(outplanes,outplanes)

    def forward(self,x):
        x=functional.relu(self.bn(self.conv(x)))
        x=x.view(-1,self.outplanes)
        x=self.fc(x)
        probas=self.logSoftMax(x).exp()
        return probas