from config import *
from config import GLOBAL_DICT as gl
from src.tools import *
from src.go import Go
from src.net import Server
from database.db import Database
from ai.xuan import Xuan
from ai.mcts import MCTS
import json,logging

config=CONFIG
gl['ai']=config['ai']
gl['modelPath']=config['model']

mcts=MCTS()
go=Go()
engine=Xuan()

if __name__ == '__main__':
    goban=[]
    color=1
    num=1
    mcts.analyze(goban=goban)
    son=mcts.root.getSon()
    logging.info('son :>> %s'%son)