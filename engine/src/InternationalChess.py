import logging,chess

from src.tools import *
from config import *
from config import GLOBAL_DICT as gl

class Chess(object):
    @staticmethod
    def getCurrentColorByFen(fen:str):
        fenList=fen.split(' ')
        color=fenList[1]
        return True if color=='w' else False

    @staticmethod
    def countPieces(board:list)->dict:#计算双方各有多少棋子
        res={
            'white':{
                'soldier':0,
                'horse':0,
                'elephant':0,
                'car':0,
                'queen':0,
                'light':0,#轻子,象和马
                'heavy':0#重子,车和后
            },
            'black':{
                'soldier':0,
                'horse':0,
                'elephant':0,
                'car':0,
                'queen':0,
                'light':0
            }
        }
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                place=board[i][j]
                if place==PIECES['WHITE_SOLDIER']:
                    res['white']['soldier']+=1
                if place==PIECES['WHITE_CAR']:
                    res['white']['car']+=1
                    res['white']['heavy']+=1
                if place==PIECES['WHITE_HORSE']:
                    res['white']['horse']+=1
                    res['white']['light']+=1
                if place==PIECES['WHITE_ELEPHANT']:
                    res['white']['elephant']+=1
                    res['white']['light']+=1
                if place==PIECES['WHITE_QUEEN']:
                    res['white']['queen']+=1
                    res['white']['heavy']+=1
                if place==PIECES['BLACK_SOLDIER']:
                    res['black']['soldier']+=1
                if place==PIECES['BLACK_CAR']:
                    res['black']['car']+=1
                    res['black']['heavy']+=1
                if place==PIECES['BLACK_HORSE']:
                    res['black']['horse']+=1
                    res['black']['light']+=1
                if place==PIECES['BLACK_ELEPHANT']:
                    res['black']['elephant']+=1
                    res['black']['light']+=1
                if place==PIECES['BLACK_QUEEN']:
                    res['black']['queen']+=1
                    res['black']['heavy']+=1
        return res

    @staticmethod
    def getSoldierPiled(board:list)->tuple:
        res=[]
        whiteRes=[]
        blackRes=[]
        for j in range(BOARD_SIZE):#按列枚举
            tempWhite=[]
            tempBlack=[]
            for i in range(BOARD_SIZE):
                columnPlace=board[i][j]
                if columnPlace==PIECES['WHITE_SOLDIER']:
                    tempWhite.append({
                        'x':i,
                        'y':j,
                        'piece':columnPlace
                    })
                if columnPlace==PIECES['BLACK_SOLDIER']:
                    tempBlack.append({
                        'x':i,
                        'y':j,
                        'piece':columnPlace
                    })
            if len(tempWhite)>1:whiteRes.extend(tempWhite)
            if len(tempBlack)>1:blackRes.extend(tempBlack)
        res.extend(whiteRes)
        res.extend(blackRes)
        return res,whiteRes,blackRes

    def getCurrentGameCourse(self,board:list)->str:
        #判断目前的对局处于什么样的进程:OG/MG/EG
        res=self.countPieces(board=board)
        if (res['white']['queen']==0) or (res['black']['queen']==0):
            return END_GAME #无后直接残局
        #双方兵大于开局threshold,轻子也没兑换多少,属于开局
        if (res['white']['soldier']>=OPEN_SOLDIER_THRESHOLD)\
        and(res['black']['soldier']>=OPEN_SOLDIER_THRESHOLD)\
        and(res['white']['light']>=OPEN_LIGHT_THRESHOLD)\
        and(res['black']['light']>=OPEN_LIGHT_THRESHOLD):
            return OPEN_GAME
        #轻子小于等于残局threshold,车也少了,基本算残局
        if (res['white']['car']<=END_CAR_THRESHOLD)\
        and(res['black']['car']<=END_CAR_THRESHOLD)\
        and(res['white']['light']<=END_LIGHT_THRESHOLD)\
        and(res['black']['light']<=END_LIGHT_THRESHOLD):
            return END_GAME
        return MIDDLE_GAME#默认其他都是中局

    @staticmethod
    def parseBoard(board:chess.Board or chess.SquareSet)->list:
        lines=str(board).split('\n')
        lineList=[]
        for i in range(len(lines)):
            singleLine=lines[i].split(' ')
            lineList.append(singleLine)
        return lineList

    #判断这个棋子是不是白棋
    @staticmethod
    def isWhite(piece:str)->bool:
        return True if piece.isupper() else False

    def getSingleAttack(self,board:chess.Board,i,j):
        res=board.attacks(square=BOARD_PLACE[i][j])
        res=self.parseBoard(res)
        return res

    @staticmethod
    def isLight(piece:str)->bool:
        return True if piece=='h' or piece=='H' or piece=='e' or piece=='E' else False

    @staticmethod
    def isHeavy(piece:str)->bool:
        return True if piece=='c' or piece=='C' or piece=='q' or piece=='Q' else False

    @staticmethod
    def isSoldier(piece:str)->bool:
        return True if piece=='s' or piece=='S' else False

    @staticmethod
    def isKing(piece:str)->bool:
        return True if piece=='k' or piece=='K' else False

    @staticmethod
    def isOutPost(index:int)->bool:#先锋区域,3~6行
        return True if 2<=index<=5 else False

    @staticmethod
    def isMiddle(index:int)->bool:#中心区域,3~6列
        return True if 3<=index<=6 else False

    @staticmethod
    def parseUci2Step(uci,parsedBoard:list,board)->str:
        logging.warning('不建议使用parseUci2Step函数')
        uciStr=str(uci)
        logging.info('parsedBoard :>> %s'%parsedBoard)
        beginX=ALPHABET[uciStr[0:1]]
        beginY=ALPHABET[uciStr[1:2]]
        endX=uciStr[2:3]
        endY=uciStr[3:4]
        promote=uciStr[4:5] or None
        promoteText=('='+promote.upper() if promote is not None else '')
        x,y=beginX-1,8-beginY
        destX,destY=ALPHABET[endX]-1,8-ALPHABET[endY]
        kill=('x' if parsedBoard[destY][destX]!='.' else '')
        pieces:str=parsedBoard[y][x]
        name=('' if(pieces=='.' or pieces.upper()=='P') else pieces.upper())
        board.push(uci)
        #增加对将军和将杀的校验
        isCheck:bool=board.is_check()
        isCheckmate:bool=board.is_checkmate()
        res=str(name)+kill+str(endX)+str(endY)+str(promoteText)
        if isCheckmate:
            res+='#'
            return res
        if isCheck:
            res+='+'
            return res

    #传入一个棋盘的list,解析其中的内容,方便估值函数使用.尽量做到时间复杂度O(n²)
    def parseInternalBoardInfo(self,rootBoard:chess.Board,fen)->dict:
        #自动转换,方便点
        board=self.parseBoard(rootBoard) if not isinstance(rootBoard,list) else rootBoard
        res={
            'whiteAttack':getEmptyBoard(),
            'blackAttack':getEmptyBoard(),
            'white':getEmptyPieceTypeDict(),
            'black':getEmptyPieceTypeDict(),
            'whiteOutpost':[],
            'blackOutpost':[],
            'whitePieces':getEmptyPieceTypeDict(),
            'blackPieces':getEmptyPieceTypeDict(),
            'allSoldierPiled':None,
            'whiteSoldierPiled':None,
            'blackSoldierPiled':None,
            'whiteBadCar':[],
            'blackBadCar':[],
            'whiteThreaten':[],
            'blackThreaten':[],
            'whitePromotionSoldier':[],
            'blackPromotionSoldier':[],
            'currentColor':self.getCurrentColorByFen(fen=fen)
        }
        allRes,whiteRes,blackRes=self.getSoldierPiled(board=board)
        res['allSoldierPiled']=allRes
        res['whiteSoldierPiled']=whiteRes
        res['blackSoldierPiled']=blackRes
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                piece=board[i][j]
                if piece!=PIECES['EMPTY']:
                    pass
        return res

    @staticmethod
    def getPiecesInfo(info:dict,color)->tuple:
        text='white' if color==WHITE else 'black'
        subInfo=info[text]
        elephant=subInfo['elephant']
        car=subInfo['car']
        queen=subInfo['queen']
        horse=subInfo['horse']
        soldier=subInfo['soldier']
        king=subInfo['king']
        return elephant,car,queen,horse,soldier,king

    #判断这个棋子是否受到威胁,不能只看攻击列表,还得看子力强弱,先不判断棋子被钉死的情况
    def checkIfThreaten(self,info:dict,x,y,color,pieceType)->bool:
        if color==WHITE:
            oppoColor=BLACK
            attackListText='whiteAttack'
            oppoAttackListText='blackAttack'
        else:
            oppoColor=WHITE
            attackListText='blackAttack'
            oppoAttackListText='whiteAttack'
        #获取对方的棋子情况
        elephant,car,queen,horse,soldier,king=self.getPiecesInfo(info=info,color=oppoColor)
        attackList=info[attackListText]
        oppoAttackList=info[oppoAttackListText]
        #被对方攻击然而自己没人保护,直接返回True,节约性能
        if oppoAttackList[x][y] and not attackList[x][y]:return True
        #被兵攻击就是威胁,因为兵吃任何棋子都不亏
        for i in range(len(soldier)):
            attack=soldier[i]
            if attack['attack'][x][y]!=PIECES['EMPTY']:return True
        #重子被轻子威胁,直接就是威胁了
        if pieceType==PIECES['WHITE_CAR'] or pieceType==PIECES['WHITE_QUEEN']:
            for i in range(len(elephant)):
                attack=elephant[i]
                if attack['attack'][x][y]!=PIECES['EMPTY']:return True
            for i in range(len(horse)):
                attack=horse[i]
                if attack['attack'][x][y]!=PIECES['EMPTY']:return True
            #后被车威胁
            if pieceType==PIECES['WHITE_QUEEN']:
                for i in range(len(car)):
                    attack=car[i]
                    if attack['attack'][x][y]!=PIECES['EMPTY']:return True
        return False

    def checkSingleColorThreaten(self,info:dict,color)->dict:#判断每个颜色的棋子是否受到威胁
        if color==WHITE:
            text='white'
            threatText='whiteThreaten'
            attackText='blackAttack'
        else:
            text='black'
            threatText='blackThreaten'
            attackText='whiteAttack'
        attacked=info[attackText]
        elephant,car,queen,horse,soldier,king=self.getPiecesInfo(info=info,color=color)
        for i in range(len(elephant)):
            x,y=elephant[i]['x'],elephant[i]['y']
            check=self.checkIfThreaten(info=info,x=x,y=y,color=color,pieceType=PIECES['WHITE_ELEPHANT'])
            if check:info[threatText].append({'x':x,'y':y})
        for i in range(len(car)):
            x,y=car[i]['x'],car[i]['y']
            check=self.checkIfThreaten(info=info,x=x,y=y,color=color,pieceType=PIECES['WHITE_CAR'])
            if check:info[threatText].append({'x':x,'y':y})
        for i in range(len(queen)):
            x,y=queen[i]['x'],queen[i]['y']
            check=self.checkIfThreaten(info=info,x=x,y=y,color=color,pieceType=PIECES['WHITE_QUEEN'])
            if check:info[threatText].append({'x':x,'y':y})
        for i in range(len(horse)):
            x,y=horse[i]['x'],horse[i]['y']
            check=self.checkIfThreaten(info=info,x=x,y=y,color=color,pieceType=PIECES['WHITE_HORSE'])
            if check:info[threatText].append({'x':x,'y':y})
        return info

    def checkAllThreaten(self,info:dict)->dict:
        info=self.checkSingleColorThreaten(info,WHITE)
        info=self.checkSingleColorThreaten(info,BLACK)
        return info

    #自身左右的格子不能有兵拦着,对白棋来说对手的兵如果y坐标比自己的大可以忽略,黑棋反之,因为已经超过自己了,不会阻挡升变.
    @staticmethod
    def checkSingleSoldierIsPromotion(oppoSoldier:list,x,y,color)->bool:
        y1,y2=y-1,y-2
        for i in range(len(oppoSoldier)):
            soldier=oppoSoldier[i]
            oppoX=soldier['x']
            oppoY=soldier['y']
            #判断条件是白棋的路线上有黑棋或黑棋的路线有白棋
            if color==WHITE and x>oppoX:
                if y==oppoY or y1==oppoY or y2==oppoY:
                    return False#不是通路兵
            if color==BLACK and x<oppoX:
                if y==oppoY or y1==oppoY or y2==oppoY:
                    return False#不是通路兵
        return True

    def getAllPromotion(self,info:dict)->dict:
        whiteSoldiers=info['whitePieces']['soldier']
        blackSoldiers=info['blackPieces']['soldier']
        for i in range(len(whiteSoldiers)):
            soldier=whiteSoldiers[i]
            x,y=soldier['x'],soldier['y']
            res=self.checkSingleSoldierIsPromotion(blackSoldiers,x,y,WHITE)
            if res:info['whitePromotionSoldier'].append({'x':x,'y':y})
        for i in range(len(blackSoldiers)):
            soldier=blackSoldiers[i]
            x,y=soldier['x'],soldier['y']
            res=self.checkSingleSoldierIsPromotion(whiteSoldiers,x,y,BLACK)
            if res:info['blackPromotionSoldier'].append({'x':x,'y':y})
        return info

    @staticmethod
    def getPieceTypeByText(piece:str)->str:
        #输入缩写返回全称
        piece=piece.upper()
        if piece=='S':return 'soldier'
        if piece=='Q':return 'queen'
        if piece=='E':return 'elephant'
        if piece=='H':return 'horse'
        if piece=='C':return 'car'
        if piece=='K':return 'king'

    #将获取到的棋子放入数组
    def setPieces(self,info:dict,piece:str,x:int,y:int)->dict:
        colorText='whitePieces' if self.isWhite(piece=piece) else 'blackPieces'
        pieceText=self.getPieceTypeByText(piece=piece)
        info[colorText][pieceText].append({'x':x,'y':y})
        return info

    #将获取到的进攻状态进行处理
    def setAttacks(self,info:dict,attack:list,piece:str,x:int,y:int):
        if self.isWhite(piece=piece):
            attackType='whiteAttack'
            color='white'
        else:
            attackType='blackAttack'
            color='black'
        pieceText=self.getPieceTypeByText(piece=piece)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if attack[i][j]!=PIECES['EMPTY']:
                    info[attackType][i][j]+=1
        info[color][pieceText].append({'x':x,'y':y,'attack':attack})
        return info

    #给先锋棋子赋值
    def setOutposts(self,info:dict,piece:str,x:int,y:int,attack:list):
        outpostType='whiteOutpost' if self.isWhite(piece) else 'blackOutpost'
        info[outpostType].append({'x':x,'y':y,'piece':piece})
        return info