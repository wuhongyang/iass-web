#encodeing utf-8
import MySQLdb as mysql
import httplib
import urllib
import json
import logging
import string
import pdb
#db = mysql.connect("10.10.82.111","root","cci","mapdb")
db = mysql.connect("10.10.82.248","root","root","mapdb",3306)
cursor = db.cursor()

logging.basicConfig(filename='/root/getMap/monitor.log',level=logging.DEBUG,format = '%(asctime)s - %(levelname)s: %(message)s')


data = {}
hostdata = {}
deletedata = {}


def syncToHost():
	'''
		send the changes of mapping info to the compute nodes
	'''
	logging.info("Starting syncToHost host=%s and uuid=%s",data['host_address'],data['uuid'])
	newdata = {}
	newdata = data
	newdata['created_at'] = ''
	newdata['updated_at'] = ''
	url = data['host_address']
	#print "1---url:%s" % (url)
	httpMethod = 'POST'
	headers = {'Content-type': 'application/json'}
	requestURI = '/sync/'
	conn = httplib.HTTPConnection(url,8000,timeout=3)
	# the tuple data contains the info of the request 
	conn.request(httpMethod,requestURI,json.dumps(newdata),headers)
	response = conn.getresponse()
	conn.close()
	if response.status == 201:
		logging.info("get 201,insetion ok! host=%s, uuid='%s'",url,data['uuid'])
	else:
		logging.info("%d error! failed to insertion,uuid='%s'", response.status, data['uuid'])
	
	
def delete_in_db(info,flag):
	'''
		if the sync operation of delete a vm or a host be done successfully,then 
		we will delete the record of this vm of host in local db del_info_vm or del_info_host
	'''
	logging.info("Starting delete_in_db info=%s and flag = %s", info,flag)
	if flag == 0:
		#delete from the del_info_vm
		sql = "delete from mapdb.del_info_vm where uuid = '%s'" % (info)
		print sql
		try:
			cursor.execute(sql)
			db.commit()
		except mysql.Error, e:
			logging.info("delete from table del_info_vm failed, error%d:%s ", e.args[0], e.args[1])
	else:
		#delete from the del_info_host
		sql = "delete from mapdb.del_info_host where ip = '%s'" % (info)
		try:
			cursor.execute(sql)
			db.commit()
			logging.info("delete_in_db success!")
		except mysql.Error, e:
			logging.info("delete from table del_info_host failed, error%d:%s ",e.args[0],e.args[1])

def deleteRecord(info,flag,hostIp=''):
	'''
		send a delete request to Host Data-APT
		if flag=0,the value of info will be a {uuid} and we will delete a record of a vm
		if flag=1,the value of info will be a {host_ip} and we will delete a record of a host
	'''
	logging.info("Starting deleteRecord info=%s and flag = %s",info,flag)
	if flag == 0:
		#get the fixed_ip of vm
		sql = "select fixed_ip from mapdb.mappings where uuid = '%s'" % (info)
		cursor.execute(sql)
		#check if rest1 is none type or not
		rest1 = cursor.fetchone()
		if rest1 is None:
			logging.info("there is no record of uuid='%s' in table mappings", info)
			delete_in_db(info,flag)
			return
		fixed_ip = rest1[0]
		
		#if hostIp is not null,it means that it is a vm migration,and we will Not delete this record from the mapdb.mappings
		#otherwise we will delete this record from the mapdb.mappings
		if hostIp == '':
			sql = "delete from mapdb.mappings where uuid = '%s'" % (info)
			print sql
			cursor.execute(sql)
			db.commit()
		'''	
		#get the host_ip of vm
		sql = "select host from ops_nova.instances where uuid='%s'" % (info)
		cursor.execute(sql)
		rest1 = cursor.fetchone()
		if rest1 is None:
			logging.info("there is no record of uuid='%s' in table ops_nova.instances", info)
			delete_in_db(info,flag)
			return
		sql = "select host_ip from ops_nova.compute_nodes where hypervisor_hostname='%s'" % (rest1[0])
		cursor.execute(sql)
		rest = cursor.fetchone()
		if rest is None:
			logging.info("there is no record of hypervisor_hostname='%s' in table ops_nova.compute_nodes", rest1[0])
			delete_in_db(info,flag)
			return
		host_ip = rest[0]
		'''
	else:
		fixed_ip = info
		host_ip = info
	'''
	#if hostIp has value , it means that we will delete a record in a old host
	if hostIp != '':
		host_ip = hostIp
	
	logging.info("send request to host:%s and vm with fixed_ip:%s will be delete", host_ip,fixed_ip)
	url = host_ip
	httpMethod = 'DELETE'
	headers = {'Contene-type':'application/json'}
	requestURI = '/sync/'+fixed_ip+'/'
	conn = httplib.HTTPConnection(url,8000,timeout=3)
	conn.request(httpMethod,requestURI,'',headers)
	response = conn.getresponse()
	conn.close()
		
	if response.status == 204:
		logging.info("delete success!fixed_ip=%s",fixed_ip)
		#delete this record from local database
		delete_in_db(info,flag)
	else:
		logging.info("delete failed!error code %d",response.status)
	'''
	delete_in_db(info,flag)

def getVmInfo(uuid):
	'''
		get the full imformation of the instance to update the mapping table
		use uuid the sql the db
	'''
	logging.info("Starting getVmInfo of vm with uuid=%s",uuid)
	try:
		data['uuid'] = uuid
		sql = "select address,id from ops_nova.fixed_ips where instance_uuid = '%s'" % (uuid)
		cursor.execute(sql)
		rest1 = cursor.fetchone()# make sure that the result has just one line
		#check if rest1 is None type or not
		if rest1 is None:
		    data['fixed_ip'] = ''
		else:	
			data['fixed_ip'] = rest1[0]
		#is_vm=1 for vm
		data['is_vm'] = 1
		sql = "select address from ops_nova.floating_ips where fixed_ip_id = %s" % (rest1[1])
		if cursor.execute(sql)==1:
			rest1 = cursor.fetchone()
			data['floating_ip'] = rest1[0]
		else:
			data['floating_ip'] = ''
		sql2 = "select display_name,image_ref,host,user_id,project_id,created_at,updated_at,vcpus,memory_mb,root_gb,availability_zone,ephemeral_gb from ops_nova.instances where uuid='%s'" % (uuid)
		cursor.execute(sql2)
		rest2 = cursor.fetchone()
		data['instance_name'] = rest2[0]
		data['host_name'] = rest2[2]
        # modified by lijun
		#data['user_id'] = rest2[3]
		#data['project_id'] = rest2[4]
		data['created_at'] = rest2[5]
		data['updated_at'] = rest2[6]
		data['vcpus'] = rest2[7]
		data['memory_mb'] = rest2[8]
		data['root_gb'] = rest2[9]
		data['availability_zone'] = rest2[10]
		data['ephemeral_gb'] = rest2[11]
		#get image_name from ops_glance.images
		sql = "select name from ops_glance.images where id='%s'" % (rest2[1])
		cursor.execute(sql)
		rest1 = cursor.fetchone()
		data['os_type']=rest1[0]

        # modified by lijun
		sql_getmis = "select user_id, projectId from mapdb.temp where uuid='%s'" % (data['uuid'])
		cursor.execute(sql_getmis)
		rest_getmis = cursor.fetchone()
		#pdb.set_trace()
		data['user_id'] = rest_getmis[0]
		data['project_id'] = rest_getmis[1]

		# modified by lijun
		#sql3 = "select name from ops_keystone.user where id='%s'" % (data['user_id'])
		sql3 = "select user_name from mapdb.mis_umuser where user_id=%s" % (data['user_id'])
		print sql3
		cursor.execute(sql3)
		rest3 = cursor.fetchone()
		data['user_name'] = rest3[0]
		print "user_name: '%s'" % (data['user_name'])

		# modified by lijun
		#sql4 = "select name from ops_keystone.project where id='%s'" % (data['project_id'])
		sql4 = "select org_name from mapdb.mis_umorg where org_id=%s" % (data['project_id'])
		cursor.execute(sql4)
		rest4 = cursor.fetchone()
		data['project_name']=rest4[0];
		
		#get the value 'ecus per vcpu' from table instance_type_extra_specs
		#get the flavor name of instance with uuid
		sql = "select value from ops_nova.instance_system_metadata where instance_uuid='%s' and `key`='instance_type_name'" % (uuid)
		cursor.execute(sql)
		rest1 = cursor.fetchone()
		#get the instance_type_id  of flavor name
		sql = "select id from ops_nova.instance_types where name = '%s'" % (rest1[0])
		cursor.execute(sql)
		rest1 = cursor.fetchone()
		#get the value of ecus per vcpu
		sql = "select value from ops_nova.instance_type_extra_specs where instance_type_id = %s and `key`='ecus_per_vcpu:'" % (rest1[0])
		cursor.execute(sql)
		rest1 = cursor.fetchone()
		data['ecus_per_vcpu']=long(rest1[0])
		

	except mysql.Error, e:
		logging.info("get vm full info error%d:%s ",e.args[0],e.args[1])

	try:	
		sql5 = "select host_ip from ops_nova.compute_nodes where hypervisor_hostname='%s'" % (data['host_name'])
		cursor.execute(sql5)
		rest5 = cursor.fetchone()
		data['host_address'] = rest5[0]

		#check if the mapping record of this uuid exists or not
		sql6 = "select fixed_ip,host_address from mapdb.mappings where uuid='%s'" % (data['uuid'])
		print sql6
		if cursor.execute(sql6) >= 1:
			myrest = cursor.fetchone()
			old_host = myrest[1]

			#check if old_host equals to new_host or not,to find out whether the vm has beed migrated or not
			if old_host != data['host_address']:
				#vm has been migrated,we will delete the record of this vm in the old host,and insert a new record in the new host
				logging.info("vm has been migrated From %s To %s.",old_host,data['host_address'])
				#deleteRecord(uuid,0,old_host)

			#update the record
			logging.info("update instance in mappings with Instance_Name='%s' uuid=%s ",data['instance_name'],uuid)
			finalsql = "update mapdb.mappings set instance_name='%s',host_address='%s',host_name='%s',user_id='%s',user_name='%s',updated_at=now(),root_gb=%s,ephemeral_gb=%s,memory_mb=%s,vcpus=%s,ecus_per_vcpu=%s,az='%s' where uuid='%s'" % (data['instance_name'],data['host_address'],data['host_name'],data['user_id'],data['user_name'],data['root_gb'],data['ephemeral_gb'],data['memory_mb'],data['vcpus'],data['ecus_per_vcpu'],data['availability_zone'],uuid)
		else:
			#insert this record into mapdb.mappings.
			logging.info("insert a new instance into mappings with uuid=%s ",uuid)
			finalsql = "insert into mapdb.mappings values('%s','%s',%s,'%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,'%s','%s','%s','%s','%s')" % (data['fixed_ip'],data['floating_ip'],data['is_vm'],data['instance_name'],data['uuid'],data['os_type'],data['host_address'],data['host_name'],data['user_id'],data['user_name'],data['root_gb'],data['ephemeral_gb'],data['memory_mb'],data['vcpus'],data['ecus_per_vcpu'],data['availability_zone'],data['project_id'],data['project_name'],data['created_at'],data['updated_at'])
		print finalsql
		cursor.execute(finalsql)
		db.commit()
		
		#if insert success, the dirty record in temp table will be changed to clean, in other word, change the colum 'is_ditry' to 0
		updatesql = "update temp set is_dirty=0,updated_at=now() where uuid='%s'" % (uuid)
		cursor.execute(updatesql)
		db.commit()
		
		#insert a new record of this vm to host machine
		#syncToHost()

	except mysql.Error, e:
		logging.info("get vm full info error%d:%s ",e.args[0],e.args[1])
		db.rollback()

def getHostInfo(ip):
	'''
		get the full information of a physical machine and then 
		store it in the mapping table
	'''
	logging.info("Starting getHostInfo of host with ip:%s",ip)
	try:
		sql = "select hypervisor_hostname,created_at,updated_at from ops_nova.compute_nodes where host_ip='%s'" % (ip)
		cursor.execute(sql)
		result = cursor.fetchone()
		hostdata['fixed_ip'] = ip
		hostdata['host_address'] = ip 
		hostdata['host_name'] = result[0]
		hostdata['created_at'] = result[1]
		hostdata['updated_at'] = result[2]
		#check if the mapping record of this ip exists or not
		sql6 = "select * from mapdb.mappings where fixed_ip='%s'" % (hostdata['fixed_ip'])
		if cursor.execute(sql6) >= 1:
			#update the record
			finalsql = "update mapdb.mappings set host_address='%s',host_name='%s',updated_at=now() where fixed_ip='%s'" % (hostdata['host_address'], hostdata['host_name'], ip)
		else:
			#insert this record into mapdb.mapping table
			finalsql = "insert into mapdb.mappings(fixed_ip,is_vm,host_address,host_name,created_at,updated_at) values('%s',%s,'%s','%s','%s','%s')" % (hostdata['fixed_ip'],0,hostdata['host_address'],hostdata['host_name'],hostdata['created_at'],hostdata['updated_at'])
		#print finalsql
		cursor.execute(finalsql)
		db.commit()
		
		#if insert success, the dirty record in host table will be changed to clean, in other word, change the colum 'is_ditry' to 0
		updatesql = "update mapdb.host set is_dirty=0,updated_at=now() where host_ip='%s'" % (ip)
		cursor.execute(updatesql)
		db.commit()
	except mysql.Error, e:
		logging.info("get vm full info error%d:%s ", e.args[0],e.args[1])
		db.rollback()

if __name__== '__main__':
	'''
		scan database to check if there are any changes in the cloud system need to be sync
	'''

	#get dirty record and update it to mapping table;
	#scan temp table to check vm changes and host changes
	try:
		#print '0 ---#############################'
		#check for vms
		cursor.execute("select * from mapdb.temp where is_dirty=1")
		results = cursor.fetchall()
		for row in results:
			getVmInfo(row[0])
	
		#check for compute nodes
		cursor.execute("select * from mapdb.host where is_dirty=1")
		results = cursor.fetchall()
		for row in results:
			getHostInfo(row[0])
	
		
		#check del_info_host to find host info about to delete
		cursor.execute("select * from mapdb.del_info_host")
		results = cursor.fetchall()
		for row in results:
			deleteRecord(row[0],1)#delete a record of host
			#delete_in_db(row[0],1)
		
		#check del_info_host to find host info about to delete
		cursor.execute("select * from mapdb.del_info_vm")
		results = cursor.fetchall()
		for row in results:
			deleteRecord(row[0],0) #delete a record of a vm
			#delete_in_db(row[0],0)
			
		cursor.close()
		db.close()
	except mysql.Error, e:
		logging.info("Error:unable to fetch data%d:%s", e.args[0],e.args[1])

