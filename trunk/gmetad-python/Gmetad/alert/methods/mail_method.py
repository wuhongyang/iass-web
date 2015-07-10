import logging
import smtplib
from email.mime.text import MIMEText

from Gmetad.alert.alert_method import AlertMethod

'''
example:
    mail.alert-method {
        mailhost ""
        mailuser ""
        mailfrom ""
        mailpass ""
        enableSSL ""
    }
'''

def get_alert_method(impid="mail", cfgid="alert-method"):
    return MailMethod(impid, cfgid)

class MailMethod(AlertMethod):

    MAIL_HOST = 'mailhost'
    MAIL_USER = 'mailuser'
    MAIL_FROM = 'mailfrom'
    MAIL_PASS = 'mailpass'
    MAIL_SSL = 'enalbleSSL'

    _cfgDefaults = {
        MAIL_HOST: 'smtp.citycloud.com.cn',
        MAIL_USER: 'rdnotifier@citycloud.com.cn',
        MAIL_FROM: 'rdnotifier@citycloud.com.cn',
        MAIL_PASS: 'ccird123',
        MAIL_SSL: True,
    }

    def _send_mail(self, contacts, sub, content):
        '''
        @param contacts: type tuple ('rdnotifier@citycloud.com.cn',) 
        @param sub: type str
        @param content: type str
        '''
        msg = MIMEText(content, _subtype='html', _charset='utf8')
        msg['Subject'] = sub
        msg['From'] = self.cfg[MailMethod.MAIL_FROM]
        msg['To'] = ";".join(contacts)
        try:
            server = smtplib.SMTP_SSL()
            server.connect(self.cfg[MailMethod.MAIL_HOST])
            server.login(self.cfg[MailMethod.MAIL_USER], self.cfg[MailMethod.MAIL_PASS])
            server.sendmail(self.cfg[MailMethod.MAIL_FROM], contacts, msg.as_string())
            server.close()
            return True
        except Exception, e:
            print str(e)
            return False

    def initConfDefaults(self):
        self.cfg = MailMethod._cfgDefaults

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        self.cfgHandlers = {
            MailMethod.MAIL_HOST: self._parseMailHost,
            MailMethod.MAIL_USER: self._parseMailUser,
            MailMethod.MAIL_FROM: self._parseMailFrom,
            MailMethod.MAIL_PASS: self._parseMailPass,
            MailMethod.MAIL_SSL: self._parseMailSSL
        }

    def _parseMailHost(self, arg):
        ''' Parse the mail host. '''
        self.cfg[MailMethod.MAIL_HOST] = arg.strip().strip('"')

    def _parseMailUser(self, arg):
        ''' Parse the mail user. '''
        self.cfg[MailMethod.MAIL_USER] = arg.strip().strip('"')

    def _parseMailFrom(self, arg):
        ''' Parse the mail user. '''
        self.cfg[MailMethod.MAIL_FROM] = arg.strip().strip('"')

    def _parseMailPass(self, arg):
        ''' Parse the mail password. '''
        self.cfg[MailMethod.MAIL_PASS] = arg.strip().strip('"')

    def _parseMailSSL(self, arg):
        ''' Parse the mail password. '''
        strSSL = arg.strip().strip('"')
        if strSSL.lower() == 'false':
            self.cfg[MailMethod.MAIL_SSL] = False

    def issueAlert(self, msg, sub, contacts):
        '''Called by the alert_plugin find a alert_rule is hit'''
        if contacts is None:
            return
        
        emails = []
        for i in contacts:
            emails.append(i['email'])
            
        self._send_mail(emails, sub, msg)

