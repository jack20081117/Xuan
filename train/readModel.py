import sqlite3,sys,os,logging
from src.go import Go
from ai.datacenter import DataCenter
from config import *
from config import GLOBAL_DICT as gl

config=CONFIG
port=config['tcp']['port']

dbpath=os.path.dirname(os.path.realpath(__file__))
gl['logpath']=dbpath
dbpath=os.path.join(dbpath,config['db']['filepath'])
gl['dbpath']=dbpath
gl['config']=config

dataCenter=DataCenter()

argv=sys.argv
file=argv[1]

def combine(data:str):
    lines=data.split('\n')
    result=''
    for i in range(len(lines)):
        result+=lines[i]
    return result

def saveFile(fileName,need):
    select=dataCenter.checkFileName(fileName)
    select=select[0]
    if int(select['count']):
        logging.info("该文件=[%s]已被解析过"%fileName)
        dataCenter.vaccum()
        if need is True:
            return None
        exit(0)
    logging.info("正在解析%s"%fileName)
    go=Go()
    with open(fileName,'r',encoding='UTF-8') as f:
        try:
            line=f.read()
        except UnicodeError:
            logging.error("文件编码错误!")
            return None
        if need is True:
            line=combine(line)
        line=line.split('\n')
        if len(argv)>3:
            logging.info("大概有%d行数据"%len(line))
            exit(0)
        for i in range(len(line)):
            logging.info("正在处理:%d"%i)
            sgf=line[i]
            if len(sgf)<10:continue
            additional=go.parseAdditionalSgf(sgf)
            logging.info('additional:{}'.format(additional))
            try:
                dataCenter.saveGoban(sgf,additional)
            except sqlite3.IntegrityError:
                logging.error("主键冲突 棋谱已经存在")
            except sqlite3.OperationalError:
                logging.error("出现错误")
        logging.info("文件解析完毕 保存解析记录...")
        dataCenter.saveCheckedName(fileName)

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