import hashlib,re,numpy as np
from datetime import datetime

def getEmptyBoard():#返回19x19的空棋盘
    return np.zeros([19,19],dtype=np.int32)

def getEmptyString()->dict:#返回空的棋串
    return {
        'black':{},
        'white':{},
        'num':19
    }

def getFourDirect(x,y)->tuple:#返回点(x,y)上下左右四个点
    up={'x':x,'y':y+1}
    down={'x':x,'y':y-1}
    left={'x':x-1,'y':y}
    right={'x':x+1,'y':y}
    return up,down,left,right

def getHash(data)->str:#返回字符串的sha1值
    return hashlib.sha1(data.encode(encoding='UTF-8')).hexdigest()

def getSgfInfo(data,target,default)->str:#从sgf中找出有用的信息
    p=re.compile(r"{}\[(.*?)]".format(target),re.S)
    result=re.findall(p,data)
    if default=='':default='unknown'
    return default if not len(result) else result[0]

def getDatetime()->dict:#返回当前时间的三种形式
    timestamp=datetime.now()
    timestr=timestamp.strftime('%Y%m%d%H%M%S')
    timeformat=timestamp.strftime('%Y-%m-%d %H:%M:%S')
    datestr=timestamp.strftime('%Y-%m-%d')
    return {
        'timestr':timestr,
        'timeformat':timeformat,
        'datestr':datestr
    }

def loopFor2D(List:list[list]):#对一个二维数组(如棋盘)作处理
    return [item for subList in List for item in subList]

def bless():#神兽保佑我的代码没有BUG!
    print('''

       ┌─┐       ┌─┐
    ┌──┘ ┴───────┘ ┴──┐
    │   Jack  Zhang   │
    │                 │
    │  └┬┘       └┬┘  │
    │                 │
    │       ───       │
    │                 │
    └───┐         ┌───┘
        │         │
        │         │
        │         │
        │ X   X   └─────────────┐
        │  X X  u  u  aa   n  n │
        │   X   u  u a  a  nn n ├─┐
        │  X X  u  u aaaa  n nn ┌─┘
        │ X   X  uu  a  a  n  n │
        └─┐  ┐  ┌───────┬──┐  ┌─┘
          │ ─┤ ─┤       │ ─┤ ─┤
          └──┴──┘       └──┴──┘
    
    神兽保佑
    代码无BUG!
    ''')