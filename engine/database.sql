--把这些语句放到python自带的sqlite3中运行吧

-- >>> import sqlite3
-- >>> ...
-- >>> cursor.execute('''
-- ... CREATE TABLE "goData"
-- ... (
-- ... ...
-- ... );
-- ... ''')
-- >>> ...

CREATE TABLE "goData"
(
    id INTEGER
        CONSTRAINT gobanPK
            PRIMARY KEY autoincrement,
    sgf VARCHAR(1000) NOT NULL,
    black VARCHAR(20),
    white VARCHAR(20),
    createTime VARCHAR(20)
);

CREATE TABLE "fileRead"
(
    id INTEGER NOT NULL
        CONSTRAINT fileReadPK
            PRIMARY KEY autoincrement,
    filename VARCHAR(500)
);