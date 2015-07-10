from Gmetad.alert.alert_store import AlertStore
from Gmetad.alert.alert_rule import AlertSession ,AlertRule
import mysql.connector as mdb
from mysql.connector import errorcode
import time
from datetime import datetime
import logging

'''
    mysql.alert-store{
        host "10.10.82.111"
        port "3306"
        db "mapdb"
        user "root"
        pass "cci"
    }
'''
def get_alert_store(impid="mysql", cfgid="alert-store"):
    ''' Get the specified alert method from the factory via cfgid '''
    return MysqlStore(impid, cfgid)

class MysqlStore(AlertStore):

    MYSQL_HOST = 'host'
    MYSQL_PORT = 'port'
    MYSQL_DB = 'db'
    MYSQL_USER = 'user'
    MYSQL_PASS = 'pass'

    _cfgDefaults = {
        MYSQL_HOST: '10.10.82.111',
        MYSQL_PORT: 3306,
        MYSQL_DB: 'mapdb',
        MYSQL_USER: 'root',
        MYSQL_PASS: 'cci',
    }
    
    def __init__(self, impid, cfgid):
        AlertStore.__init__(self, impid, cfgid)
        self.store = AlertRule()

    def initConfDefaults(self):
        self.cfg = MysqlStore._cfgDefaults

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        self.cfgHandlers = {
            MysqlStore.MYSQL_HOST: self._parseMysqlHost,
            MysqlStore.MYSQL_PORT: self._parseMysqlPort,
            MysqlStore.MYSQL_DB: self._parseMysqlDB,
            MysqlStore.MYSQL_USER: self._parseMysqlUser,
            MysqlStore.MYSQL_PASS: self._parseMysqlPass,
        }

    def _parseMysqlHost(self, arg):
        ''' Parse the Mysql host. '''
        self.cfg[MysqlStore.MYSQL_HOST] = arg.strip().strip('"')

    def _parseMysqlPort(self, arg):
        ''' Parse the Mysql port. '''
        if not isinstance(arg, int):
            res = int(arg.strip().strip('"'))
        else:
            res = arg
        self.cfg[MysqlStore.MYSQL_PORT] = res

    def _parseMysqlDB(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_DB] = arg.strip().strip('"')

    def _parseMysqlUser(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_USER] = arg.strip().strip('"')

    def _parseMysqlPass(self, arg):
        ''' Parse the Mysql port. '''
        self.cfg[MysqlStore.MYSQL_PASS] = arg.strip().strip('"')

    def _connect(self):
        try:
            _mdb = mdb.connect(
                host=self.cfg[MysqlStore.MYSQL_HOST],
                port=self.cfg[MysqlStore.MYSQL_PORT],
                database=self.cfg[MysqlStore.MYSQL_DB],
                user=self.cfg[MysqlStore.MYSQL_USER],
                password=self.cfg[MysqlStore.MYSQL_PASS],
            )
            return _mdb
        except mdb.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exists")
            else:
                print(err)
            raise


    def getRules(self, filters=None):
        '''TODO property filters is not used by now'''
        _mdb = self._connect()
        cursor = _mdb.cursor()
        
        query = ""
        cursor.execute(query)
        rows = cursor.fetchall()

    def getMetricRules(self, metric, filters=None):
        pass

    def getHostRules(self, host, filters=None):
        pass

    def getHMRules(self, host, metric, filters=None):
        _mdb = self._connect()
        cursor = _mdb.cursor()
        results = []
        
        # alarm_rule is expired will not be selected
        query1 = "select alarm_rule_id,alarm_project_id from cm_alarm_disabled where fixed_ip=%(fixed_ip)s and expired=1"
        cursor.execute(query1, {'fixed_ip':host})
        rows_dif = cursor.fetchall()
        rule_reduce = []
        for row in rows_dif:
            rule_reduce.append(dict(zip(cursor.column_names, row)))
        
        #cm_alarm_mapping,mapping,cm_alarm_rule
        query = "select a.* from cm_alarm_rule a,cm_alarm_mapping b,mappings c where c.fixed_ip = b.fixed_ip and b.alarm_project_id = a.alarm_project_id and a.disabled = 0 and c.fixed_ip=%(fixed_ip)s and a.metric_name=%(metric_name)s"
        cursor.execute(query, {'fixed_ip':host,'metric_name':metric})
        rows = cursor.fetchall()
        
        _rule = None
        for row in rows:
            ruleinfo = dict(zip(cursor.column_names, row))
            if rule_reduce:
                flag = 0
                for rule in rule_reduce:
                    if ruleinfo['id'] == rule['alarm_rule_id'] and ruleinfo['alarm_project_id'] == rule['alarm_project_id']:
                        flag = 1
                if flag == 0:
                    _rule = AlertRule(**ruleinfo)
                    results.append(_rule)
            else:
                _rule = AlertRule(**ruleinfo)
                results.append(_rule)
        
        return results
    
    def disable_HWRule(self, rule, projcet_id, host):
        _mdb = self._connect()
        cursor = _mdb.cursor()
        
        query_set = 'select * from cm_alarm_disabled where alarm_rule_id=%(alarm_rule_id)s and fixed_ip=%(fixed_ip)s and alarm_project_id=%(alarm_project_id)s'
        cursor.execute(query_set, {'alarm_rule_id':rule,'alarm_project_id':projcet_id,'fixed_ip':host})
        rows = cursor.fetchall()
        if not rows:
            query_insert = "insert into cm_alarm_disabled (alarm_rule_id,alarm_project_id,fixed_ip,expired) value(%(alarm_rule_id)s,%(alarm_project_id)s,%(fixed_ip)s,1)"
            cursor.execute(query_insert, {'alarm_rule_id':rule,'alarm_project_id':projcet_id,'fixed_ip':host})
        else:
            query = "update cm_alarm_disabled set expired=1 where alarm_rule_id=%(alarm_rule_id)s and fixed_ip=%(fixed_ip)s and alarm_project_id=%(alarm_project_id)s"
            cursor.execute(query, {'alarm_rule_id':rule,'alarm_project_id':projcet_id,'fixed_ip':host})
        
        _mdb.commit()
        
        cursor.close()
        _mdb.close()

    def getRule(self, key):
        pass
    
    def getContacts(self, project_id):
        _mdb = self._connect()
        cursor = _mdb.cursor()
        
        query = "select alarm_group_ids from cm_alarm_project where id=%(alarm_project_id)s"
        cursor.execute(query, {'alarm_project_id':project_id})
        row = cursor.fetchone()
        
        _contacts = []
        if row is not None:
            group_ids = row[0]
            # when i use cursor.execute(query, {'group_ids':group_ids}) it may cause run false, lost some records
            query = "select b.* from cm_user_group_mapping a, cm_alarm_user b where b.id = a.alarm_user_id and a.alarm_group_id in (%(group_ids)s)"
            cursor.execute(query%{'group_ids':group_ids})
            rows = cursor.fetchall()
            if rows is not None:
                for r in rows:
                    _contacts.append(dict(zip(cursor.column_names, r)))
        
        cursor.close()
        _mdb.close()
        
        return _contacts
    
    def storeAlertMsg(self, rule, host, sub, msg, alert_time):
        _mdb = self._connect()
        cursor = _mdb.cursor()

        if alert_time is not None and isinstance(alert_time, int):
            last_alert = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert_time))
        else:
            last_alert = None
        
        cursor.execute("select alarm_group_ids from cm_alarm_project where id=%(alarm_project_id)s",{'alarm_project_id':rule.alarmProjectId})
        group_ids = cursor.fetchone()[0]
        
        cursor.execute("select group_concat(alarm_group_name) from cm_alarm_group where id in (%(group_ids)s)"%{'group_ids':group_ids})
        group_names = cursor.fetchone()[0]

        insert_data = {'alarm_rule_id':rule.id,'metric_name':rule.metricName,'alarm_time':last_alert,'alarm_content_summary':sub,'alarm_content':msg,'alarm_group_ids':group_ids,'alarm_group_names':group_names,'fixed_ip':host,'metric_desc':rule.metricDesc}
        add_alert = "insert into cm_alarm_history (`alarm_rule_id`,`metric_name`,`alarm_time`,`alarm_content_summary`,`alarm_content`,`alarm_group_ids`,`alarm_group_names`,`fixed_ip`,`metric_desc`) values (%(alarm_rule_id)s,%(metric_name)s,%(alarm_time)s,%(alarm_content_summary)s,%(alarm_content)s,%(alarm_group_ids)s,%(alarm_group_names)s,%(fixed_ip)s,%(metric_desc)s)"
        cursor.execute(add_alert, insert_data)
        
        _mdb.commit()

        cursor.close()
        _mdb.close()
    
    def getSession(self, rule, host):
        _mdb = self._connect()
        cursor = _mdb.cursor()

        query = "SELECT * FROM cm_alert_sessions WHERE rule_id=%(rule_id)s and fixed_ip=%(fixed_ip)s and is_active=1 order by id desc limit 1"
        cursor.execute(query, {'rule_id': rule, 'fixed_ip':host})
        row = cursor.fetchone()

        _ses = None
        if row is not None:
            sesinfo = dict(zip(cursor.column_names, row))
            _ses = AlertSession()
            _ses.id = sesinfo['id']
            _ses.rule = sesinfo['rule_id']
            _ses.host = sesinfo['fixed_ip']
            if isinstance(sesinfo['last_alert'], datetime):
                temp_time = sesinfo['last_alert'].utctimetuple()
            elif isinstance(sesinfo['last_alert'], str):
                temp_time = time.strptime(sesinfo['last_alert'], '%Y-%m-%d %H:%M:%S')
            else:
                temp_time = None
            
            if temp_time is not None:
                _ses.lastAlert = int(time.mktime(temp_time))
            else:
                _ses.lastAlert = None
            _ses.alertTimes = sesinfo['alert_times']

        cursor.close()
        _mdb.close()

        return _ses

    def newSession(self, rule, host, alert_time):
        '''
        @param rule:
        @param host:
        @param last_alert: int type timestamp   
        '''
        _mdb = self._connect()
        cursor = _mdb.cursor()

        add_session = "insert into cm_alert_sessions (rule_id, fixed_ip, last_alert) values (%(rule_id)s, %(fixed_ip)s, %(last_alert)s)"

        if alert_time is not None and isinstance(alert_time, int):
            last_alert = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert_time))
        else:
            last_alert = None

        # Insert salary information
        data_session = {
            'rule_id': rule,
            'fixed_ip': host,
            'last_alert': last_alert,
        }
        cursor.execute(add_session, data_session)

        _mdb.commit()

        cursor.close()
        _mdb.close()

    def renewSession(self, sid, rule, host, alert_time):
        _mdb = self._connect()
        cursor = _mdb.cursor()

        close_session = "update cm_alert_sessions set is_active=0 where id=%(id)s"
        add_session = "insert into cm_alert_sessions (rule_id, fixed_ip, last_alert) values (%(rule_id)s, %(fixed_ip)s, %(last_alert)s)"
        
        if alert_time is not None and isinstance(alert_time, int):
            last_alert = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert_time))
        else:
            last_alert = None
        
        cursor.execute(close_session, { 'id': sid} )

        data_session = {
            'rule_id': rule,
            'fixed_ip': host,
            'last_alert': last_alert,
        }

        cursor.execute(add_session, data_session)

        _mdb.commit()

        cursor.close()
        _mdb.close()

    def hitSession(self, sid, rule, host, alert_time):
        _mdb = self._connect()
        cursor = _mdb.cursor()

        hit_session = "update cm_alert_sessions set alert_times=alert_times+1, last_alert=%(last_alert)s where id=%(id)s"
        
        if alert_time is not None and isinstance(alert_time, int):
            last_alert = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert_time))
        else:
            last_alert = None
        
        cursor.execute(hit_session, { 'id': sid, 'last_alert': last_alert } )

        _mdb.commit()

        cursor.close()
        _mdb.close()

