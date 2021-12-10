from database.db import Database
from database.sql import *
from src.tools import *
from src.config import *
import hashlib,sqlite3,logging

class DataCenter(object):
    database=None
    databasePath=None
    model=None

    def __init__(self):
        self.database=Database()
        self.databasePath=None
        self.model={}

    def getGoban(self):
        sql=selectGoData
        data=self.database.select(sql)
        return data

    def setGoban(self,sgf,additional):
        createtime=getDatetime()['timestr']
        black=additional['PB']
        white=additional['PW']
        sql=insertGoData.format(sgf,black,white,createtime)
        self.database.execute(sql)
        return {
            'code':0,
            'message':'成功保存棋谱'
        }

    def checkFileName(self,name):
        sql=selectFileRead.format(name)
        data=self.database.select(sql)
        return data

    def countGoData(self):
        sql=selectGoData
        data=self.database.select(sql)
        return data

    def saveCheckedName(self,name):
        sql=insertFileRead.format(name)
        data=self.database.execute(sql)
        return data

    def vaccum(self):
        self.database.execute(vacuum)

    def deleteGoData(self,password):
        if password=='xuan':
            self.database.execute(deleteGoData)
            self.database.execute(deleteFileRead)
            self.vaccum()

    def getModelByName(self,name):
        path=self.model.get(name,None)
        if path is None:
            logging.error('未配置%d数据库地址'%name)
            return []
        self.database.init(path)
        result=self.database.select(selectGoData)
        return result

    def getAllDataSet(self):
        result=[]
        result.extend(self.getModelByName('current'))
        logging.info('总计%d条数据'%len(result))
        return result