selectTest='select * from t'

selectGoData="select sgf,black,white from goData"
selectGoDataPlus="select sgf,black,white from goData {}"
selectFileRead="select count(*) as count from fileRead where filename='{}'"
selectCountGoData='select count(1) as count from goData'

insertGoData="insert into goData (sgf,black,white) values ('{}','{}','{}')"
insertFileRead="insert into fileRead (filename) values ('{}')"

vacuum='vacuum'

deleteGoData='delete from goData'
deleteFileRead='delete from fileRead'