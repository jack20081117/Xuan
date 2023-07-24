# 损失计算器

import torch
from torch.nn.modules.module import Module

class Loss(Module):
    def __init__(self):
        super(Loss,self).__init__()

    @staticmethod
    def forward(winner,selfPlayWinner,probas,selfPlayProbas):
        valueError=(selfPlayWinner-winner)**2
        policyError=torch.sum((-selfPlayProbas*(1e-6+probas).log()),1)
        totalError=(valueError.view(-1)+policyError).mean()
        return totalError