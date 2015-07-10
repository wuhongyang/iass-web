# coding:utf-8
from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route, list_route, link
from data_vm_utils import VMData, UserData, PlatformData, DepartData, Visitor
from utils import TimePeriod
from data_pm_utils import PhysicalMachineData
import models
import serializers
import datetime
# import logging
from django.db import connection, transaction
from rest_framework.views import APIView


def get_trend(fetchall):
    trend = {}
    trend['value'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    trend['time'] = []
    # filled instance trend time value
    current_time = datetime.datetime.now()
    index = 1
    current_year = current_time.year
    current_month = current_time.month
    trend['time'].append(str(current_year) + '-' + str(current_month))
    while index < 12:
        current_month -= 1
        if current_month == 0:
            current_year -= 1
            current_month = 12
        str_time = str(current_year) + '-' + str(current_month)
        trend['time'].append(str_time)
        index += 1
    # update count value
    for obj in fetchall:
        if obj[1] in trend['time']:
            index = trend['time'].index(obj[1])
            trend['value'][index] = (obj[0])
    return trend


class CMDepartViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CMdeparts
    /departs/     list all departs info
    /departs/count     list all departs count
    /departs/#org_id/       show the specified depart info
    /departs/#org_id/inscount/  show the specified depart instances count
    /departs/#org_id/instances/  show the specified depart instances info
    /departs/#org_id/metrics/?metric=#&period=#  show the specified depart overall metircs
    """
    lookup_field = 'org_id'
    queryset = models.MisUmorg.objects.all()
    serializer_class = serializers.CmOrgSerializer

    @list_route(methods=['get'])
    def count(self, request):
        depart_count = self.queryset.count()
        return Response({"depart_count": depart_count})

    @list_route(methods=['get'])
    def overview(self, request):
        content = []
        for org in self.queryset:
            org_data = {}
            org_data['org_id'] = org.org_id
            org_data['org_name'] = org.org_name
            org_data['user_count'] = models.MisUmuser.objects.filter(org_id=org.org_id).count()
            tp = TimePeriod()
            start_time, end_time = tp.visit('month')
            org_data['month_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, project_id=org.org_id,
                                                                               created_at__lte=end_time,
                                                                               created_at__gte=start_time).count()
            start_time, end_time = tp.visit('quarter')
            org_data['quarter_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, project_id=org.org_id,
                                                                                 created_at__lte=end_time,
                                                                                 created_at__gte=start_time).count()
            start_time, end_time = tp.visit('year')
            org_data['year_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, project_id=org.org_id,
                                                                              created_at__lte=end_time,
                                                                              created_at__gte=start_time).count()
            start_time, end_time = tp.visit('all')
            org_data['total_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, project_id=org.org_id,
                                                                               created_at__lte=end_time,
                                                                               created_at__gte=start_time).count()
            org_data['ticket_count'] = models.WorkOrder.objects.filter(org_id=org.org_id).count()
            content.append(org_data)
        return Response(content)

    @link()
    def user_overview(self, request, org_id):
        content = []
        user_set = models.MisUmuser.objects.filter(org_id=org_id)
        for user in user_set:
            user_data = {}
            user_data['user_id'] = user.user_id
            user_data['user_name'] = user.user_name
            tp = TimePeriod()
            start_time, end_time = tp.visit('month')
            user_data['month_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                                created_at__lte=end_time,
                                                                                created_at__gte=start_time).count()
            start_time, end_time = tp.visit('quarter')
            user_data['quarter_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                                  created_at__lte=end_time,
                                                                                  created_at__gte=start_time).count()
            start_time, end_time = tp.visit('year')
            user_data['year_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                               created_at__lte=end_time,
                                                                               created_at__gte=start_time).count()
            start_time, end_time = tp.visit('all')
            user_data['total_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                                created_at__lte=end_time,
                                                                                created_at__gte=start_time).count()
            user_data['ticket_count'] = models.WorkOrder.objects.filter(user_id=user.user_id).count()
            content.append(user_data)
        return Response(content)

    @link()
    def inscount(self, request, org_id):
        try:
            tenantid = self.queryset.get(pk=org_id)
            instance_count = models.CmUserInstaMapping.objects.filter(project_id=org_id, is_vm=1).count()
            return Response({"instance_count": instance_count})
        except models.MisUmorg.DoesNotExist:
            raise Http404

    @link()
    def users(self, request, org_id):
        try:
            users_set = models.MisUmuser.objects.filter(org_id=org_id)
            users_serializer = serializers.CmUserSerializer(users_set, many=True)
            return Response(users_serializer.data, status=status.HTTP_200_OK)
        except models.MisUmorg.DoesNotExist:
            raise Http404

    @link()
    def instances(self, request, org_id):
        try:
            instance_set = models.CmUserInstaMapping.objects.filter(project_id=org_id, is_vm=1)
            instance_serilizer = serializers.CmUserInstaMapSerializer(instance_set, many=True)
            return Response(instance_serilizer.data, status=status.HTTP_200_OK)
        except models.CmUserInstaMapping.DoesNotExist:
            raise Http404

    @link()
    def metrics(self, request, org_id):
        try:
            depart = self.queryset.get(org_id=org_id)
            metric = request.GET.get('metric') or 'cpu_usage'
            period = request.GET.get('period') or '1hour'
            visitor = Visitor()
            depart_cls = DepartData(target=org_id, metric=metric, timestamp=period, monitor_type='org')
            depart_data = visitor.visit(depart_cls)
            return Response(depart_data)
        except models.MisUmorg.DoesNotExist:
            raise Http404


class CMUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CMUSERs
    /users/     list all users info
    /users/count     list all users count
    /users/#user_id/       show the specified user info
    /users/#user_id/inscount/  show the specified user instances count
    /users/#user_id/instances/  show the specified user instances info
    /users/#user_id/metrics/?metric=#&period=#  show the specified user overall metircs
    """

    # user_id from mis_user who has no quotas commemt by lijun 2014-10-30
    lookup_field = 'user_id'
    queryset = models.MisUmuser.objects.all()
    serializer_class = serializers.CmUserSerializer

    def retrieve(self, request, user_id=None):
        try:
            user_serializer = serializers.CmUserSerializer(self.queryset.get(user_id=user_id))
            # get instance and ticket counts
            instance_count = models.CmUserInstaMapping.objects.filter(user_id=user_id, is_vm=1).count()
            user_serializer.data["instance_count"] = instance_count
            ticket_count = models.WorkOrder.objects.filter(user_id=user_id).count()
            user_serializer.data["ticket_count"] = ticket_count
            # get instance and ticket trend for recent year
            cursor = connection.cursor()
            instance_sql = "select count(*) as counts,concat(cast(year(created_at) as char),'-',cast(month(created_at) as char)) as time from mappings where user_id=%s and is_vm=1 group by year(created_at), month(created_at) limit 12"
            cursor.execute(instance_sql, user_id)
            instance_counts = cursor.fetchall()
            user_serializer.data['instance_trend'] = get_trend(instance_counts)
            ticket_sql = 'select count(*) as counts,concat(cast(year(commit_time) as char),"-",cast(month(commit_time) as char)) as time from work_order where user_id=%s  group by year(commit_time) desc, month(commit_time) desc limit 12;'
            cursor.execute(ticket_sql, user_id)
            user_counts = cursor.fetchall()
            user_serializer.data['ticket_trend'] = get_trend(user_counts)

            return Response(user_serializer.data)
        except models.MisUmuser.DoesNotExist:
            raise Http404

    @list_route(methods=['get'])
    def overview(self, request):
        content = []
        for user in self.queryset:
            user_data = {}
            user_data['user_name'] = user.user_name
            tp = TimePeriod()
            start_time, end_time = tp.visit('month')
            user_data['month_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                                created_at__lte=end_time,
                                                                                created_at__gte=start_time).count()
            start_time, end_time = tp.visit('quarter')
            user_data['quarter_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                                  created_at__lte=end_time,
                                                                                  created_at__gte=start_time).count()
            start_time, end_time = tp.visit('year')
            user_data['year_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                               created_at__lte=end_time,
                                                                               created_at__gte=start_time).count()
            start_time, end_time = tp.visit('all')
            user_data['total_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, user_id=user.user_id,
                                                                                created_at__lte=end_time,
                                                                                created_at__gte=start_time).count()
            content.append(user_data)
        return Response(content)

    @list_route(methods=['get'])
    def count(self, request):
        user_count = self.queryset.count()
        return Response({"user_count": user_count})


    @link()
    def inscount(self, request, user_id):
        try:
            userset = self.queryset.get(pk=user_id)
            instance_count = models.CmUserInstaMapping.objects.filter(user_id=user_id, is_vm=1).count()
            return Response({"instance_count": instance_count})
        except models.MisUmuser.DoesNotExist:
            raise Http404

    @link()
    def instances(self, request, user_id):
        try:
            instance_set = models.CmUserInstaMapping.objects.filter(user_id=user_id, is_vm=1)
            instance_serilizer = serializers.CmUserInstaMapSerializer(instance_set, many=True)
            return Response(instance_serilizer.data, status=status.HTTP_200_OK)
        except models.CmUserInstaMapping.DoesNotExist:
            raise Http404

    @link()
    def metrics(self, request, user_id):
        try:
            user = self.queryset.get(user_id=user_id)
            metric = request.GET.get('metric') or 'cpu_usage'
            period = request.GET.get('period') or '1hour'
            visitor = Visitor()
            user_cls = UserData(target=user_id, metric=metric, timestamp=period, monitor_type='user')
            user_data = visitor.visit(user_cls)
            return Response(user_data)
        except models.MisUmuser.DoesNotExist:
            raise Http404


class CmHostViewset(viewsets.ReadOnlyModelViewSet):
    """
    CMHosts
    /hosts/     list all hosts info
    /hosts/count     list all hosts count
    /users/#host_ip/       show the specified host info
    /users/#host_ip/inscount/  show the specified host instances count
    /users/#host_ip/instances/  show the specified host instances info
    /users/#host_ip/metrics/?metric=#&period=#  show the specified host overall metircs
    """
    lookup_field = 'host_ip'
    lookup_value_regex = '[^/]+'
    queryset = models.CmNovaHosts.objects.filter(deleted=0)
    serializer_class = serializers.CmNovaHostsSerializer

    def list(self, request, *args, **kwargs):
        try:
            host_serializer = serializers.CmNovaHostsSerializer(self.queryset, many=True)
            for hostEntry in host_serializer.data:
                instance_set = models.CmUserInstaMapping.objects.filter(host_ip=hostEntry['host_ip'], is_vm=1)
                for instance in instance_set:
                    hostEntry['ecus_used'] += instance.vcpus * instance.ecus_per_vcpu
            return Response(host_serializer.data)
        except:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            host_ip = kwargs['host_ip']
            host_serializer = serializers.CmNovaHostsSerializer(self.queryset.get(host_ip=host_ip))
            for instance in models.CmUserInstaMapping.objects.filter(host_ip=host_serializer.data['host_ip'], is_vm=1):
                host_serializer.data['ecus_used'] += instance.vcpus * instance.ecus_per_vcpu

            result_data = {}
            hostinfo = self.queryset.get(host_ip=host_ip)
            pm_info = PhysicalMachineData().get_host_info(host_ip)
            device_set = models.Device.objects.get(host_ip=host_ip)
            device_ser = serializers.DeviceSerializer(device_set)
            result_data = dict(pm_info.items() + device_ser.data.items() + host_serializer.data.items())
            return Response(result_data)
        except models.CmNovaHosts.DoesNotExist:
            raise Http404

    @list_route(methods=['get'])
    def count(self, request):
        return Response({"host_count": self.queryset.count()})

    @link()
    def inscount(self, request, host_ip):
        try:
            hostinfo = self.queryset.get(host_ip=host_ip)
            instance_count = models.CmUserInstaMapping.objects.filter(host_ip=host_ip, is_vm=1).count()
            return Response({"instance_count": instance_count})
        except models.CmNovaHosts.DoesNotExist:
            raise Http404

    @link()
    def instance(self, request, host_ip):
        try:
            hostinfo = self.queryset.get(host_ip=host_ip)
            instance_set = models.CmUserInstaMapping.objects.filter(host_ip=host_ip, is_vm=1)
            instance_serilizer = serializers.CmUserInstaMapSerializer(instance_set, many=True)
            return Response(instance_serilizer.data, status=status.HTTP_200_OK)
        except models.CmNovaHosts.DoesNotExist:
            raise Http404

    @link()
    def metrics(self, request, host_ip):
        try:
            hostinfo = self.queryset.get(host_ip=host_ip)
            metric = request.GET.get('metric') or 'cpu_usage'
            period = request.GET.get('period') or '1hour'
            '''
            commented for cpu_usage 2014-11-27
            if metric == 'cpu_usage':
                pmdata = PhysicalMachineData().get_data(host_ip, 'cpu_idle', period)
                for i in range(0, len(pmdata['value'])):
                    pmdata['value'][i] = 100 - pmdata['value'][i]
            else:
                pmdata = PhysicalMachineData().get_data(host_ip, metric, period)
          '''
            pmdata = PhysicalMachineData().get_data(host_ip, metric, period)
            return Response(pmdata)
        except:
            raise Http404

    # @link()
    # def pminfo(self, request, host_ip):
    #     try:
    #         result_data = {}
    #         hostinfo = self.queryset.get(host_ip=host_ip)
    #         pm_info = PhysicalMachineData().get_host_info(host_ip)
    #         device_set = models.Device.objects.get(host_ip=host_ip)
    #         device_ser = serializers.DeviceSerializer(device_set)
    #         result_data = dict(pm_info.items() + device_ser.data.items())
    #         return Response(result_data)
    #     except:
    #         raise Http404


class CmInstanceViewset(viewsets.ReadOnlyModelViewSet):
    """
    CMInstances
    /instance/     list all hosts info
    /hosts/count     list all instances count
    /users/#fixed_ip/       show the specified instance info
    /users/#fixed_ip/metrics/?metric=#&period=#  show the specified instance metircs
    """
    lookup_field = 'fixed_ip'
    lookup_value_regex = '[^/]+'
    queryset = models.CmUserInstaMapping.objects.filter(is_vm=1)
    serializer_class = serializers.CmUserInstaMapSerializer

    def retrieve(self, request, fixed_ip=None):
        try:
            instance_serializer = serializers.CmUserInstaMapSerializer(self.queryset.get(fixed_ip=fixed_ip))
            nova_fixed_ip = models.FixedIps.objects.get(address=fixed_ip)
            uuid = nova_fixed_ip.instance_uuid
            fixed_id = nova_fixed_ip.id
            nova_instances = models.Instances.objects.get(uuid=uuid)
            nova_floating_ips = models.FloatingIps.objects.filter(fixed_ip_id=fixed_id)

            power_state_map = {1: '运行', 3: '暂停', 4: '关机'}
            vm_state_map = {'active': '正常', 'suspended': '休眠', 'stopped': '关机'}
            instance_serializer.data['task_state'] = nova_instances.task_state
            if nova_instances.vm_state in vm_state_map.keys():
                instance_serializer.data['vm_state'] = vm_state_map[nova_instances.vm_state]
            else:
                instance_serializer.data['vm_state'] = nova_instances.vm_state

            if nova_instances.power_state in power_state_map.keys():
                instance_serializer.data['power_state'] = power_state_map[nova_instances.power_state]
            else:
                instance_serializer.data['power_state'] = str(nova_instances.power_state)

            instance_serializer.data['floating_ip'] = []
            for floating_ip in nova_floating_ips:
                instance_serializer.data['floating_ip'].append(floating_ip.address)

            instance_serializer.data['created_at'] = nova_instances.created_at
            return Response(instance_serializer.data)
        except models.CmUserInstaMapping.DoesNotExist:
            raise Http404

    @list_route(methods=['get'])
    def count(self, request):
        try:
            content = {}
            period = request.GET.get('period') or 'all'
            tp = TimePeriod()
            start_time, end_time = tp.visit(period)
            content['instance_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, created_at__lte=end_time,
                                                                                 created_at__gte=start_time).count()
            return Response(content)
        except:
            raise Http404

    @link()
    def metrics(self, request, fixed_ip):
        try:
            vm = self.queryset.get(fixed_ip=fixed_ip)
            metric = request.GET.get('metric') or 'cpu_usage'
            period = request.GET.get('period') or '1hour'
            visitor = Visitor()
            vm_cls = VMData(target=fixed_ip, metric=metric, timestamp=period, monitor_type='vm')
            vm_data = visitor.visit(vm_cls)
            return Response(vm_data)
        except:
            raise Http404


class CmPlatformViewset(viewsets.ReadOnlyModelViewSet):
    """
    CMInstances
    /platform/     list the platform overall info
    /platform/metrics/?metric=#&period=#  show the platform overall metircs
    """
    queryset = models.CmUserInstaMapping.objects.filter(is_vm=0)

    def list(self, request):
        content = {}
        content['user_count'] = models.MisUmuser.objects.all().count()
        content['depart_count'] = models.MisUmorg.objects.all().count()
        content['host_count'] = self.queryset.count()
        period = request.GET.get('period') or 'all'
        tp = TimePeriod()
        start_time, end_time = tp.visit(period)
        content['instance_count'] = models.CmUserInstaMapping.objects.filter(is_vm=1, created_at__lte=end_time,
                                                                             created_at__gte=start_time).count()
        content['ticket_count'] = models.WorkOrder.objects.filter(commit_time__lte=end_time,
                                                                  commit_time__gte=start_time).count()
        content['storage_count'] = models.Device.objects.filter(online_time__lte=end_time,
                                                                online_time__gte=start_time,classification=2).count()
        content['network_count'] = models.Device.objects.filter(online_time__lte=end_time,
                                                                online_time__gte=start_time,classification=3).count()
        return Response(content)

    @list_route(methods=['get'])
    def metrics(self, request):
        # try:
        metric = request.GET.get('metric') or 'cpu_usage'
        period = request.GET.get('period') or '1hour'
        visitor = Visitor()
        pf_cls = PlatformData(metric=metric, timestamp=period, monitor_type='hosts')
        pf_data = visitor.visit(pf_cls)
        # logging.info('metirc:  ' + str(pf_data))
        # logging.info('final data:  ' + str(pf_data))
        return Response(pf_data)
        # except:
        # raise  Http404


class CmWorkOrderViewset(viewsets.ReadOnlyModelViewSet):
    """
    CMmWorkOrder
    /orders/     list the order overall info
    /orders/count/?period=#  show the orders count
    """
    queryset = models.WorkOrder.objects.all()
    serializer_class = serializers.WorkOrderSerializer


    @list_route(methods=['get'])
    def count(self, request):
        try:
            content = {}
            period = request.GET.get('period') or 'all'
            tp = TimePeriod()
            start_time, end_time = tp.visit(period)
            content['work_order_count'] = models.WorkOrder.objects.filter(commit_time__lte=end_time,
                                                                          commit_time__gte=start_time).count()
            return Response(content)
        except:
            raise Http404


class CmDeviceViewset(viewsets.ModelViewSet):
    """
    CmDevice
    /devices/     list all devices info
    /devices/<id>/       show the specified devices info
    """
    lookup_field = 'classification'
    lookup_value_regex = '[^/]+'
    queryset = models.Device.objects.all()
    serializer_class = serializers.DeviceSerializer

    @link()
    def info(self, request, classification):
        try:
            device_set = models.Device.objects.filter(classification=classification)
            device_serilizer = serializers.DeviceSerializer(device_set, many=True)
            return Response(device_serilizer.data, status=status.HTTP_200_OK)
        except models.Device.DoesNotExist:
            raise Http404