import logging

from Gmetad.alert.alert_method import AlertMethod


def get_alert_method(impid="log", cfgid="alert-method"):
    return LogMethod(impid, cfgid)

class LogMethod(AlertMethod):

    def issueAlert(self, msg, sub, contacts):
        '''Called by the alert_plugin find a alert_rule is hit'''
        for contact in contacts:
            logging.info("%s-----%s" % (msg, contact['alarm_user_name']))

    def initConfDefaults(self):
        '''Init the default values of configs'''
        pass

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        pass

