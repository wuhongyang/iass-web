# encoding: utf-8
'''
Created on 2015年3月10日

@author: mhjlq1989@gmail.com
'''
import logging
import httplib2
import hashlib

from Gmetad.alert.alert_method import AlertMethod

'''
example:
    phone.alert-method {
        phonehost ""
        phoneuser ""
        phonpass ""
    }
'''

def get_alert_method(impid="phone", cfgid="alert-method"):
    return PhoneMethod(impid, cfgid)

def get_md5_value(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest

class PhoneMethod(AlertMethod):

    PHONE_HOST = 'phonehost'
    PHONE_USER = 'phoneuser'
    PHONE_PASS = 'phonepass'

    _cfgDefaults = {
        PHONE_HOST: 'http://api.sms.cn/mt/',
        PHONE_USER: 'duxiu1100',
        PHONE_PASS: 'li5747100duxiu1100',
    }

    def initConfDefaults(self):
        self.cfg = PhoneMethod._cfgDefaults

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        self.cfgHandlers = {
            PhoneMethod.PHONE_HOST: self._parsePhoneHost,
            PhoneMethod.PHONE_USER: self._parsePhoneUser,
            PhoneMethod.PHONE_PASS: self._parsePhonePass,
        }

    def _parsePhoneHost(self, arg):
        ''' Parse the phone host. '''
        self.cfg[PhoneMethod.PHONE_HOST] = arg.strip().strip('"')

    def _parsePhoneUser(self, arg):
        ''' Parse the phone user. '''
        self.cfg[PhoneMethod.PHONE_USER] = arg.strip().strip('"')

    def _parsePhonePass(self, arg):
        ''' Parse the phone pass. '''
        self.cfg[PhoneMethod.PHONE_PASS] = arg.strip().strip('"')

    def _send_msg(self, contacts, sub, content, encode='utf8'):
        '''
        @param contacts: type list ['13732204565',] 
        @param sub: type str
        @param content: type str
        '''
        
        http = httplib2.Http()
        recievers = ','.join(contacts)
        passwd = get_md5_value(self.cfg[PhoneMethod.PHONE_PASS])
        url = self.cfg[PhoneMethod.PHONE_HOST] + "?uid=" + self.cfg[PhoneMethod.PHONE_USER] + "&pwd=" + passwd + "&mobile=" + recievers + "&encode=" + encode + "&content=" + sub
        try:
            response, re_msg = http.request(url, 'POST')
            # re_msg style sms&stat=100&message=发送成功
            return True
        except Exception, e:
            print e
            return False

    def issueAlert(self, msg, sub, contacts):
        '''Called by the alert_plugin find a alert_rule is hit'''
        if contacts is None:
            return

        phones = []
        for i in contacts:
            phones.append(i['phone'])

        self._send_msg(phones, sub, msg)
