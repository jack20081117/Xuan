from ai.datacenter import DataCenter
from src.go import Go
import logging
logging.basicConfig(level=logging.INFO)

datacenter=DataCenter()
go=Go()

if __name__ == '__main__':
    result=datacenter.getAllDataSet()

    go.transferSgf2StringAndBoard(result[0][0])
    result=go.checkWinner(go.board)
