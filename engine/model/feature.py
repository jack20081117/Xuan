#提取器

import torch.nn as nn
import torch.nn.functional as functional
from torch.nn.modules.module import Module

class BasicBlock(Module):
    def __init__(self,inplanes,outplanes,configBlock,stride=1):
        super(BasicBlock,self).__init__()
        self.BLOCKS=configBlock
        self.conv1=nn.Conv2d(inplanes,outplanes,kernel_size=3,stride=stride,padding=1,bias=False)
        self.bn1=nn.BatchNorm2d(outplanes)
        self.conv2=nn.Conv2d(outplanes,outplanes,kernel_size=3,stride=stride,padding=1,bias=False)
        self.bn2=nn.BatchNorm2d(outplanes)

    def forward(self,x):
        residual=x
        output=x

        output=self.conv1(output)
        output=self.bn1(output)
        output=functional.relu(output)
        output=self.conv2(output)
        output=self.bn2(output)
        output=output+residual
        output=functional.relu(output)

        return output

class Extractor(Module):
    def __init__(self,inplanes,outplanes,configBlock):
        super(Extractor,self).__init__()
        self.BLOCKS=configBlock
        self.conv1=nn.Conv2d(inplanes,outplanes,stride=1,kernel_size=3,padding=1,bias=False)
        self.bn1=nn.BatchNorm2d(outplanes)
        for block in range(self.BLOCKS):
            setattr(self,'res{}'.format(block),BasicBlock(outplanes,outplanes,configBlock))

    def forward(self,x):
        '''
        :param x:tensor representing the state
        :return:result of the residual layers forward pass
        '''
        x=functional.relu(self.bn1(self.conv1(x)))
        for block in range(self.BLOCKS-1):
            basicBlock=getattr(self,"res{}".format(block))
            x=basicBlock(x)
        basicBlock=getattr(self,"res{}".format(self.BLOCKS-1))
        featureMaps=basicBlock(x)
        return featureMaps