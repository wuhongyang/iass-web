import datetime
import MySQLdb as mysql
import logging

Host = "10.10.82.248"
User = "root"
Password = "root"
Database = "mapdb"
Port = 3306

Logfile = "/root/getMap/countAlarmByMonth.log"
logging.basicConfig(filename=Logfile, level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

if __name__ == '__main__':
    '''
        count the total alarm times of one month in table alarm_history
    '''
    today = datetime.date.today()
    oneday = datetime.timedelta(days=15)
    #this script will be executed at 1st day of everymonth,so yesterday is the day of last month
    yesterday = today-oneday
    t1 = datetime.datetime(today.year, today.month, 1, 0, 0)
    t2 = datetime.datetime(yesterday.year, yesterday.month, 1, 0, 0)
    logging.info("Starting count the alarm times of %s-%s", yesterday.year, yesterday.month)
    db = mysql.connect(Host, User, Password, Database, Port)
    cursor = db.cursor()
    sql = "select count(*) from cm_alarm_history where alarm_time < now() and alarm_time > DATE_SUB(now(),INTERVAL 1 MONTH)"
    #sql = "select count(*) from cm_alarm_history where alarm_time < '%s' and alarm_time > '%s'" % (t1, t2)
    print "sql: "+sql
    cursor.execute(sql)
    res = cursor.fetchone()
    count = res[0]
    logging.info("%s-%s has %s alarm info of the month totally", yesterday.year, yesterday.month, count)
    time_str = str(t2.year) + '-' + str(t2.month)
    
    fetch_sql = "select * from cm_alarm_history_month_count where alarm_time='%s'" % (time_str)
    if cursor.execute(fetch_sql) >=1:
        refresh_sql = "update cm_alarm_history_month_count set count = %s where alarm_time='%s'" % (count, time_str)
    else:
		refresh_sql = "insert into cm_alarm_history_month_count values(null,%s,'%s')" % (count, time_str)
    print "insert_sql: "+refresh_sql
    try:
        cursor.execute(refresh_sql)
        db.commit()
    except mysql.Error, e:
        logging.info("Insertion of cm_alarm_history_month_count failed:%d:%s", e.args[0], e.args[1])
        db.rollback
    db.close()
