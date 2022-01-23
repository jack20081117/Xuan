import hashlib,re
from datetime import datetime

def getEmptyBoard():
    return [
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0]
    ]

def getEmptyString():#这里就不按国际象棋的标准英文设置了,相信大家都看得懂
    return {
        'soldier':[],
        'elephant':[],
        'queen':[],
        'horse':[],
        'car':[],
        'king':[]
    }

def getHash(data):
    return hashlib.sha1(data.encode(encoding='UTF-8')).hexdigest()

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