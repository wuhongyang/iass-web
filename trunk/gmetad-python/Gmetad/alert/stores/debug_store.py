from Gmetad.alert.alert_store import AlertStore
from Gmetad.alert.alert_rule import AlertRule, AlertSession

_sessions = {}

def get_alert_store(impid="debug", cfgid="alert-store"):
    ''' Get the specified alert method from the factory via cfgid '''
    return DebugStore(impid, cfgid)

class DebugStore(AlertStore):

    def __init__(self, impid, cfgid):
        load1_rule = AlertRule(self)
        load1_rule.id = 1
        load1_rule.owner = 'admin'
        load1_rule.contacts = ['baihe@citycloud.com.cn']
        load1_rule.methods = [None, 'mail', 'mail', 'mail']
        load1_rule.alertConds = [None, "$val>0", "$val>0.1", "$val>0.2"]
        load1_rule.metric = "load_one"
        load1_rule.template = "$metric [$val] is high"
        load1_rule.interval = 60
        self._rule = load1_rule

    def getRules(self, filters):
        return [self._rule]

    def getMetricRules(self, metric, filters):
        if metric == 'load_one':
            return [self._rule]
        return []

    def getHostRules(self, host, filters):
        return [self._rule]

    def getHMRules(self, host, metric, filters):
        '''get host metric rules!'''
        if metric == 'load_one':
            return [self._rule]
        return []

    def getRule(self, key):
        if key == 1:
            return self._rule
        return []

    def getSession(self, rule, host):
        if _sessions.has_key(host):
            return _sessions[host]
        return None

    def newSession(self, rule, host, time):
        nsession = AlertSession()
        nsession.id = host
        nsession.host = host
        nsession.lastAlert = time
        nsession.alertTimes = 1
        _sessions[host] = nsession

    def renewSession(self, sid, rule, host, time):
        session = _sessions[sid]
        session.lastAlert = time
        session.alertTimes = 1

    def hitSession(self, sid, rule, host, time):
        session = _sessions[sid]
        session.lastAlert = time
        session.alertTimes += 1

