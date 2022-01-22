selectTest='select * from t'

selectGoData="select sgf,black,white,createtime from goData"
selectGoDataPlus="select sgf,black,white,createtime from goData {}"
selectCountFileRead="select count(*) count from fileRead where filename='{}'"
selectCountGoData='select count(*) count from goData'

insertGoData="insert into goData (sgf,black,white,createtime) values ('{}','{}','{}','{}')"
insertFileRead="insert into fileRead (filename) values ('{}')"

vacuum='vacuum'

deleteGoData='delete from goData'
deleteFileRead='delete from fileRead'