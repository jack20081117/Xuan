import configparser,os

BOARD_LENGTH=19

ALPHABET={
    'a':1,'b':2,'c':3,'d':4,'e':5,
    'f':6,'g':7,'h':8,'i':9,'j':10,
    'k':11,'l':12,'m':13,'n':14,'o':15,
    'p':16,'q':17,'r':18,'s':19,

    1:'a',2:'b',3:'c',4:'d',5:'e',
    6:'f',7:'g',8:'h',9:'i',10:'j',
    11:'k',12:'l',13:'m',14:'n',15:'o',
    16:'p',17:'q',18:'r',19:'s'
}

COLOR_DICT={
    -1:'W',1:'B',
    'W':'white',
    'B':'black'
}

BLACK=1
WHITE=-1
EMPTY=0

UNKNOWN='unknown'
DRAW='draw'

KOMI=6.5

WINNER={
    'B':1,
    'W':-1
}

GLOBAL_DICT={}

dbpath=os.path.dirname(os.path.realpath(__file__))
CONFIGFILEPATH=os.path.join(dbpath,'config.ini')

CONFIG=configparser.ConfigParser()
CONFIG.read(CONFIGFILEPATH,encoding='utf-8')

GLOBAL_DICT['logpath']=dbpath
old=os.path.join(dbpath,CONFIG['db'].get('old',None))
current=os.path.join(dbpath,CONFIG['db'].get('current',None))
ai=os.path.join(dbpath,CONFIG['db'].get('ai',None))
Tom=os.path.join(dbpath,CONFIG['db'].get('Tom',None))

model={
    'old':old,
    'current':current,
    'ai':ai,
    'Tom':Tom
}

GLOBAL_DICT['model']=model
GLOBAL_DICT['ai']=CONFIG['ai']
GLOBAL_DICT['modelPath']=CONFIG['model']