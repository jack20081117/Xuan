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