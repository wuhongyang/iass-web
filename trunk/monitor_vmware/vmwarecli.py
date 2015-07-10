# encoding: utf-8
'''
Created on 2014年9月17日

@author: mhjlq1989@gmail.com
'''
import time
from pysphere import VIServer,VIProperty

_xml_starttag = '<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>'
_xml_dtd = '''<!DOCTYPE GANGLIA_XML [
   <!ELEMENT GANGLIA_XML (GRID|CLUSTER|HOST)*>
      <!ATTLIST GANGLIA_XML VERSION CDATA #REQUIRED>
      <!ATTLIST GANGLIA_XML SOURCE CDATA #REQUIRED>
   <!ELEMENT GRID (CLUSTER | GRID | HOSTS | METRICS)*>
      <!ATTLIST GRID NAME CDATA #REQUIRED>
      <!ATTLIST GRID AUTHORITY CDATA #REQUIRED>
      <!ATTLIST GRID LOCALTIME CDATA #IMPLIED>
   <!ELEMENT CLUSTER (HOST | HOSTS | METRICS)*>
      <!ATTLIST CLUSTER NAME CDATA #REQUIRED>
      <!ATTLIST CLUSTER OWNER CDATA #IMPLIED>
      <!ATTLIST CLUSTER LATLONG CDATA #IMPLIED>
      <!ATTLIST CLUSTER URL CDATA #IMPLIED>
      <!ATTLIST CLUSTER LOCALTIME CDATA #REQUIRED>
   <!ELEMENT HOST (METRIC)*>
      <!ATTLIST HOST NAME CDATA #REQUIRED>
      <!ATTLIST HOST IP CDATA #REQUIRED>
      <!ATTLIST HOST LOCATION CDATA #IMPLIED>
      <!ATTLIST HOST TAGS CDATA #IMPLIED>
      <!ATTLIST HOST REPORTED CDATA #REQUIRED>
      <!ATTLIST HOST TN CDATA #IMPLIED>
      <!ATTLIST HOST TMAX CDATA #IMPLIED>
      <!ATTLIST HOST DMAX CDATA #IMPLIED>
      <!ATTLIST HOST GMOND_STARTED CDATA #IMPLIED>
   <!ELEMENT METRIC (EXTRA_DATA*)>
      <!ATTLIST METRIC NAME CDATA #REQUIRED>
      <!ATTLIST METRIC VAL CDATA #REQUIRED>
      <!ATTLIST METRIC TYPE (string | int8 | uint8 | int16 | uint16 | int32 | uint32 | float | double | timestamp) #REQUIRED>
      <!ATTLIST METRIC UNITS CDATA #IMPLIED>
      <!ATTLIST METRIC TN CDATA #IMPLIED>
      <!ATTLIST METRIC TMAX CDATA #IMPLIED>
      <!ATTLIST METRIC DMAX CDATA #IMPLIED>
      <!ATTLIST METRIC SLOPE (zero | positive | negative | both | unspecified) #IMPLIED>
      <!ATTLIST METRIC SOURCE (gmond) 'gmond'>
   <!ELEMENT EXTRA_DATA (EXTRA_ELEMENT*)>
   <!ELEMENT EXTRA_ELEMENT EMPTY>
      <!ATTLIST EXTRA_ELEMENT NAME CDATA #REQUIRED>
      <!ATTLIST EXTRA_ELEMENT VAL CDATA #REQUIRED>
   <!ELEMENT HOSTS EMPTY>
      <!ATTLIST HOSTS UP CDATA #REQUIRED>
      <!ATTLIST HOSTS DOWN CDATA #REQUIRED>
      <!ATTLIST HOSTS SOURCE (gmond | gmetad) #REQUIRED>
   <!ELEMENT METRICS (EXTRA_DATA*)>
      <!ATTLIST METRICS NAME CDATA #REQUIRED>
      <!ATTLIST METRICS SUM CDATA #REQUIRED>
      <!ATTLIST METRICS NUM CDATA #REQUIRED>
      <!ATTLIST METRICS TYPE (string | int8 | uint8 | int16 | uint16 | int32 | uint32 | float | double | timestamp) #REQUIRED>
      <!ATTLIST METRICS UNITS CDATA #IMPLIED>
      <!ATTLIST METRICS SLOPE (zero | positive | negative | both | unspecified) #IMPLIED>
      <!ATTLIST METRICS SOURCE (gmond) 'gmond'>
]>'''

class VMWareHost(object):
    '''
    host is the hypervisor host, we can get instance's information from hypervisor, the hypervisor is esxi not vcenter
    when i make this code, i always ask myself why do you seperate cpu,mem,disk from a function, because one function can handle it(most logical is common)
    i thought in the future, cpu,mem,disk metric will have more and more different logical, for computing the metric data
    '''
    
    'cpu_usage - 1, cpu_idle - 13, cpu_capacity - 23'
    cpu = [1]
    'mem_usage - 65537, mem_use - 65545, mem_total - 65625'
    mem = [65537,65545,65625]
    'disk_usage'
    disk = [131073]
    'datastoreio_read, datastore_write,numberReadAveraged, numberWriteAveraged 655362,655363,655360,655361,, disk_read 131078, disk_write 131079, disk_usage 131073'
    diskio = [131078,131079]
    'bytesRx, bytesTx, packetsRx, packetsTx'
    networkio = [196618, 196619]
    
    def __init__(self, server, ip):
        self.server = server
        self.ip = ip
        self.host = server.get_hosts()
        self.gmondstarted = str(int(time.time()))
        self.perfman = server.get_performance_manager()
        self.vms = server.get_registered_vms()
    
    def get_cpu_info(self, node, cpu_metric=cpu, host_type=1):
        '''
        get the cpu metric info, cpu metric is include many properties, we just select some of them
            @param node:Managed Object Types, the instance's type, the instance is host or virtual machine
            @param cpu_metric:point the properties of the cpu metric, for example [1,13,23]  stand for cpu_usage, cpu_idle, cpu_capacity
            @return: string, contain the node's metrics data which be formatted(abandon)
        '''
        result = self.perfman.get_entity_statistic(node, cpu_metric)
        metric_data = ''      
        if not result:
            return metric_data
        
        count = 0
        metric_value_count = 0
        
        for data_des in result:
            #print 'vm name is :' + vm.properties.name +' counter:' + data_des.counter +' counter_key:' + data_des.counter_key +' description:' + data_des.description + ' group:' + data_des.group + ' group_description:' + data_des.group_description + ' instance:' + data_des.instance + ' time:' + data_des.time + ' unit:' + data_des.unit + ' unit_description:' + data_des.unit_description + ' value:' + data_des.value
            #TODO metric name select
            metric_name = data_des.group + '_' + data_des.counter
            if data_des.unit == 'percent':
                metric_value =  str(int(data_des.value)/100)
            else:
                metric_value = data_des.value
                
            metric_value_count += int(metric_value)
            count += 1


        metric_value = str(int(metric_value_count/count))
        metric_data += "<METRIC NAME=\"" + metric_name + "\" VAL=\"" + metric_value + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + data_des.unit + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
        metric_data += "<EXTRA_DATA>\n"
        metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + data_des.counter + "\"/>\n"
        metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + data_des.description + "\"/>\n"
        metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + data_des.group + "\"/>\n"
        metric_data += "</EXTRA_DATA>\n"
        metric_data += "</METRIC>\n"
   
        return metric_data
    
    def get_mem_info(self, node, mem_metric=mem):
        '''
        get the mem metric info, mem metric include many properties, we just select some of them
            @param node: Managed Object Types, the instance's type, the instance is host or virtual machine
            @param mem_metric: point the properties of the cpu metric
            @return: string, contain the node's metrics data which be formatted
        '''
        result = self.perfman.get_entity_statistic(node, mem_metric)
        metric_data = ''
        if not result:
            return metric_data
        
        for data_des in result:
            #TODO metric name select
            metric_name = data_des.group + '_' + data_des.counter
            if data_des.unit == 'percent':
                metric_value =  str(int(data_des.value)/100)
            else:
                metric_value = data_des.value
            metric_data += "<METRIC NAME=\"" + metric_name + "\" VAL=\"" + metric_value + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + data_des.unit + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
            metric_data += "<EXTRA_DATA>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + data_des.counter + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + data_des.description + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + data_des.group + "\"/>\n"
            metric_data += "</EXTRA_DATA>\n"
            metric_data += "</METRIC>\n"
            
        return metric_data
    
    
    def get_disk_info(self, node, host_type=1):
        '''
        get the disk metic info, disk metric include capacity and free space
            @param node: the instance is host or virtual machine, has the value of node._disk
            @param host_type: 1 stands for hypervisor, 0 stands for virtual machine
            @return: string, contain the node's metrics data which be formatted
        '''
        if host_type == 1:
            metric_data = ''
            metric_capacity = 0
            metric_free = 0
            for ds_mor in self.server.get_datastores():
                props = VIProperty(self.server, ds_mor)
                metric_capacity += props.summary.capacity
                metric_free += props.summary.freeSpace
            metric_data += "<METRIC NAME=\"" + 'disk_total' + "\" VAL=\"" + str(metric_capacity) + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + 'Bytes' + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
            metric_data += "<EXTRA_DATA>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + 'disk_total' + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + 'disk_total' + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + 'disk' + "\"/>\n"
            metric_data += "</EXTRA_DATA>\n"
            metric_data += "</METRIC>\n"
            metric_data += "<METRIC NAME=\"" + 'disk_free' + "\" VAL=\"" + str(metric_free) + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + 'Bytes' + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
            metric_data += "<EXTRA_DATA>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + 'disk_total' + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + 'disk_total' + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + 'disk' + "\"/>\n"
            metric_data += "</EXTRA_DATA>\n"
            metric_data += "</METRIC>\n"
        else:
            metric_data = ''
            metric_capacity = 0
            for vdisk in node._disks:
                metric_capacity += vdisk['capacity']
            metric_data += "<METRIC NAME=\"" + 'disk_total' + "\" VAL=\"" + str(metric_capacity) + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + 'Bytes' + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
            metric_data += "<EXTRA_DATA>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + 'disk_total' + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + 'disk_total' + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + 'disk' + "\"/>\n"
            metric_data += "</EXTRA_DATA>\n"
            metric_data += "</METRIC>\n"
        return metric_data
    
    
    def get_diskio_info(self, node, host_type=1, diskio_metric=diskio):
        '''
        get the diskio metic info, diskio metric include many properties, select some of them
            @param node: Managed Object Types, the instance's type, the instance is host or virtual machine
            @param host_type: 1 stands for hypervisor, 0 stands for virtual machine
            @param diskio_metric: point the properties of the diskio metric
            @return: string, contain the node's metrics data which be formatted
        '''
        result = self.perfman.get_entity_statistic(node, diskio_metric)
        metric_data = ''
        
        if not result:
            return metric_data
        
        if host_type == 1:
            for data_des in result:
                #host name is always null, i guess TODO
                if data_des.instance == '':
                    metric_name = data_des.group + '_' + data_des.counter
                    if data_des.unit == 'percent':
                        metric_value =  str(int(data_des.value)/100)
                    else:
                        metric_value = data_des.value
                    
                    metric_data += "<METRIC NAME=\"" + metric_name + "\" VAL=\"" + metric_value + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + data_des.unit + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
                    metric_data += "<EXTRA_DATA>\n"
                    metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + data_des.counter + "\"/>\n"
                    metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + data_des.description + "\"/>\n"
                    metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + data_des.group + "\"/>\n"
                    metric_data += "</EXTRA_DATA>\n"
                    metric_data += "</METRIC>\n"
                
        else:
            reduce_data = []
            for data_des in result:
                # disk object instance deduplication
                if data_des.counter not in reduce_data:
                    reduce_data.append(data_des.counter)
                else:
                    continue
                
                metric_name = data_des.group + '_' + data_des.counter
                if data_des.unit == 'percent':
                    metric_value =  str(int(data_des.value)/100)
                else:
                    metric_value = data_des.value
                    
                metric_data += "<METRIC NAME=\"" + metric_name + "\" VAL=\"" + metric_value + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + data_des.unit + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
                metric_data += "<EXTRA_DATA>\n"
                metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + data_des.counter + "\"/>\n"
                metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + data_des.description + "\"/>\n"
                metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + data_des.group + "\"/>\n"
                metric_data += "</EXTRA_DATA>\n"
                metric_data += "</METRIC>\n"
        
        return metric_data
    
    
    def get_network_info(self, node, network_metric=networkio):
        '''
        get the networkio metic info, networkio metric include many properties, select some of them
            @param node: Managed Object Types, the instance's type, the instance is host or virtual machine
            @param network_metric: point the properties of the network metric
            @return: string, contain the node's metrics data which be formatted
        '''
        result = self.perfman.get_entity_statistic(node, network_metric)
        metric_data = ''
        if not result:
            return metric_data
        
        i = 0
        reduce_data = []
        
        for data_des in result:
            i = i+1
            if data_des.counter not in reduce_data:
                reduce_data.append(data_des.counter)
        
        for counter in reduce_data:
            metric_value = 0
            
            for data_des in result:
                if data_des.counter == counter:
                    metric_value += int(data_des.value)
                    metric_name = data_des.group + '_' + data_des.counter
                    metric_unit = data_des.unit
                    metric_des = data_des.description
                    metric_gro = data_des.group
            metric_value = str(metric_value/(i/network_metric.__len__()))
            metric_data += "<METRIC NAME=\"" + metric_name + "\" VAL=\"" + metric_value + "\" TYPE=\"" + 'float' + "\" UNITS=\"" + metric_unit + "\" TN=\"18\" TMAX=\"60\" DMAX=\"600\" SLOPE=\"both\">\n"
            metric_data += "<EXTRA_DATA>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"TITLE\" VAL=\"" + counter + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"DESC\" VAL=\"" + metric_des + "\"/>\n"
            metric_data += "<EXTRA_ELEMENT NAME=\"GROUP\" VAL=\"" + metric_gro + "\"/>\n"
            metric_data += "</EXTRA_DATA>\n"
            metric_data += "</METRIC>\n"
                
        return metric_data
    
    def get_host_xml(self):
        
        update_at = str(int(time.time()))
        rbuf = ''
        # set host's tag(host is hypervisor)
        for host in self.host.keys():
            host_data = self.get_cpu_info(host)
            if host_data:
                rbuf += "<HOST NAME=\"" + self.ip + "\" IP=\"" + self.ip + "\" TAGS=\"\" REPORTED=\"" + update_at + "\" TN=\"25\" TMAX=\"20\" DMAX=\"0\" LOCATION=\"unspecified\" GMOND_STARTED=\"" + self.gmondstarted + "\">\n"
                # set host's metrics tag(host is hypervisor)
                rbuf += host_data
                rbuf += self.get_mem_info(host)
                rbuf += self.get_disk_info(host, host_type=1)
                rbuf += self.get_diskio_info(host, host_type=1)
                rbuf += self.get_network_info(host)                
                rbuf += "</HOST>\n"
        
        # set host's tag(host is virtual machine)
        for vmpath in self.vms:
            vm = self.server.get_vm_by_path(vmpath)
            vm_name = self.ip + '_' + vm.properties.name
            vm_metric = self.get_cpu_info(vm._mor)
            # whether host is append or not is judge by cpu_metric is get or not
            if vm_metric:
                rbuf += "<HOST NAME=\"" + vm_name + "\" IP=\"" + 'NAN' + "\" TAGS=\"\" REPORTED=\"" + update_at + "\" TN=\"25\" TMAX=\"20\" DMAX=\"0\" LOCATION=\"unspecified\" GMOND_STARTED=\"" + self.gmondstarted + "\">\n"
                rbuf += vm_metric
                rbuf += self.get_mem_info(vm._mor)
                rbuf += self.get_disk_info(vm, host_type=0)
                rbuf += self.get_diskio_info(vm._mor, host_type=0)
                rbuf += self.get_network_info(vm._mor)
                rbuf += "</HOST>\n"
                      
        return rbuf
    
def wrapper_title(rbuf):
    '''
    wrapper a title before the contxt, the title is cluster and state
        @param rbuf: string object formatted as xml style, contain the information of hosts
        @return wbuf: the whole xml  
    '''
    update_at = str(int(time.time()))
    wbuf = "%s\n%s\n"%(_xml_starttag, _xml_dtd)
    # set ganglia xml tag
    wbuf += "<GANGLIA_XML VERSION=\"3.3.8\" SOURCE=\"gmond\">\n"
    # set cluster tag
    wbuf += "<CLUSTER NAME=\"VMware-instances\" LOCALTIME=\"" + update_at +"\" OWNER=\"unspecified\" LATLONG=\"unspecified\" URL=\"unspecified\">\n"
        
    #add the hosts information
    wbuf += rbuf
        
    wbuf += "</CLUSTER>\n"
    wbuf += "</GANGLIA_XML>\n"
        
    return wbuf

def get_connection(host_ip, username, password):
    server = VIServer()
    if host_ip is not None and username is not None and password is not None:
        server.connect(host_ip, username, password)
    else:
        return None
    return server

def close_connection(server):
    try:
        server.disconnect()
    except Exception as ex:
        raise ex

def profileTest():
    server = get_connection("10.10.82.247", "root", "P@ssw0rd")
    vmhost = VMWareHost(server, "10.10.82.247")
    print vmhost.get_host_xml()

#if __name__ == '__main__':
#    profile.run("profileTest()")
