import configparser,json,os,logging
from src.tools import *
from src.net import Server
from config import GLOBAL_DICT as gl
from config import *

filePath='./config.ini'

def hello():
    print('''
    X     X
     X   X   U     U     A     N    N
      X X    U     U    A A    NN   N
       X     U     U   A   A   N N  N
      X X    U     U  A AAA A  N  N N
     X   X    U   U   A     A  N   NN
    X     X    UUU    A     A  N    N
    ''')
    print("This is Jack Zhang's AI architecture.")
    print("Copyright 2021-2025.All rights deserved.")

if __name__ == '__main__':
    config=CONFIG
    port=config['tcp']['port']

    dbpath=os.path.dirname(os.path.realpath(__file__))
    gl['logpath']=dbpath
    #dbpath=os.path.join(dbpath,config['db']['filepath'])
    #gl['dbpath']=dbpath
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
    gl['model_path']=config['model']

    if port is None:
        logging.warning('缺少端口号')
        raise Exception

    hello()
    net=Server()
    net.run(port)