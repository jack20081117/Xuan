from config import *
from config import GLOBAL_DICT as gl
from src.go import Go
from ai.xuan import Xuan
from ai.mcts import MCTS
import logging,os

config=CONFIG
gl['ai']=config['ai']
gl['modelPath']=config['model']
dbpath=os.path.dirname(os.path.realpath(__file__))
dbpath=os.path.join(dbpath,config['db'].get('current',None))
gl['dbpath']=dbpath

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