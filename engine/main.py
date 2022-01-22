import os,logging
from src.net import Server
from config import GLOBAL_DICT as gl
from config import *

def hello():
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
    dbpath=os.path.join(dbpath,config['db']['filepath'])
    gl['dbpath']=dbpath
    old=os.path.join(dbpath,config['db'].get('old',None))
    current=os.path.join(dbpath,config['db'].get('current',None))
    ai=os.path.join(dbpath,config['db'].get('ai',None))
    Jack=os.path.join(dbpath,config['db'].get('Jack',None))

    model={
        'old':old,
        'current':current,
        'ai':ai,
        'Jack':Jack
    }

    gl['model']=model
    gl['ai']=config['ai']
    gl['modelPath']=config['model']

    if port is None:
        logging.warning('缺少端口号!')
        exit(1)

    hello()
    net=Server()
    net.run(port)