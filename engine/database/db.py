import sqlite3

class Database(object):
    def init(self,name):
        self.filename=name
        self.conn=sqlite3.connect(self.filename,check_same_thread=False)
        self.cur=self.conn.cursor()

    def dictFactory(self,cursor,row):
        d={}
        for index,col in enumerate(cursor.description):
            d[col[0]]=row[index]
        return d

    def select(self,sql):
        self.conn.row_factory=self.dictFactory
        queryResult=self.cur.execute(sql).fetchall()
        return queryResult

    def execute(self,sql):
        self.cur.execute(sql)
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
