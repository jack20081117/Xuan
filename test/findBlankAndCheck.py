#本文件检查Go()中判断目数的机制

import numpy

def findBlank(board,cell):
    def _findBlank(board,result,cell):
        i,j=cell
        board[i,j]=9
        result['cross'].add(cell)
        if i>0:
            if not board[i-1,j]:
                _findBlank(board,result,(i-1,j))
            elif board[i-1,j]==1:
                result['b_around'].add((i-1,j))
            elif board[i-1,j]==2:
                result['w_around'].add((i-1,j))
        if i<18:
            if not board[i+1,j]:
                _findBlank(board,result,(i+1,j))
            elif board[i+1,j]==1:
                result['b_around'].add((i+1,j))
            elif board[i+1,j]==2:
                result['w_around'].add((i+1,j))
        if j>0:
            if not board[i,j-1]:
                _findBlank(board,result,(i,j-1))
            elif board[i,j-1]==1:
                result['b_around'].add((i,j-1))
            elif board[i,j-1]==2:
                result['w_around'].add((i,j-1))
        if j<18:
            if not board[i,j+1]:
                _findBlank(board,result,(i,j+1))
            elif board[i,j+1]==1:
                result['b_around'].add((i,j+1))
            elif board[i,j+1]==2:
                result['w_around'].add((i,j+1))

    result={'cross':set(),'b_around':set(),'w_around':set()}
    _findBlank(board,result,cell)
    return result

def findBlanks(board):
    blanks=[]
    while True:
        cells=numpy.where(board==0)
        if not cells[0].size: break
        blanks.append(findBlank(board,(cells[0][0],cells[1][0])))
    return blanks

def checkWinner(board):
    temp=numpy.copy(board)
    for item in findBlanks(numpy.copy(board)):
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
    print('temp:\n',temp)

    black=temp[temp==1].size+temp[temp==3].size
    white=temp[temp==2].size+temp[temp==4].size
    common=temp[temp==9].size

    return black,white,common

if __name__ == '__main__':
    board=numpy.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ],dtype=numpy.ubyte)
    black,white,common=checkWinner(board)
    print('--------------------------------------')
    print('black:%d,white:%d,common:%d'%(black,white,common))