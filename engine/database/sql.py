selectTest='select * from t'

selectGoData="select sgf,black,white,createtime,hash from go_data"
selectGoDataPlus="select sgf,black,white,createtime,hash from go_data {}"
selectCountFileRead="select count(*) count from file_read where filename='{}'"
selectCountGoData='select count(*) count from go_data'

insertGoData="insert into go_data (sgf,black,white,createtime,hash) values ('{}','{}','{}','{}','{}')"
insertFileRead="insert into file_read (filename) values ('{}')"

vacuum='vacuum'

deleteGoData='delete from go_data'
deleteFileRead='delete from file_read'