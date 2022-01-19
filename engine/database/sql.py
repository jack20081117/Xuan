selectTest='select * from t'

selectGoData="select sgf,black,white,createtime from goData"
selectGoDataPlus="select sgf,black,white,createtime from goData {}"
selectFileRead="select count(*) as count from fileRead where filename='{}'"
selectCountGoData='select count(1) as count from goData'

insertGoData="insert into goData (sgf,black,white,createtime) values ('{}','{}','{}','{}')"
insertFileRead="insert into fileRead (filename) values ('{}')"

vacuum='vacuum'

deleteGoData='delete from goData'
deleteFileRead='delete from fileRead'