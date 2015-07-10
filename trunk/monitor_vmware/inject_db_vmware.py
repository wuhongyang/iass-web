# encoding: utf-8
'''
Created on 2014年9月22日

@author: mhjlq1989@gmail.com
'''
from pysphere import VIServer
from pysphere import MORTypes
import MySQLdb

mysql_ip = '10.10.82.248'
mysql_user = 'root'
mysql_passwd = 'root'
mysql_port = 3306
mysql_db = 'mapdb'
connection_info = {'ip':mysql_ip,'user':mysql_user,'passwd':mysql_passwd,'port':mysql_port}

def connect_esxi(host_ip, username, password):
    '''
    get base information from esxi
    @param host_ip: vmware esxi host's ip
    @param username: vmware esxi host's super username
    @param password: vmware esxi host's password
    @return: vmware esxi host's object  
    '''
    server = VIServer()
    try:
        server.connect(host_ip, username, password)
    except Exception as ex:
        server = None
        print ex
    return server

def disconnect_esxi(server):
    server.disconnect()

def connect_db(connection_info=None, database=mysql_db):
    '''
    by default it's mysql database
    @param connection_info: dictonary type, must has some k(ip,user,passwd,port)
    @param database: database name
    @return: connection 
    '''
    ip = connection_info.get('ip', None)
    user = connection_info.get('user', None)
    passwd = connection_info.get('passwd', None)
    port = connection_info.get('port', None)
    try:
        conn = MySQLdb.connect(host=ip,user=user,passwd=passwd,port=port,db=database,charset='utf8')
    except Exception as ex:
        print ex
    
    return conn

def disconnect_db(conn):
    try:
        conn.close()
    except Exception as ex:
        print ex

def get_cursor(conn):
    '''
    get mysql cursor
    '''
    try:
        cursor = conn.cursor()
    except Exception as ex:
        print ex
        
    return cursor

def release_cursor(cursor):
    '''
    release mysql cursor
    '''
    try:
        cursor.close()
    except Exception as ex:
        print ex

def get_host_data(cursor = None):
    '''
    get the host information
    @param cursor: mysql's cursor from connection object, usually call the function execute to run sql
    @return: hosts' basical information, host_ip,host_user,host_pwd(inserted by administrator manually)
    '''
    hosts = []
    
    sql = 'select host_ip,host_user,host_password from vmware_host'
    cursor.execute(sql)
    
    for row in cursor.fetchall():
        temp_data = dict()
        temp_data['host_ip'] = row[0]
        temp_data['host_user'] = row[1]
        temp_data['host_pwd'] = row[2]
        hosts.append(temp_data)
        
    return hosts

def get_host_detail(server):
    '''
    get vmware esxi host information, include cpu,mem
    @param server: vmware esxi host object
    @return: vmware esxi host detail information, can insert into table vmware_host
    '''
    #get vmware esxi host's cpu information, and mem information 
    properties = ['hardware.cpuInfo.hz','hardware.cpuInfo.numCpuCores','hardware.cpuInfo.numCpuPackages','hardware.cpuInfo.numCpuThreads','hardware.memorySize']
    results = server._retrieve_properties_traversal(property_names=properties, obj_type=MORTypes.HostSystem)
    host_info = {}
    for result in results:
        for p in result.PropSet:
            value = p.Val
            if p.Name == 'hardware.cpuInfo.hz' or p.Name == 'hardware.memorySize':
                value = str(p.Val/(1024*1024*1024))
            host_info[p.Name] = value
    
    final_info = {}
    final_info['cpu'] = "("+str(host_info['hardware.cpuInfo.numCpuPackages'])+"*"+str(host_info['hardware.cpuInfo.numCpuCores'])+") * "+host_info['hardware.cpuInfo.hz']+"GHz"
    final_info['mem'] = str(host_info['hardware.memorySize'])+"GB"
    
    return final_info
    
def get_vm_detail(server, host_ip, host_name):
    '''
    get virtual machine detail information
    @param server: vmware esxi host object
    @param host_ip: vmware esxi host's ip
    @param host_name: vmware esxi host's domainname 
    @return: virtual machines' information, include name,cpu,mem,pwState,uptime 
    '''
    #get vm's cpu information, and mem information
    properties = ['name','config.hardware.numCPU','config.hardware.memoryMB','summary.runtime.powerState','summary.quickStats.uptimeSeconds']
    results = server._retrieve_properties_traversal(property_names=properties, obj_type=MORTypes.VirtualMachine)
    vms_info = []
    for result in results:
        vm_info = dict()
        for p in result.PropSet:
            value = p.Val
            if p.Name == 'config.hardware.memoryMB':
                value = str(p.Val) + "MB"
                vm_info['mem'] = value
            elif p.Name == 'name' and host_ip:
                vm_info['name'] = value
            elif p.Name == 'config.hardware.numCPU':
                value = str(value) + "vcpu * 1ecu"
                vm_info['cpu'] = value
            elif p.Name == 'summary.runtime.powerState':
                vm_info['power_state'] = value
            elif p.Name == 'summary.quickStats.uptimeSeconds':
                vm_info['up_time'] = value
            vm_info['host_ip'] = host_ip
            vm_info['host_name'] = host_name
        vms_info.append(vm_info)
    
    return vms_info

def update_host_table(cursor, data):
    '''
    insert the base information into table of host
    @param cursor: mysql's cursor from connection object, usually call the function execute to run sql
    @param data: list type, update vmware_host, host_ip,cpu,mem
    @return: cursor execute return flag 
    '''
    if not isinstance(data, dict) or not data or not data.has_key('host_ip'):
        return
    
    sql = "update `vmware_host` set "
    param = []
    if data.has_key('host_name'):
        sql += 'host_name=%s,'
        param.append(data.get('host_name'))
    if data.has_key('cpu'):
        sql += 'cpu=%s,'
        param.append(data.get('cpu'))
    if data.has_key('mem'):
        sql += 'mem=%s,'
        param.append(data.get('mem'))
    sql = sql[:-1] + ' where host_ip=%s'
    param.append(data.get('host_ip'))
    
    flag = cursor.execute(sql,param)
    
    return flag


def update_vm_table(cursor, data):
    '''
    insert the base information into table of virtual machine
    @param cursor: mysql's cursor from connection object, usually call the function execute to run sql
    @param data: list type, contain virtual machine information, host_ip,host_name,instance_name,cpu,mem,power_state,up_time
    @return: cursor execute return flag 
    '''
    if not isinstance(data, dict) or not data or not data.has_key('name') or not data.has_key('host_ip'):
        return
    
    num = cursor.execute("select * from vmware_instance where instance_name='%s' and host_ip='%s'"%(data.get('name'),data.get('host_ip')))
    
    param = []
    if num > 0:
        sql = "update `vmware_instance` set "
        if data.has_key('host_ip'):
            sql += 'host_ip=%s,'
            param.append(data.get('host_ip'))
        if data.has_key('host_name'):
            sql += 'host_name=%s,'
            param.append(data.get('host_name'))
        if data.has_key('name'):
            sql += 'instance_name=%s,'
            param.append(data.get('name'))
        if data.has_key('cpu'):
            sql += 'cpu=%s,'
            param.append(data.get('cpu'))
        if data.has_key('mem'):
            sql += 'mem=%s,'
            param.append(data.get('mem'))
        if data.has_key('power_state'):
            sql += 'power_state=%s,'
            param.append(data.get('power_state'))
        if data.has_key('up_time'):
            sql += 'up_time=%s,'
            param.append(data.get('up_time'))
        sql = sql[:-1] + ' where instance_name=%s and host_ip=%s'
        param.append(data.get('name'))
        param.append(data.get('host_ip'))
    elif num == 0:
        # instance is not inserted, so we do not to add the logical of property judgements
        sql = "insert `vmware_instance`(`host_ip`,`host_name`,`instance_name`,`cpu`,`mem`,`power_state`,`up_time`) value(%s,%s,%s,%s,%s,%s,%s)"
        param.append(data.get('host_ip',' '))
        param.append(data.get('host_name',' '))
        param.append(data.get('name',' '))
        param.append(data.get('cpu',' '))
        param.append(data.get('mem',' '))
        param.append(data.get('power_state',' '))
        param.append(data.get('up_time',' '))
    
    flag = cursor.execute(sql,param)
    
    return flag

def remove_vm_duplication(cursor, data):
    '''
    remove the vm duplication from mysql database mapdb
    @param cursor:  mysql's cursor from connection object, usually call the function execute to run sql
    @param data: virtual machine's information from esxi hosts 
    '''
    if not data or not isinstance(data, list):
        return
    sql = "select host_ip,instance_name from vmware_instance"
    cursor.execute(sql)
    for row in cursor.fetchall():
        flag = 0
        host_ip = str(row[0])
        instance_name = str(row[1])
        for vm_info in data:
            if host_ip==str(vm_info.get('host_ip')) and instance_name==str(vm_info.get('name')):
                flag = 1
        if flag == 0:
            sql_delete = "delete from vmware_instance where host_ip='%s' and instance_name='%s'"%(row[0],row[1])
            cursor.execute(sql_delete)

def connect_vcenter(host_ip, username, password):
    '''
    deprecated!
    '''
    server = VIServer()
    server.connect(host_ip, username, password)
    vms = server.get_registered_vms()
    hosts = server.get_hosts()
    print hosts
    for vmpath in vms:
        vm = server.get_vm_by_path(vmpath)
        print vm.properties.name

    server.disconnect()

if __name__ == '__main__':
    conn = connect_db(connection_info)
    cursor = get_cursor(conn)
    hosts = get_host_data(cursor)
    vms = []
    for host in hosts:
        vms_info = []
        server = connect_esxi(host['host_ip'], host['host_user'], host['host_pwd'])
        if server is not None:
            hosts_info = get_host_detail(server)
            host_name = server.get_hosts().get('ha-host',None)
            vms_info = get_vm_detail(server, host['host_ip'], host_name)
            hosts_info['host_ip'] = host['host_ip']
            hosts_info['host_name'] = host_name
            # update table vmware_host
            flag = update_host_table(cursor, data=hosts_info)
            if flag:
                conn.commit()
            for vm_info in vms_info:
                flag = None
                # update table vmware_instance
                flag = update_vm_table(cursor, data=vm_info)
                if flag:
                    conn.commit()
        vms.extend(vms_info)
    #TODO delete the vmware_host(we can't) or vmware_instance redundancy, get the data from mysql,then compare it to vms_info
    remove_vm_duplication(cursor, data=vms)
    conn.commit()
    release_cursor(cursor)
    disconnect_db(conn)
