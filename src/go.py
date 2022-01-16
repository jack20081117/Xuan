from src.tools import *
from config import *

import numpy,logging,json,copy
logging.basicConfig(level=logging.INFO)

class Go(object):
    def __init__(self):
        self.board=getEmptyBoard()
        self.string=getEmptyString()
        self.robX=None#当前打劫点的x坐标
        self.robY=None#当前打劫点的y坐标
        self.isBlack=True#当前是否为黑方执子

    def setBoard(self,data):
        self.board=data

    def getStringInfo(self,x,y):#返回(x,y)点所在的棋串编号
        #越界 刚才的点在边界
        if x<0 or x>18 or y<0 or y>18:
            return -1

        #目前是黑在下 但这个点返回的是空或者白
        color=1 if self.isBlack else -1
        if self.board[x][y]!=color:
            return False

        subString=self.string['black'] if self.isBlack else self.string['white']
        logging.info("get string info:x=%d,y=%d"%(x,y))
        if x in subString and y in subString[x]:
            num=subString[x][y]
            return num
        return True

    @staticmethod
    def getSrcString(*args):
        for s in args:
            if s>0 and not isinstance(s,bool):
                return s

    def combineCurrentString(self,x,y,src,*args):
        logging.info("combine current string 处理前 string:",self.string)
        subString=self.string['black'] if self.isBlack else self.string['white']
        if x not in subString:
            subString[x]={}
        subString[x][y]=src
        subString[src].append({'x':x,'y':y})
        for s in args:
            if s>0 and s!=src and not isinstance(s,bool):
                if s in subString:
                    subString[src].extend(subString[s])
                    for key in subString:
                        if key<19:
                            for subkey in subString[key]:
                                if subString[key][subkey]==s:
                                    subString[key][subkey]=src
                    logging.info("即将删除棋串%s"%subString[s])
                    del subString[s]

    def combine(self,x,y):
        up,down,left,right=getFourDirect(x,y)

        logging.info('get string info...')
        su=self.getStringInfo(up['x'],up['y'])
        sd=self.getStringInfo(down['x'],down['y'])
        sl=self.getStringInfo(left['x'],left['y'])
        sr=self.getStringInfo(right['x'],right['y'])
        logging.info('su={},sd={},sl={},sr={}'.format(su,sd,sl,sr))

        if (su==False or su==-1)\
        and(sd==False or sd==-1)\
        and(sl==False or sl==-1)\
        and(sr==False or sr==-1):
            logging.info('combine 检测到需要新增string:',self.string)
            stringNum=self.string['num']
            subString=self.string['black'] if self.isBlack else self.string['white']
            if x not in subString:
                subString[x]={}
            if stringNum not in subString:
                subString[stringNum]=[]
            subString[x][y]=stringNum
            subString[stringNum].append({'x':x,'y':y})
            self.string['num']+=1
            logging.info('combine result:%s'%self.string)
        else:
            logging.info('combine 检测到需要合并string:',self.string)
            src=self.getSrcString(su,sd,sl,sr)
            self.combineCurrentString(x,y,src,su,sd,sl,sr)
            logging.info('combine result:%s'%self.string)
        return None

    def doStep(self,x,y):
        if x<0 or x>18 or y<0 or y>18:
            raise Exception('x,y must be in [0,18]!')
        num=1 if self.isBlack else -1
        self.board[x][y]=num

    def checkStep(self,x,y):
        if self.board[x][y]:
            logging.error('不能在已有棋子的位置落子!')
            return False
        return True

    def doKill(self,x,y,flag):
        logging.info('kill string:%s'%self.string)
        directs=getFourDirect(x,y)
        killed=[]
        for direct in directs:
            if 0<=direct['x']<19 and 0<=direct['y']<19:
                if self.board[direct['x']][direct['y']]==flag:
                    res=self.checkKill(x,y,flag)
                    if res:
                        killed.append(res)
        return killed

    def checkKill(self,x,y,flag):
        color='black' if flag==1 else 'white'
        subString=self.string[color]
        num=subString[x][y]
        logging.info('check kill 检查的棋串为:%d'%num)
        L=subString[num]#棋串

        for i in range(len(L)):
            x=L[i]['x']
            y=L[i]['y']
            directs=getFourDirect(x,y)

            for direct in directs:
                if 0<=direct['x']<19 and 0<=direct['y']<19:
                    if not self.board[direct['x']][direct['y']]:
                        logging.info('棋串%d为活棋'%num)
                        return False

        logging.info('棋串%d为死棋'%num)
        return num

    def cleanString(self,num):
        logging.info('clean string 正在删除棋串:%d'%num)
        if num in self.string['black']: color='black'
        elif num in self.string['white']: color='white'
        else: return []
        killed=[]
        subString=self.string[color]
        L=subString[num]
        if L is None:
            logging.info('棋串%d已被杀死'%num)
            return []
        for i in range(len(L)):
            x,y=L[i]['x'],L[i]['y']
            self.board[x][y]=0#将棋串中所有棋子标记为0
            if y in subString[x]:
                subString[x].pop(y)
                killed.append({'x':x,'y':y})
        return killed

    def checkSuicide(self,x,y):
        color='black' if self.board[x][y]==1 else 'white'
        subString=self.string[color]
        num=subString[x][y]
        L=subString[num]
        for i in range(len(L)-1,-1,-1):
            if L[i]['x']==x and L[i]['y']==y:
                del L[i]
                break
        self.board[x][y]=0
        subString['x'].pop('y')

    @staticmethod
    def transferBoard(board,src,target):
        for i in range(19):
            for j in range(19):
                if board[i][j]==src:
                    board[i][j]=target
        return board

    def transferSgf2StringAndBoard(self,sgfData):
        self.__init__()
        data=self.parseSgf(sgfData)
        for i in range(len(data)):
            singleData=data[i]
            x,y,color=singleData['x'],singleData['y'],singleData['color']
            logging.info('目前是第%d步棋,x=%d,y=%d,color=%s'%(i+1,x,y,color))
            self.simpleGoLogic(x,y,color)
        logging.info('board->%s'%self.board)
        logging.info('string->%s'%self.string)

    def transferBoard2String(self,board):
        self.__init__()
        string=None
        for i in range(19):
            for j in range(19):
                if board[i][j]:
                    self.isBlack=True if board[i][j]==1 else False
                    string=self.combine(i,j)
        if string is None:string=getEmptyString()
        return string

    @staticmethod
    def findBlank(board,cell):
        def _findBlank(board,result,cell):
            i,j=cell
            board[i,j]=9
            result['cross'].add(cell)
            if i>0:
                if not board[i-1,j]:
                    _findBlank(board,result,(i-1,j))
                if board[i-1,j]==1:
                    result['b_around'].add((i-1,j))
                if board[i-1,j]==2:
                    result['w_around'].add((i-1,j))
            if i<18:
                if not board[i+1,j]:
                    _findBlank(board,result,(i+1,j))
                if board[i+1,j]==1:
                    result['b_around'].add((i+1,j))
                if board[i+1,j]==2:
                    result['w_around'].add((i+1,j))
            if j>0:
                if not board[i,j-1]:
                    _findBlank(board,result,(i,j-1))
                if board[i,j-1]==1:
                    result['b_around'].add((i,j-1))
                if board[i,j-1]==2:
                    result['w_around'].add((i,j-1))
            if j<18:
                if not board[i,j+1]:
                    _findBlank(board,result,(i,j+1))
                if board[i,j+1]==1:
                    result['b_around'].add((i,j+1))
                if board[i,j+1]==2:
                    result['w_around'].add((i,j+1))

        result={'cross':set(),'b_around':set(),'w_around':set()}
        _findBlank(board,result,cell)
        return result

    def findBlanks(self,board):
        blanks=[]
        while True:
            cells=numpy.where(board==0)
            if not cells[0].size: break
            blanks.append(self.findBlank(board,(cells[0][0],cells[1][0])))
        return blanks

    def checkWinner(self,board):
        logging.info('checking winner...')
        board=self.transferBoard(board,-1,2)
        temp=numpy.copy(board)
        for item in self.findBlanks(numpy.copy(board)):
            if not len(item['w_around']) and not len(item['b_around']):
                value=9
            elif not len(item['w_around']):
                value=3
            elif not len(item['b_around']):
                value=4
            else:
                value=9
            for i,j in item['cross']:
                temp[i,j]=value

        black=temp[temp==1].size+temp[temp==3].size
        white=temp[temp==2].size+temp[temp==4].size
        common=temp[temp==9].size

        logging.info('black:%d,white:%d,common:%d'%(black,white,common))

        return {
            'black':black,
            'white':white,
            'common':common
        }

    @staticmethod
    def parseSgf(sgfData):
        #sgf文件格式 W为白 B为黑
        #类似B[ac];W[dp];...
        L=sgfData.split(';')
        result=[]
        for i in range(len(L)):
            step=L[i]
            if step[0] in COLOR_DICT and step[2] in ALPHABET and step[3] in ALPHABET:
                color=COLOR_DICT[step[0]]
                x=ALPHABET[step[2]]-1
                y=ALPHABET[step[3]]-1
                result.append({
                    "color":color,
                    "x":x,
                    "y":y
                })
        return result

    @staticmethod
    def parseAdditionalSgf(sgfData):
        RE=getSgfInfo(sgfData,'RE','')
        PB=getSgfInfo(sgfData,'PB','')
        PW=getSgfInfo(sgfData,'PW','')
        BR=getSgfInfo(sgfData,'BR','9d')
        WR=getSgfInfo(sgfData,'WR','9d')
        KM=getSgfInfo(sgfData,'KM','6.5')
        AP=getSgfInfo(sgfData,'AP','Xuan')
        DT=getSgfInfo(sgfData,'DT',getDatetime()['datestr'])
        RU=getSgfInfo(sgfData,'RU=','chinese')
        return {
            'RE':RE,'PB':PB,'PW':PW,'BR':BR,'WR':WR,
            'KM':KM,'AP':AP,'DT':DT,'RU':RU
        }

    @staticmethod
    def parseGoban2Sgf(gobanData):
        sgf=''
        for i in range(len(gobanData)):
            x=ALPHABET[int(gobanData[i]['x'])]
            y=ALPHABET[int(gobanData[i]['y'])]
            color=COLOR_DICT[int(gobanData[i]['color'])]
            temp='%s[%s%s];'%(color,x,y)
            sgf+=temp
        return {
            'raw':json.dumps(gobanData),
            'sgf':sgf
        }

    def parseSingleData(self,data):
        sgf=data['sgf']
        self.__init__()
        parsedSgf=self.parseSgf(sgf)
        additionalSgf=self.parseAdditionalSgf(sgf)
        goban=[]
        stringList=[]
        for i in range(len(parsedSgf)):
            x=parsedSgf[i]['x']
            y=parsedSgf[i]['y']
            color=parsedSgf[i]['color']
            success,board,string,robX,robY=self.GoLogic(x,y,color)
            goban.append(board)
            stringList.append(string)
        RE=additionalSgf['RE']
        if RE[0]!='W' and RE[0]!='B' and RE[0]!=UNKNOWN:
            RE[0]=UNKNOWN
        if RE!=UNKNOWN:
            winnerc=RE[0]
        else:
            latestGoban=copy.deepcopy(goban[-1])
            winResult=self.checkWinner(latestGoban)
            winnerc='B' if winResult['black']>winResult['white']+KOMI else 'W'
        winner=[WINNER[winnerc]]
        return goban,winner,parsedSgf,stringList

    def parseSgf2NetworkData(self,sgf):
        sgfDict={'sgf':sgf}
        return self.parseSingleData(sgfDict)

    def simpleGoLogic(self,x,y,color):
        #Xuan内部使用的围棋逻辑,即把传进来的坐标转为自己的棋盘信息
        #不需要判断自身死棋或者打劫 因为传进来的棋谱默认合法
        self.isBlack=True if color=='black' else False
        flag=1 if color=='black' else -1
        self.board[x][y]=flag
        self.combine(x,y)
        result=self.doKill(x,y,flag)
        if len(result)>0:
            for i in range(len(result)):
                self.cleanString(result[i])

    def returnData(self,success):
        return success,self.board,self.string,self.robX,self.robY

    def GoLogic(self,x,y,color):#完整的围棋逻辑
        #先做好备份 防止出现要类似悔棋的逻辑
        backupBoard=copy.deepcopy(self.board)
        backupString=copy.deepcopy(self.string)
        backupRobX,backupRobY=self.robX,self.robY
        checkStep=self.checkStep(x,y)
        if not checkStep:
            return self.returnData(False)
        #判断自杀逻辑是反过来的
        if color=='black':
            self.isBlack=True
            selfKillflag=1
            killFlag=-1
        else:
            self.isBlack=False
            selfKillflag=-1
            killFlag=1
        self.board[x][y]=selfKillflag
        self.combine(x,y)
        result=self.doKill(x,y,killFlag)
        if len(result):
            for i in range(len(result)):
                killed=self.cleanString(result[i])
                if len(killed)==1:
                    #在这里判断打劫
                    logging.info('GoLogic正在判断打劫,robX=%d,robY=%d,x=%d,y=%d'%(self.robX,self.robY,x,y))
                    if self.robX is not None\
                    and self.robY is not None\
                    and int(self.robX)==int(x)\
                    and int(self.robY)==int(y):
                        logging.error('无法在打劫点落子!')
                        logging.error('GoLogic校验失败!')
                        self.board=backupBoard
                        self.string=backupString
                        return self.returnData(False)
                    self.robX=killed[0]['x']
                    self.robY=killed[0]['y']
                    logging.info('保存了目前打劫点:x=%d,y=%d'%(self.robX,self.robY))
                else:
                    self.robX=None
                    self.robY=None
        else:
            selfResult=self.checkKill(x,y,selfKillflag)
            if selfResult:
                self.board=backupBoard
                self.string=backupString
                self.robX=backupRobX
                self.robY=backupRobY
                logging.error('GoLogic校验失败!')
                return self.returnData(False)
        logging.info('GoLogic校验成功!')
        return self.returnData(True)

    def getLastBoard(self,boardList,index,myColor,oppoColor):
        myLast=[]
        oppoLast=[]
        start=index-7
        for i in range(7):
            if start<0 or start>len(boardList):
                empty=getEmptyBoard()
                myLast.append(empty)
                oppoLast.append(empty)
            else:
                currentBoard=boardList[start]
                myBoard=self.setBoardByColor(copy.deepcopy(currentBoard),myColor)
                oppoBoard=self.setBoardByColor(copy.deepcopy(currentBoard),oppoColor)
                myLast.append(myBoard)
                oppoLast.append(oppoBoard)
            start+=1
        return myLast,oppoLast

    @staticmethod
    def getDotLife(x,y,board):
        if x<0 or x>18 or y<0 or y>18:
            return 0
        return 1 if not board[x][y] else 0

    def getStringLife(self,board,L,threshold=4):
        life=0
        for i in range(len(L)):
            x=L[i]['x']
            y=L[i]['y']
            directs=getFourDirect(x,y)
            for direct in directs:
                life+=self.getDotLife(direct['x'],direct['y'],board)
        return life if life<threshold else -1

    def getBoardAddition(self,board,string,color):
        myBoard=copy.deepcopy(board)
        oppoBoard=copy.deepcopy(board)
        myLifeBoard=[getEmptyBoard(),getEmptyBoard(),getEmptyBoard()]
        oppoLifeBoard=[getEmptyBoard(),getEmptyBoard(),getEmptyBoard()]
        myColor=1
        oppoColor=-1
        if color==1:
            myColorText='white'
            oppoColorText='black'
        else:
            myColorText='black'
            oppoColorText='white'
        for i in range(19):
            for j in range(19):
                if board[i][j]!=color and board[i][j]:
                    myBoard[i][j]=0
                if board[i][j]==color:
                    oppoBoard[i][j]=0
        myString=copy.deepcopy(string[myColorText])
        oppoString=copy.deepcopy(string[oppoColorText])
        myArray=[[],[],[]]
        oppoArray=[[],[],[]]
        for key in myString:
            if int(key)<19: continue
            array=myString[key]
            life=self.getStringLife(board,array)
            if life==-1: continue
            if life==1:
                myArray[0].append(array)
            if life==2:
                myArray[1].append(array)
            if life==3:
                myArray[2].append(array)
        for key in oppoString:
            if int(key)<19: continue
            array=oppoString[key]
            life=self.getStringLife(board,array)
            if life==-1: continue
            if life==1:
                oppoArray[0].append(array)
            if life==2:
                oppoArray[1].append(array)
            if life==3:
                oppoArray[2].append(array)
        for k in range(3):
            myLifeBoard[k]=self.setBoardByArray(myLifeBoard[k],myArray[k],myColor)
            oppoLifeBoard[k]=self.setBoardByArray(oppoLifeBoard[k],oppoArray[k],oppoColor)
        return myBoard,oppoBoard,myLifeBoard,oppoLifeBoard

    @staticmethod
    def setBoardByArray(board,array,color):
        for i in range(len(array)):
            x=array[i]['x']
            y=array[i]['y']
            board[x][y]=color
        return board

    @staticmethod
    def setBoardByColor(board,color):
        for i in range(19):
            for j in range(19):
                if board[i][j]!=color:
                    board[i][j]=0
        return board

    @staticmethod
    def getColorNumByText(text):
        return 1 if text=='black' else 0

    @staticmethod
    def getColorTextByNum(num):
        return 'black' if num==1 else 'white'

    def getCurrentColorBoard(self,num):
        board=getEmptyBoard()
        for i in range(19):
            for j in range(19):
                board[i][j]=num
        return board

    @staticmethod
    def getMyOppoBoard(board,mycolor,oppocolor):
        myboard=copy.deepcopy(board)
        oppoboard=copy.deepcopy(board)
        for i in range(19):
            for j in range(19):
                myboard[i][j]=1 if myboard[i][j]==mycolor else 0
                oppoboard[i][j]=1 if oppoboard[i][j]==oppocolor else 0
        return myboard,oppoboard