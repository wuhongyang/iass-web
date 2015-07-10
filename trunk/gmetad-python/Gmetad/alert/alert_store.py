from Gmetad.gmetad_confable import GmetadConfable
import importlib


def get_alert_store(impid, cfgid="alert-store"):
    ''' Get the specified alert method from the factory via cfgid '''
    store_module = importlib.import_module("Gmetad.alert.stores." + impid + "_store")
    return store_module.get_alert_store(impid, cfgid)

class AlertStore(GmetadConfable):
    ''' This is the backend store to maintain available alert rules and sessions
        mysql {
            user "user"
            pass "pass"
            host "127.0.0.1"
            port 3306
        }

        mysql.alert {
            getRulesSQL "select * from alertdb.rules where @{filters}"
            getRulesViaMetricSQL "select * from alertdb.rules where metric=${metric} and @{filters}"
            ...
            newSessionSQL "Insert into alertdb.sessions (rule, host, time) values ('RULE_XXX', 'HOST_YYY',
            '2013-11-27 00:00:00')"
            hitSessionSQL "Update alertdb.sessions set lastAlert = ${ntime}, alertTimes = alertTime + 1
            where id = ${sid}"
        }
        '''

    def getRules(self, filters):
        pass

    def getMetricRules(self, metric, filters):
        pass

    def getHostRules(self, host, filters):
        pass

    def getHMRules(self, host, metric, filters):
        pass

    def getRule(self, key):
        pass
    
    def getContacts(self, project_id):
        '''
        @param project_id: alarm_project_id ex:'1,2'
        '''
        pass
    
    def storeAlertMsg(self, rule, host, sub, msg, alert_time):
        '''
        @param rule: AlertRule object 
        @param host: fixed_ip
        @param sub: subject type str
        @param msg: message type str  
        @param alert_time: timestamp object 
        '''
        pass
    
    def getSession(self, rule, host):
        '''
        @param rule: rule_id
        @param host: fixed_ip
        '''
        pass

    def newSession(self, rule, host, time):
        '''
        @param rule: rule_id
        @param host: fixed_ip
        @param time: last_alert   
        '''
        pass

    def renewSession(self, sid, rule, host, time):
        '''
        @param sid: alert_session id
        @param rule: rule_id
        @param host: fixed_ip
        @param time: last_alert
        '''
        pass

    def hitSession(self, sid, rule, host, time):
        '''
        @param sid: alert_session id
        @param rule: rule_id
        @param host: fixed_ip
        @param time: last_alert        
        '''
        pass
    
    def disable_HWRule(self, rule, project_id, host):
        '''
        @param rule: rule_id
        @param project_id: alarm_project_id
        @param host: fixed_ip  
        '''
        pass

