import sqlite3

if __name__ == '__main__':
    file=input('FILE:')
    conn=sqlite3.connect('./dataSet/'+file)
    cursor=conn.cursor()
    cursor.execute('''
    CREATE TABLE "goData"
    (
        id INTEGER
            CONSTRAINT gobanPK
                PRIMARY KEY autoincrement,
        sgf VARCHAR(1000) NOT NULL,
        black VARCHAR(20),
        white VARCHAR(20),
        createTime VARCHAR(20),
        hash VARCHAR(20)
    );
    ''')

    cursor.execute('''
    CREATE TABLE "fileRead"
    (
        id INTEGER NOT NULL
            CONSTRAINT fileReadPK
                PRIMARY KEY autoincrement,
        filename VARCHAR(500)
    );''')

    cursor.close()
    conn.commit()
    conn.close()