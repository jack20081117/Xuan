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