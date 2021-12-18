import sqlite3,sys,os,json,configparser,logging
from src.go import Go
from ai.datacenter import DataCenter
from config import GLOBAL_DICT as gl

fileName='./config.ini'

config=configparser.ConfigParser()
config.read(fileName)
port=config['tcp']['port']

dbpath=os.path.dirname(os.path.realpath(__file__))
gl['logpath']=dbpath
dbpath=os.path.join(dbpath,config['db']['filepath'])
gl['dbpath']=dbpath
gl['config']=config

dataCenter=DataCenter()

argv=sys.argv
file=argv[1]

def saveFile(fileName,need):
    select=dataCenter.checkFileName(fileName)
    select=select[0]

if file=='del' or file=='delete':
    delete=input("即将删除所有围棋训练数据 输入[delete]以确认:\n")
    if delete=='delete':
        dataCenter.deleteGoData('xuan')
        logging.info("已删除所有数据")
    else:
        logging.info("已取消删除")
    exit(0)

if file=='count':
    count=dataCenter.countGoData()
    count=count[0]
    logging.info("目前数据库已有{}个棋谱".format(count['count']))
    exit(0)

try:
    dirs=os.listdir(file)
    for single in range(len(dirs)):
        dirs[single]=file+'/'+dirs[single]
        saveFile(dirs[single],True)
except NotADirectoryError:
    logging.info('检测到文件')
    saveFile(file,False)

logging.info("程序处理完毕")
dataCenter.vaccum()