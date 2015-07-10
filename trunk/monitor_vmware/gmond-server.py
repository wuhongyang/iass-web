# encoding: utf-8
'''
Created on 2014年10月8日

@author: mhjlq1989@gmail.com
'''

import socket
import threading
import vmwarecli
import MySQLdb
import logging
import sys
import os

from optparse import OptionParser

host = '0.0.0.0'
port = 8565
lock = threading.Lock()
rbuf= ''
mysql_ip = '10.10.82.111'
mysql_user = 'root'
mysql_password = 'cci'
mysql_port = 3306

def socket_server(host=host, port=port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    contxt = None
    while True:
        contxt = response()
        conn,addr = s.accept()
        print 'connection created by ', addr
        if contxt:
            conn.sendall(contxt)
        else:
            conn.sendall('Error!')
        conn.close()
    s.close()

def get_host_data(mysql_ip=None, mysql_user=None, mysql_pwd=None, mysql_port=None):
    hosts = []
    
    conn = MySQLdb.connect(host=mysql_ip,user=mysql_user,passwd=mysql_password,port=mysql_port,db='mapdb',charset='utf8')
    cursor = conn.cursor()
    
    sql = 'select host_ip,host_user,host_password from vmware_host'
    cursor.execute(sql)
    
    for row in cursor.fetchall():
        temp_data = dict()
        temp_data['host_ip'] = row[0]
        temp_data['host_user'] = row[1]
        temp_data['host_pwd'] = row[2]
        hosts.append(temp_data)
    return hosts

def get_data(host_ip, host_user, host_pwd):
    global rbuf
    server = vmwarecli.get_connection(host_ip, host_user, host_pwd)
    vm_host_cli = vmwarecli.VMWareHost(server, host_ip)
    lock.acquire()
    rbuf += vm_host_cli.get_host_xml()
    lock.release()

def response():
    global rbuf
    threads = []
    rbuf = ''
    vmware_hosts = get_host_data(mysql_ip, mysql_user, mysql_password, mysql_port)
    for vm_host in vmware_hosts:
        threads.append(threading.Thread(target=get_data, args=(vm_host['host_ip'], vm_host['host_user'], vm_host['host_pwd'])))
    # start threads to get the information of each host
    for thread in threads:
        thread.start()
    # wait for threads exit
    for thread in threads:
        thread.join()
    contxt = vmwarecli.wrapper_title(rbuf)
    return contxt

def getConfig(args=sys.argv):
    parser = OptionParser()
    parser.add_option('-p', '--pid_file', dest='PID_FILE',
                      help='Write process-id to file', type='string', action='store', default=None)
    parser.add_option('-f', '--foreground', dest='daemonize',
                      help='Run in foreground (don\'t daemonize)', action='store_false')
    (options, args) = parser.parse_args()
    return options

def daemonize():
    UMASK=0
    WORKDIR = '/'
    MAXFD = 1024
    REDIRECT_TO = '/dev/null'
    if hasattr(os, 'devnull'):
        REDIRECT_TO = os.devnull
        
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, 'Daemonize error: %d (%s)' % (e.errno, e.strerror)
    if pid == 0:
        # first child
        os.setsid()
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, 'Daemonize error: %d (%s)' % (e.errno, e.strerror)
        if pid == 0:
            # second child
            os.chdir(WORKDIR)
            os.umask(UMASK)
        else:
            os._exit(0)
    else:
        os._exit(0)
        
        
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if resource.RLIM_INFINITY == maxfd:
        maxfd = MAXFD
    for fd in range(0,maxfd):
        try:
            os.close(fd)
        except OSError:
            pass
            
    os.open(REDIRECT_TO, os.O_RDWR)
    os.dup2(0,1)
    os.dup2(0,2)

if __name__ == '__main__':
    conf = getConfig()
    
    # Determine if the service should be daemonized
    if conf.daemonize:
        #daemonize()
        pass
    
    # Create a PID file if the command line parameter was specified.
    pffd = None
    if conf.PID_FILE is not None:
        try:
            pffd = open(conf.PID_FILE, 'w')
            pffd.write('%d\n'%os.getpid())
            logging.debug('Write the process id %d into file %s'%(os.getpid(),conf.PID_FILE))
            pffd.close()
            pffd = open(conf.PID_FILE, 'r')
        except Exception, e:
            logging.error('Unable to write PID %d to %s (%s)' % (os.getpid(), conf.PID_FILE, e))
            sys.exit()
    
    try:
        socket_server()
    except Exception, e:
        logging.error(e)
    finally:
        if pffd is not None:
            pffd.close()
            os.unlink(conf.PID_FILE)
    