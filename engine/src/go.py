from src.tools import *
from config import *

import numpy,logging,json,copy
logging.basicConfig(level=logging.DEBUG)

class Go(object):
    board:list[list]=None#棋盘
    string:dict=None#棋串
    robX=None#打劫点X
    robY=None#打劫点Y
    isBlack:bool=True#目前是谁在走子(默认黑先)

    def __init__(self):
        self.board=getEmptyBoard()
        self.string=getEmptyString()
        self.robX=None#当前打劫点的x坐标
        self.robY=None#当前打劫点的y坐标
        self.isBlack=True#当前是否为黑方执子

    def setBoard(self,board:list[list]):#直接通过已有的棋盘克隆新棋盘
        '''
        :param board:old board
        '''
        self.board=board

    def getStringInfo(self,x:int,y:int)->int or bool:#返回(x,y)点所在的棋串编号
        '''
        :return:the number of the string where (x,y) is located
        '''
        #越界 点(x,y)在边界
        if x<0 or x>18 or y<0 or y>18:
            return -1

        #目前是黑在下 但这个点返回的是空或者白
        color=1 if self.isBlack else -1
        if self.board[x][y]!=color:
            return False

        subString=self.string['black'] if self.isBlack else self.string['white']
        logging.debug("get string info:x=%d,y=%d"%(x,y))
        if x in subString and y in subString[x]:
            num=subString[x][y]
            return num
        return True

    @staticmethod
    def getSrcString(*args)->int:
        for s in args:
            if s>0 and not isinstance(s,bool):
                return s

    def combineCurrentString(self,x:int,y:int,src:int,*args):#将(x,y)与四周的点所在棋串进行合并
        logging.debug("combine current string 处理前 string:",self.string)
        subString=self.string['black'] if self.isBlack else self.string['white']
        if x not in subString:
            subString[x]={}
        subString[x][y]=src
        subString[src].append({'x':x,'y':y})
        for s in args:
            if s>0 and s!=src and not isinstance(s,bool):
                if s in subString:
                    subString[src].extend(subString[s])#合并棋串
                    for key in subString:
                        if key<19:
                            for subkey in subString[key]:
                                if subString[key][subkey]==s:
                                    subString[key][subkey]=src
                    logging.debug("即将删除棋串%s"%subString[s])
                    del subString[s]

    def combine(self,x:int,y:int,isBlack=None):
        if isBlack is not None:self.isBlack=isBlack
        up,down,left,right=getFourDirect(x,y)

        logging.debug('get string info...')
        #获取四周的点的棋串编号
        su=self.getStringInfo(up['x'],up['y'])
        sd=self.getStringInfo(down['x'],down['y'])
        sl=self.getStringInfo(left['x'],left['y'])
        sr=self.getStringInfo(right['x'],right['y'])
        logging.debug('su={},sd={},sl={},sr={}'.format(su,sd,sl,sr))

        if (su is False or su==-1) and (sd is False or sd==-1) and (sl is False or sl==-1) and (sr is False or sr==-1):
            #四周都不是同色棋子,则新增了一个棋串
            logging.debug('combine 检测到需要新增string:',self.string)
            stringNum=self.string['num']
            subString=self.string['black'] if self.isBlack else self.string['white']
            if x not in subString:
                subString[x]={}
            if stringNum not in subString:
                subString[stringNum]=[]
            subString[x][y]=stringNum
            subString[stringNum].append({'x':x,'y':y})
            self.string['num']+=1
            logging.debug('combine result:%s'%self.string)
        else:
            logging.debug('combine 检测到需要合并string:',self.string)
            src=self.getSrcString(su,sd,sl,sr)
            self.combineCurrentString(x,y,src,su,sd,sl,sr)
            logging.debug('combine result:%s'%self.string)
        return None

    def doStep(self,x:int,y:int):#落子在(x,y)
        if x<0 or x>18 or y<0 or y>18:
            logging.debug('x,y must be in [0,18]!')
        num=1 if self.isBlack else -1
        self.board[x][y]=num

    def checkStep(self,x:int,y:int)->bool:#检查(x,y)是否已有棋子
        if x<0 or x>18 or y<0 or y>18:
            logging.debug('x,y must be in [0,18]!')
        if self.board[x][y]:
            logging.debug('不能在已有棋子的位置落子!')
            return False
        return True

    def doKill(self,x:int,y:int,flag:int)->list[int]:
        logging.debug('kill string:%s'%self.string)
        directs=getFourDirect(x,y)
        killed=[]
        for direct in directs:
            if 0<=direct['x']<19 and 0<=direct['y']<19:
                if self.board[direct['x']][direct['y']]==flag:
                    res=self.checkKill(direct['x'],direct['y'],flag)
                    if res is not False:
                        killed.append(res)
        return killed

    def checkKill(self,x:int,y:int,flag:int)->int or bool:
        color='black' if flag==1 else 'white'
        subString=self.string[color]
        num=subString[x][y]
        logging.debug('check kill 检查的棋串为:%d'%num)
        L=subString[num]#棋串

        for i in range(len(L)):
            x=L[i]['x']
            y=L[i]['y']
            directs=getFourDirect(x,y)

            for direct in directs:
                if 0<=direct['x']<19 and 0<=direct['y']<19:
                    if not self.board[direct['x']][direct['y']]:
                        logging.debug('棋串%d为活棋'%num)
                        return False

        logging.debug('棋串%d为死棋'%num)
        return num

    def cleanString(self,num:int)->list[dict]:#把编号为num的棋串从棋盘上删除
        logging.debug('clean string 正在删除棋串:%d'%num)
        if num in self.string['black']: color='black'
        elif num in self.string['white']: color='white'
        else: return []
        killed=[]
        subString=self.string[color]
        L:list[dict]=subString[num]
        if L is None:
            logging.debug('棋串%d已被杀死'%num)
            return []
        for i in range(len(L)):
            x:int=L[i]['x']
            y:int=L[i]['y']
            self.board[x][y]=0#将棋串中所有棋子标记为0
            if y in subString[x]:
                subString[x].pop(y)
                killed.append({'x':x,'y':y})
        return killed

    def checkSuicide(self,x:int,y:int):
        color='black' if self.board[x][y]==1 else 'white'
        subString=self.string[color]
        num=subString[x][y]
        L=subString[num]
        for i in range(len(L)-1,-1,-1):
            if L[i]['x']==x and L[i]['y']==y:
                del L[i]
                break
        self.board[x][y]=0
        subString[x].pop(y)

    @staticmethod
    def transferBoard(board:list[list],src:int,target:int)->list[list]:
        '''
        :param board:the old board
        :param src:the source color,like -1
        :param target:the target color like 2
        :return:the new board
        '''
        for i in range(19):
            for j in range(19):
                if board[i][j]==src:
                    board[i][j]=target
        return board

    def transferSgf2StringAndBoard(self,sgfData:str):
        self.__init__()
        data=self.parseSgf2Goban(sgfData)
        for i in range(len(data)):
            singleData=data[i]
            x,y,color=singleData['x'],singleData['y'],singleData['color']
            logging.debug('目前是第%d步棋,x=%d,y=%d,color=%s'%(i+1,x,y,color))
            self.simpleGoLogic(x,y,color)
        logging.debug('board->%s'%self.board)
        logging.debug('string->%s'%self.string)

    def transferBoard2String(self,board:list[list])->dict:
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
    def findBlank(board,cell:tuple)->dict:
        def _findBlank(board,result:dict,cell:tuple):
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

    def findBlanks(self,board)->list[dict]:
        blanks=[]
        while True:
            cells=numpy.where(board==0)
            if not cells[0].size: break
            blanks.append(self.findBlank(board=board,cell=(cells[0][0],cells[1][0])))
        return blanks

    def checkWinner(self,board)->dict:
        logging.debug('checking winner...')
        board=self.transferBoard(board,-1,2)
        npBoard=numpy.copy(board)
        for item in self.findBlanks(numpy.copy(board)):
            if not len(item['w_around']) and not len(item['b_around']):value=9
            elif not len(item['w_around']):value=3
            elif not len(item['b_around']):value=4
            else:value=9
            for i,j in item['cross']:
                npBoard[i,j]=value

        black=npBoard[npBoard==1].size+npBoard[npBoard==3].size
        white=npBoard[npBoard==2].size+npBoard[npBoard==4].size
        common=npBoard[npBoard==9].size

        logging.debug('black:%d,white:%d,common:%d'%(black,white,common))

        return {
            'black':black,
            'white':white,
            'common':common
        }

    @staticmethod
    def parseSgf2Goban(sgfData:str)->list:#解析围棋的sgf文件格式,把方便入库的信息(Sgf)保存成Xuan能识别的棋谱信息(Goban)
        #sgf文件格式 W为白 B为黑
        #类似(;B[ac];W[dp];...)
        #代表黑 第一行 第三列;白 第四行 第十六列
        L=sgfData.split(';')
        result=[]
        for i in range(len(L)):
            step=L[i]
            if step[0] in COLOR_DICT and step[2] in ALPHABET and step[3] in ALPHABET:
                color=COLOR_DICT[step[0]]
                x=ALPHABET[step[2]]-1#Goban的x,y坐标为0-18,需要减1
                y=ALPHABET[step[3]]-1
                result.append({
                    "color":color,
                    "x":x,
                    "y":y
                })
        return result

    @staticmethod
    def parseAdditionalSgf(sgfData:str)->dict:#解析sgf的额外信息
        RE=getSgfInfo(sgfData,'RE','')#游戏结果
        PB=getSgfInfo(sgfData,'PB','')#黑方
        PW=getSgfInfo(sgfData,'PW','')#白方
        BR=getSgfInfo(sgfData,'BR','9d')#黑方段位,默认职业九段
        WR=getSgfInfo(sgfData,'WR','9d')#白方段位,默认职业九段
        KM=getSgfInfo(sgfData,'KM','6.5')#贴目,默认6.5目
        AP=getSgfInfo(sgfData,'AP','Xuan')#对弈平台,默认为Xuan
        DT=getSgfInfo(sgfData,'DT',getDatetime()['datestr'])#对弈时间
        RU=getSgfInfo(sgfData,'RU=','chinese')#围棋规则,默认中国规则(黑贴6.5子)
        return {
            'RE':RE,'PB':PB,'PW':PW,'BR':BR,'WR':WR,
            'KM':KM,'AP':AP,'DT':DT,'RU':RU
        }

    @staticmethod
    def parseGoban2Sgf(gobanData:list[dict])->dict:#把Xuan能识别的棋谱信息(Goban)保存成方便入库的信息(Sgf)
        sgf=''
        for i in range(len(gobanData)):
            x=ALPHABET[int(gobanData[i]['x'])+1]#Sgf的x,y坐标为a-s,对应1-19,查询时需要加1
            y=ALPHABET[int(gobanData[i]['y'])+1]
            color=COLOR_DICT[int(gobanData[i]['color'])]
            temp='%s[%s%s];'%(color,x,y)
            sgf+=temp
        return {
            'raw':json.dumps(gobanData),
            'sgf':sgf
        }

    def parseSingleData(self,data:dict)->tuple[list,list,list,list]:#解析数据集传来的Sgf
        sgf=data['sgf']
        if isinstance(sgf,tuple):sgf=sgf[0]
        #每次清除围棋类的数据,很重要
        self.__init__()
        parsedSgf=self.parseSgf2Goban(sgf)
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
        RE=additionalSgf['RE']#游戏结果
        if RE[0]!='W' and RE[0]!='B' and RE!=UNKNOWN:#棋谱记录了胜者就赋值,没有的话就自己计算
            #出现了平局,这只有ai对局或者特殊情况才会出现,那就自己计算
            RE=UNKNOWN
        if RE!=UNKNOWN:
            winner=RE[0]
        else:
            #取出最近一次的棋盘状态 丢给go分析胜率
            latestGoban=copy.deepcopy(goban[-1])
            winResult=self.checkWinner(latestGoban)
            winner='B' if winResult['black']>winResult['white']+KOMI else 'W'#黑目比白目+贴目还多,就是黑胜,否则白胜
        winner=[WINNER[winner]]
        return goban,winner,parsedSgf,stringList

    def parseSgf2NetworkData(self,sgf:str)->tuple[list,list,list,list]:#把单个sgf转为神经网络需要的数据
        sgfDict={'sgf':sgf}
        return self.parseSingleData(sgfDict)

    def simpleGoLogic(self,x:int,y:int,color:int):
        #Xuan内部使用的围棋逻辑,即把传进来的坐标转为自己的棋盘信息
        #不需要判断自身死棋或者打劫 因为传进来的棋谱默认合法
        self.isBlack=True if color=='black' else False
        selfKillFlag=1 if color=='black' else -1
        killFlag=-1 if color=='black' else 1
        #需要自己组棋盘
        self.board[x][y]=selfKillFlag
        self.combine(x,y)
        killResult=self.doKill(x,y,killFlag)
        if len(killResult):
            for i in range(len(killResult)):
                self.cleanString(killResult[i])

    def returnData(self,success:bool)->tuple:
        return success,self.board,self.string,self.robX,self.robY

    def GoLogic(self,x:int,y:int,color:int)->tuple:#完整的围棋逻辑
        #先做好备份 防止出现要类似悔棋的逻辑
        backupBoard=copy.deepcopy(self.board)
        backupString=copy.deepcopy(self.string)
        backupRobX,backupRobY=self.robX,self.robY
        checkStep=self.checkStep(x,y)#检查(x,y)是否已有棋子
        if not checkStep:
            logging.debug('GoLogic校验失败!')
            return self.returnData(success=False)
        #判断自杀逻辑是反过来的
        if color=='black':
            self.isBlack=True
            selfKillflag=1
            killFlag=-1
        else:
            self.isBlack=False
            selfKillflag=-1
            killFlag=1
        #需要自己组棋盘
        self.board[x][y]=selfKillflag
        self.combine(x,y)
        killResult=self.doKill(x,y,killFlag)
        if len(killResult):
            for i in range(len(killResult)):
                killed=self.cleanString(killResult[i])
                if len(killed)==1:
                    #在这里判断打劫
                    logging.debug('GoLogic正在判断打劫,robX={},robY={},x={},y={}'.format(self.robX,self.robY,x,y))
                    if (self.robX is not None and self.robY is not None)\
                    and int(self.robX)==int(x) and int(self.robY)==int(y):
                        logging.debug('无法在打劫点落子!')
                        logging.debug('GoLogic校验失败!')
                        self.board=backupBoard
                        self.string=backupString
                        return self.returnData(success=False)
                    #如果之前不是打劫点,则更新打劫点
                    self.robX=killed[0]['x']
                    self.robY=killed[0]['y']
                    logging.debug('保存了目前打劫点:x={},y={}'.format(self.robX,self.robY))
                else:
                    #如果之前有打劫点,则现在清空
                    self.robX=None
                    self.robY=None
        else:
            selfResult=self.checkKill(x,y,selfKillflag)
            if selfResult:#处理失败 一切还原
                self.board=backupBoard
                self.string=backupString
                self.robX=backupRobX
                self.robY=backupRobY
                logging.debug('不能在导致自己死棋的位置落子!')
                logging.debug('GoLogic校验失败!')
                return self.returnData(success=False)
        logging.debug('GoLogic校验成功!')
        return self.returnData(success=True)

    def getLastBoard(self,boardList:list[list[list]],index:int,myColor:int,oppoColor:int)->tuple:#获取最近的7步棋
        myLast7Boards=[]
        oppoLast7Boards=[]
        start=index-7
        for i in range(7):
            if start<0 or start>len(boardList):
                emptyBoard=getEmptyBoard()
                myLast7Boards.append(emptyBoard)
                oppoLast7Boards.append(emptyBoard)
            else:
                currentBoard=boardList[start]
                myBoard=self.setBoardByColor(board=copy.deepcopy(currentBoard),color=myColor)
                oppoBoard=self.setBoardByColor(board=copy.deepcopy(currentBoard),color=oppoColor)
                myLast7Boards.append(myBoard)
                oppoLast7Boards.append(oppoBoard)
            start+=1
        return myLast7Boards,oppoLast7Boards

    @staticmethod
    def getDotLife(x:int,y:int,board:list[list])->int:#获取棋盘上某个点是否为空
        if x<0 or x>18 or y<0 or y>18:
            return 0
        return 1 if not board[x][y] else 0

    def getStringLife(self,board:list[list],L:list[dict],threshold=4)->int:#获取这个棋串有多少气,大于等于threshold就返回-1,不需要讨论
        life=0
        for i in range(len(L)):
            x,y=L[i]['x'],L[i]['y']
            directs=getFourDirect(x,y)
            for direct in directs:
                life+=self.getDotLife(direct['x'],direct['y'],board)
                if life>=threshold:return -1
        return life

    def getBoardAddition(self,board:list[list],string:dict,color:int)->tuple:#获取当前局面额外的信息
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
                if board[i][j]!=color and board[i][j]: myBoard[i][j]=0#不是落子方也不是空
                if board[i][j]==color: oppoBoard[i][j]=0#落子方
        myString=copy.deepcopy(string[myColorText])
        oppoString=copy.deepcopy(string[oppoColorText])
        myArray=[[],[],[]]
        oppoArray=[[],[],[]]
        for key in myString:
            if int(key)<19: continue#不是棋串
            array=myString[key]
            life=self.getStringLife(board=board,L=array)
            if life==-1: continue#节约时间
            if life==1: myArray[0].append(array)
            if life==2: myArray[1].append(array)
            if life==3: myArray[2].append(array)
        for key in oppoString:
            if int(key)<19: continue#不是棋串
            array=oppoString[key]
            life=self.getStringLife(board=board,L=array)
            if life==-1: continue#节约时间
            if life==1: oppoArray[0].append(array)
            if life==2: oppoArray[1].append(array)
            if life==3: oppoArray[2].append(array)
        #改写数组
        for k in range(3):
            myLifeBoard[k]=self.setBoardByArray(board=myLifeBoard[k],array=myArray[k],color=myColor)
            oppoLifeBoard[k]=self.setBoardByArray(board=oppoLifeBoard[k],array=oppoArray[k],color=oppoColor)
        return myBoard,oppoBoard,myLifeBoard,oppoLifeBoard

    @staticmethod
    def setBoardByArray(board:list[list],array:list[dict],color:int):#根据传入的参数更新棋盘
        for i in range(len(array)):
            x:int=array[i]['x']
            y:int=array[i]['y']
            board[x][y]=color
        return board

    @staticmethod
    def setBoardByColor(board:list[list],color:int)->list[list]:#让棋盘只留下某个颜色
        for i in range(19):
            for j in range(19):
                if board[i][j]!=color:
                    board[i][j]=0
        return board

    @staticmethod
    def getColorNumByText(text:str)->int:#传入颜色文字转数字
        return 1 if text=='black' else 0

    @staticmethod
    def getColorTextByNum(num:int)->str:#传入颜色数字转文字
        return 'black' if int(num)==1 else 'white'

    def getCurrentColorBoard(self,num:int)->list[list]:#当前是黑色,就全1,否则全0
        board=getEmptyBoard()
        for i in range(19):
            for j in range(19):
                board[i][j]=num
        return board

    @staticmethod
    def getMyOppoBoard(board:list[list],mycolor:int,oppocolor:int)->tuple:#获取自己和对手的棋盘,数字全是1
        myboard=copy.deepcopy(board)
        oppoboard=copy.deepcopy(board)
        for i in range(19):
            for j in range(19):
                myboard[i][j]=1 if myboard[i][j]==mycolor else 0
                oppoboard[i][j]=1 if oppoboard[i][j]==oppocolor else 0
        return myboard,oppoboard

    @staticmethod
    def reverseColor(color:int)->int:#转换颜色
        return -1 if color==1 else 1

    @staticmethod
    def reverseColorText(text:str)->str:
        return 'white' if text=='black' else 'black'