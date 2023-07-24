import json,socket,threading,logging
from src.tools import *
from ai.xuan import Xuan

class Server(object):
    xuan=None

    def __init__(self):
        self.xuan=Xuan()

    def runServer(self,server,sock):
        while True:
            data=sock.recv(20000).decode()#调用recv(max)方法,一次最多接收指定的字节数,如果max太小连东西都收不到
            if not data or data=='exit':
                break
            logging.info('收到请求,time:%s'%getDatetime()['timeformat'])
            response=self.xuan.parseOperator(data)
            sock.send(json.dumps(response).encode())
        sock.close()

    def run(self,port):
        IP='127.0.0.1'
        server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)#TCP
        server.bind((IP,int(port)))
        server.listen(5)#调用listen()方法开始监听端口,传入的参数指定等待连接的最大数量
        logging.info('引擎运行在:{}:{}'.format(IP,port))
        while True:
            sock,addr=server.accept()
            thread=threading.Thread(target=self.runServer,args=(server,sock))
            thread.start()