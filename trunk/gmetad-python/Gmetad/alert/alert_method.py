from Gmetad.gmetad_confable import GmetadConfable
import importlib


def get_alert_method(impid, cfgid="alert-method"):
    ''' Get the specified alert method from the factory via cfgid '''
    method_module = importlib.import_module("Gmetad.alert.methods." + impid + "_method")
    return method_module.get_alert_method(impid, cfgid)


class AlertMethod(GmetadConfable):
    ''' This is the base class for all gmetad alert methods. '''

    def issueAlert(self, msg, sub, contacts):
        '''Called by the alert_plugin find a alert_rule is hit'''
        pass

