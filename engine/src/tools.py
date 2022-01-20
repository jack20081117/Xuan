import hashlib,re
from datetime import datetime

def getEmptyBoard():
    return [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]

def getEmptyString():
    return {
        'black':{},
        'white':{},
        'num':19
    }

def getFourDirect(x,y):
    up={'x':x,'y':y+1}
    down={'x':x,'y':y-1}
    left={'x':x-1,'y':y}
    right={'x':x+1,'y':y}
    return up,down,left,right

def getHash(data):
    return hashlib.sha1(data.encode(encoding='UTF-8')).hexdigest()

def getSgfInfo(data,target,default):
    p=re.compile(r"{}\[(.*?)]".format(target),re.S)
    result=re.findall(p,data)
    if default=='':default='unknown'
    return default if not len(result) else result[0]

def getDatetime():
    timestamp=datetime.now()
    timestr=timestamp.strftime('%Y%m%d%H%M%S')
    timeformat=timestamp.strftime('%Y-%m-%d %H:%M:%S')
    datestr=timestamp.strftime('%Y-%m-%d')
    return {
        'timestr':timestr,
        'timeformat':timeformat,
        'datestr':datestr
    }