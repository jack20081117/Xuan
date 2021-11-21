from database.db import Database
from database.sql import *
from src.tools import *
from src.config import *
import hashlib,sqlite3

class DataCenter(object):
    database=None
    databasePath=None
    model=None

    def __init__(self):
        self.database=Database()
        self.databasePath=None
        self.model=None

    def getGoban(self):
        sql=selectGoData
        data=self.database.select(sql)
        return data

    def setGoban(self,sgf,additional):
        createtime=getDatetime()['timestr']
        black=additional['PB']
        white=additional['PW']
        sql=insertGoData.format(sgf,black,white)
        self.database.execute(sql)
        return {
            'code':0,
            'message':'成功保存棋谱'
        }