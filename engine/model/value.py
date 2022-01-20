#评价器

import torch
import torch.nn as nn
import torch.nn.functional as functional
from torch.nn.modules.module import Module

class ValueNet(Module):
    '''
    This network is used to predict which player is more likely to win given the input 'state'
    described in the Feature Extractor model.
    The output is a continuous variable, between -1 and 1.
    '''
    def __init__(self,inplanes,outplanes):
        super(ValueNet,self).__init__()
        self.outplanes=outplanes
        self.conv=nn.Conv2d(inplanes,1,kernel_size=1)
        self.bn=nn.BatchNorm2d(1)
        self.fc1=nn.Linear(outplanes,256)
        self.fc2=nn.Linear(256,1)

    def forward(self,x):
        '''
        :param x:feature maps extracted from the state
        :return:probability of the current agent winning the game
                considering the actual state of the board
        '''
        x=functional.relu(self.bn(self.conv(x)))
        x=x.view(-1,self.outplanes)
        x=functional.relu(self.fc1(x))
        winning=torch.tanh(self.fc2(x))
        return winning