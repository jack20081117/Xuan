import os,logging;logging.basicConfig(level=logging.INFO)
from src.utils import *
from config import GLOBAL_DICT as gl
from config import *

def hello():
    bless()
    print('''
    X     X
     XX XX   UU   UU     A     NN   N
      XXX    UU   UU    AAA    NNN  N
       X     UU   UU   AA AA   N NN N
      XXX    UU   UU  AAAAAAA  N NN N
     XX XX   UUU UUU  AA   AA  N  NNN
    X     X   UUUUU   AA   AA  N   NN
    ''')
    print("This is Jack Zhang's AI architecture.")
    print("Copyright 2021-2025.All rights deserved.")

if __name__ == '__main__':
    config=CONFIG
    port=config['tcp']['port']

    dbpath=os.path.dirname(os.path.realpath(__file__))
    gl['logpath']=dbpath
    old=os.path.join(dbpath,config['db'].get('old',None))
    current=os.path.join(dbpath,config['db'].get('current',None))
    ai=os.path.join(dbpath,config['db'].get('ai',None))
    Tom=os.path.join(dbpath,config['db'].get('Tom',None))

    model={
        'old':old,
        'current':current,
        'ai':ai,
        'Tom':Tom
    }

    gl['model']=model
    gl['ai']=config['ai']
    gl['modelPath']=config['model']