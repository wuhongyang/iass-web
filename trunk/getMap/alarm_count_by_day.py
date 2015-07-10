import datetime
import MySQLdb as mysql
import logging

Host = "10.10.82.111"
User = "root"
Password = "cci"
Database = "mapdb"

Logfile="/root/getMap/countAlarmByDay.log"
logging.basicConfig(filename=Logfile,level=logging.DEBUG,format = '%(asctime)s - %(levelname)s: %(message)s')

if __name__ == '__main__':
	'''
		count the total alarm times of oneday in table alarm_history
	'''
	today = datetime.date.today()
	oneday = datetime.timedelta(days=1)
	yesterday = today-oneday
	t1=datetime.datetime(today.year,today.month,today.day, 0, 0)
	t2=datetime.datetime(yesterday.year,yesterday.month,yesterday.day, 0, 0)

	logging.info("Starting count the alarm times of day %s",yesterday)

	db = mysql.connect(Host,User,Password,Database)
	cursor = db.cursor()
    #sql = "select * from cm_alarm_history where alarm_time < now() and alarm_time > DATE_SUB(now(),INTERVAL 1 DAY)"
	sql = "select count(*) from cm_alarm_history where alarm_time < '%s' and alarm_time > '%s'" % (t1,t2)
	cursor.execute(sql)
	res=cursor.fetchone()
	count=res[0]
	logging.info("day %s has %s alarm info totally",yesterday,count)
	insert_sql="insert into cm_alarm_history_month_count values(null,%s,'%s')" % (count,yesterday)
	try:
		cursor.execute(insert_sql)
		db.commit()
	except mysql.Error,e:
		logging.info("Insertion of cm_alarm_history_month_count failed:%d:%s",e.args[0],e.args[1])
		db.rollback
	db.close()
	
