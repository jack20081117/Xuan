from database.db import Database
from database.sql import *
from src.utils import *
from config import GLOBAL_DICT as gl
import hashlib,sqlite3,logging

class DataCenter(object):
    database=None
    model=None

    def __init__(self):
        self.database=Database()
        self.model=gl.get('model',None)

    def getGoban(self):
        sql=selectGoData
        data=self.database.select(sql)
        return data

    def saveGoban(self,sgf,additional):
        createtime=getDatetime()['timestr']
        black=additional['PB']
        white=additional['PW']
        hash=getHash(sgf)
        sql=insertGoData.format(sgf,black,white,createtime,hash)
        self.database.execute(sql)
        return {
            'code':0,
            'message':'成功保存棋谱'
        }

    def checkFileName(self,name):
        sql=selectCountFileRead.format(name)
        data=self.database.select(sql)
        return {'count':data}

    def countGoData(self):
        sql=selectCountGoData
        data=self.database.select(sql)
        return {'count':data}

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
            logging.error('未配置%s数据库地址'%name)
            return []
        self.database.init(path)
        result=self.database.select(selectGoData)
        return result

    def getAllDataSet(self):
        result=[]
        result.extend(self.getModelByName('current'))
        # result.extend(self.getModelByName('old'))
        # result.extend(self.getModelByName('Tom'))
        # result.extend(self.getModelByName('ai'))
        logging.info('总计%d条数据'%len(result))
        return result