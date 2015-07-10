import logging

'''
session designment:
1. a session has a idle time, if beyond the idle time the session is expired
2. one alert can add one alertTimes in a session, alertTimes beyond the rule alertTimes, it will truely alert, a session alert three times and then session is expired
3. a session has a interval time, the time between the former alert and the next is bigger than the interval time
'''

class AlertSession:
    ''' This is the alert session info to maintained for every alert event '''

    MAX_IDLE = 500               # A session will die if it stay idle for 5 minutes or longer
    INTERVAL = 60                # A session can't alert within 1 minute, a session matched rule.alertTimes then it will truely alert or it will just and one alertTimes in record

    def __init__(self):
        self.id = None           # The Id of this alert session
        self.rule = None         # The hit rule of this session
        self.host = None         # The host to report in this session
        self.lastAlert = None    # The last alert timestamp in this session
        self.alertTimes = 0      # The total alert times in this session

class AlertRule:
    ''' This is the alert rule class to describe the content (condition, level, message) of the rule. '''

    LEVEL_OK = 0                # The OK level
    LEVEL_WARNING = 1            # The WARNING level
    LEVEL_CRITICAL = 2              # The CRITICAL level

    def __init__(self, *arg, **kwarg):
        self.id = kwarg.get('id', None)           # The Id of this alert rule(pk)
        
        self.method = kwarg.get('alarm_method')     # The alert method array(method object),mail or log
            
        if kwarg.has_key('comparison_operator') and kwarg.has_key('threshold'):    # Describe the conditions of the rule(ex:$val > 64)
            self.alertCond = self._getAlertCond(kwarg.get('comparison_operator', None), kwarg.get('threshold', None))
        
        self.alarmProjectId = kwarg.get('alarm_project_id', None)
        self.alarmProjectName = kwarg.get('alarm_project_name', None)
        
        self.metricId = kwarg.get('metric_id', None)       # The metric id(pk)
        self.metricName = kwarg.get('metric_name', None)   # The metric name
        self.metricDesc = kwarg.get('metric_desc', None)   # The metric name in chinese
        
        self.alarmTimes = kwarg.get('alarm_times', None)
        
        self.alarmFrequency = kwarg.get('alarm_frequency', None)  # if beyond the alarm_times then how many times alert
        
        self.alarmLevel = kwarg.get('alarm_level', 1)
        
    def applyTo(self, host):
        ''' Implemented via self.applyCond '''
        return True
    
    def getAlertMessage(self, time, host_ip, level, metric_name, value):
        '''get alert message'''
        msg = "$time $host_ip $level ALERT! The host $metric is beyond the threshold!, now the value is $val, please check it!".replace('$time', time).replace('$host_ip', host_ip).replace('$level', level).replace('$metric', metric_name).replace('$val', value)
        return msg
    
    def _getAlertCond(self, operator, threshold):
        '''
        @return: str(ex:$val > 64)
        '''
        res = None
        try:
            bench_val = float(threshold)
        except ValueError:
            logging.debug('The threshold has a wrong type, it must be a number')
            return None
        if operator in ['>','<','=','<=','>=','!=']:
            res = '$val' + operator + threshold
        return res
        
    
    def check(self, value):
        ''' Check the metric value on this rule '''
        # The metric rule that is pulled from the config file, should look like a
        #  python conditional statement and use the symbol $val as a place holder
        #  for the actual value.
        if self.alertCond is not None:
            condStr = self.alertCond.replace('$val', value)
            # If the evaluation of the metric rule produces a true condition, check pass!
            if eval(condStr):
                return self.alarmLevel

        return AlertRule.LEVEL_OK

