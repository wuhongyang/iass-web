import cx_Oracle
import MySQLdb as mysql


if __name__== '__main__':
    '''
        scan the oracle database,and sync the data in table ticket to local mysql.ticket
    '''

    mysql_conn = mysql.connect("10.10.82.227", "root", "root", "mapdb")
    mysql_cursor = mysql_conn.cursor()

    try:
        #max_id is the max record in the local db,we need to sync the records bigger than max in the remote db
        mysql_cursor.execute("select max(id) from ticket")
        r = mysql_cursor.fetchone()
        max_id = r[0]
    except mysql.Error, e:
        print ("error %d:%s" % (e.args[0], e.args[1]))
        mysql_conn.rollback()

    ora_conn = cx_Oracle.connect("system", "oracle", "192.168.133.152:49161/xe")
    #conn = cx_Oracle.connect("sys", "123456", "ORCL", mode=cx_Oracle.SYSDBA)
    c = ora_conn.cursor()
    #x = c.execute('select * from "SYSTEM"."ticket"')
    sql = 'select * from "SYSTEM"."ticket" where "SYSTEM"."ticket"."id" > %d' % (max_id)
    x = c.execute(sql)
    result = x.fetchall()

    for row in result:
        print row
        try:
            sql = "insert into mapdb.ticket values(%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s',%s,'%s')" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
            print sql
            mysql_cursor.execute(sql)
            mysql_conn.commit()
        except mysql.Error, e:
            print ("error %d:%s" % (e.args[0], e.args[1]))
            mysql_conn.rollback()

    c.close()
    ora_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
