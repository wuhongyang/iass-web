# coding:utf-8
from django.http import Http404
import models, serializers
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route, link
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings


def get_group(group_id):
    try:
        return models.CmAlarmGroup.objects.get(pk=group_id)
    except models.CmAlarmGroup.DoesNotExist:
        raise Http404


def get_project(project_id):
    try:
        return models.CmAlarmProject.objects.get(pk=project_id)
    except models.CmAlarmProject.DoesNotExist:
        raise Http404


def get_alarm_mappings(project_id):
    try:
        return models.CmAlarmMapping.objects.filter(alarm_project_id=project_id)
    except models.CmAlarmMapping.DoesNotExist:
        raise Http404


def get_alarm_rules(project_id):
    try:
        return models.CmAlarmRule.objects.filter(alarm_project_id=project_id)
    except models.CmAlarmRule.DoesNotExist:
        raise Http404


def parser_group_id(str_alarm_group_ids):
    '''
    get group data from group id list
    :param list_alarm_group_ids:
    :return:
    '''
    group_data = []
    list_alarm_group_ids = str_alarm_group_ids.split(",")
    for alarm_group_id in list_alarm_group_ids:
        alarm_group = get_group(alarm_group_id)
        s_alarm_group = serializers.CmAlarmGroupSerializer(alarm_group)
        group_data.append(s_alarm_group.data)
    return group_data


def insert_or_update_rules(alarm_rules, project_id):
    for rule in alarm_rules:
        if rule["id"] == -1:
            model_alarm_rule = models.CmAlarmRule(
            alarm_times = rule["alarm_times"],
            metric_id = rule["metric_id"],
            metric_name = rule["metric_name"],
            metric_desc = rule["metric_desc"],
            alarm_project_name = rule["alarm_project_name"],
            alarm_level = rule["alarm_level"],
            comparison_operator = rule["comparison_operator"],
            threshold = rule["threshold"],
            alarm_method = rule["alarm_method"],
            alarm_frequency = rule["alarm_frequency"],
            alarm_project_id = project_id
            )
        else:
            model_alarm_rule = models.CmAlarmRule(
            id = rule["id"],
            alarm_times = rule["alarm_times"],
            metric_id = rule["metric_id"],
            metric_name = rule["metric_name"],
            metric_desc = rule["metric_desc"],
            alarm_project_name = rule["alarm_project_name"],
            alarm_level = rule["alarm_level"],
            comparison_operator = rule["comparison_operator"],
            threshold = rule["threshold"],
            alarm_method = rule["alarm_method"],
            alarm_frequency = rule["alarm_frequency"],
            alarm_project_id = project_id
            )
        model_alarm_rule.save()

        # rule_data["alarm_times"] = rule["alarm_times"]
        # rule_data["metric_id"] = rule["metric_id"]
        # rule_data["metric_name"] = rule["metric_name"]
        # rule_data["metric_desc"] = rule["metric_desc"]
        # rule_data["alarm_project_name"] = rule["alarm_project_name"]
        # rule_data["alarm_level"] = rule["alarm_level"]
        # rule_data["comparison_operator"] = rule["comparison_operator"]
        # rule_data["threshold"] = rule["threshold"]
        # rule_data["alarm_project_id"] = project_id
        #
        # alarm_methods = rule["alarm_method"]
        # for alarm_method in alarm_methods:
        #     rule_data["alarm_method"] = alarm_method
        #     serializer = serializers.CmAlarmRuleSerializer(data=rule_data)
        #     if serializer.is_valid():
        #         serializer.save()
        #     else:
        #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def insert_alarm_mapping(fixed_ips, project_id, str_alarm_group_ids):
    d_alarm_mappings = get_alarm_mappings(project_id)
    d_alarm_mappings.delete()
    alarm_mapping_data = {}
    for fixed_ip in fixed_ips:
        #models.CmAlarmMapping.objects.filter(alarm_project_id=project_id,fixed_ip=fixed_ip)
        alarm_mapping_data["fixed_ip"] = fixed_ip
        alarm_mapping_data["alarm_project_id"] = project_id
        alarm_mapping_data["alarm_group_ids"] = str_alarm_group_ids
        serializer = serializers.CmAlarmMappingSerializer(data=alarm_mapping_data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_alarm_project_byid(project_id):
    alarm_project = get_project(project_id)
    s_alarm_project = serializers.CmAlarmProjectSerializer(alarm_project)
    # get group result data and append to CmAlarmProjectSerializer data
    s_alarm_project.data["alarm_groups"] = parser_group_id(s_alarm_project.data["alarm_group_ids"])
    '''
    # get alarm mapping data
    alarm_mappings = get_alarm_mappings(project_id)
    s_alarm_mappings = serializers.CmAlarmMappingSerializer(alarm_mappings, many=True)
    alarm_objects = []
    for s_alarm_mapping in s_alarm_mappings.data:
        alarm_objects.append(s_alarm_mapping["fixed_ip"])
    s_alarm_project.data["fixed_ips"] = alarm_objects
    # get alarm rules data
    alarm_rules = get_alarm_rules(project_id)
    s_alarm_rules = serializers.GetCmAlarmRuleSerializer(alarm_rules, many=True)
    s_alarm_project.data["alarm_rules"] = s_alarm_rules.data
   '''

    # get alarm objects
    alarm_mappings = get_alarm_mappings(project_id)
    s_alarm_mappings = serializers.CmAlarmMappingSerializer(alarm_mappings, many=True)
    s_alarm_project.data["fixed_ips"] = []
    for alarm_mapping in s_alarm_mappings.data:
        s_alarm_project.data["fixed_ips"].append(alarm_mapping["fixed_ip"])

    # get alarm rules
    alarm_rules = get_alarm_rules(project_id)
    s_alarm_rules = serializers.GetCmAlarmRuleSerializer(alarm_rules, many=True)
    '''for specific rule express
    s_alarm_project.data["alarm_rules"] = []
    for alarm_rule in s_alarm_rules.data:
        str_rule = alarm_rule["metric_desc"] + alarm_rule["comparison_operator"] + alarm_rule["threshold"]
        dict_rule ={}
        dict_rule['alarm_express'] = str_rule
        dict_rule['alarm_times'] = alarm_rule['alarm_times']
        s_alarm_project.data["alarm_rules"].append(dict_rule)
    '''
    s_alarm_project.data["alarm_rules"]=s_alarm_rules.data
    return s_alarm_project.data



class MappingsList(APIView):
    def get(self, request):
        '''
        action : 10.7 get object list
        :param request:
        :return:
        '''
        users = models.Mappings.objects.all()
        serializer = serializers.MappingsSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MetricsList(APIView):
    def get(self, request):
        '''
        action : 10.9 get metric list
        :param request:
        :return:
        '''
        users = models.CmMetric.objects.all()
        serializer = serializers.CmMetricSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectsList(APIView):
    def post(self, request):
        '''
        action : 10.3 post a new alarm project
        :param request:
        :return:
        '''
        # convert alarm_group_ids list to string with ',' delimiter
        alarm_group_ids = request.DATA["alarm_group_ids"]
        list_alarm_group_ids = []
        for alarm_group_id in alarm_group_ids:
            list_alarm_group_ids.append(str(alarm_group_id))
        str_alarm_group_ids = ",".join(list_alarm_group_ids)
        request.DATA["alarm_project"]["alarm_group_ids"] = str_alarm_group_ids

        # insert alarm_group information
        s_alarm_project = serializers.CmAlarmProjectSerializer(data=request.DATA["alarm_project"])
        if s_alarm_project.is_valid():
            alarm_projects = models.CmAlarmProject.objects.filter(
                alarm_project_name=request.DATA["alarm_project"]["alarm_project_name"])
            if alarm_projects.count() == 0:
                s_alarm_project.save()
            else:
                return Response({"error": "报警项目名称已存在!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "不合理的请求数据!"}, status=status.HTTP_400_BAD_REQUEST)


        # build rule data for  cm_alarm_rule and save the result
        insert_or_update_rules(request.DATA["alarm_rule"], s_alarm_project.data["id"])

        # build alarm mapping data for  cm_alarm_mapping and save the result
        insert_alarm_mapping(request.DATA["fixed_ips"], s_alarm_project.data["id"], str_alarm_group_ids)

        #res_alarm_projet=models.CmAlarmProject.objects.get(id = s_alarm_project.data["id"])
        result = get_alarm_project_byid(s_alarm_project.data["id"])
        return Response(result, status=status.HTTP_201_CREATED)

    def get(self, request):
        '''
        action : 10.1 get alarm project list
        :param request:
        :return:
        '''
        response_data = []
        alarm_projects = models.CmAlarmProject.objects.order_by("-id")
        s_alarm_projects = serializers.CmAlarmProjectSerializer(alarm_projects, many=True)
        for alarm_project_data in s_alarm_projects.data:
            project_id = alarm_project_data["id"]
            # alarm_project_data["alarm_groups"] = parser_group_id(alarm_project_data["alarm_group_ids"])
            # get alarm objects
            alarm_mappings = get_alarm_mappings(project_id)
            s_alarm_mappings = serializers.CmAlarmMappingSerializer(alarm_mappings, many=True)
            alarm_project_data["fixed_ips"] = []
            for alarm_mapping in s_alarm_mappings.data:
                alarm_project_data["fixed_ips"].append(alarm_mapping["fixed_ip"])

            # get alarm rules
            alarm_rules = get_alarm_rules(project_id)
            s_alarm_rules = serializers.GetCmAlarmRuleSerializer(alarm_rules, many=True)
            '''for specific rule express
            alarm_project_data["alarm_rules"] = []
            for alarm_rule in s_alarm_rules.data:
                str_rule = alarm_rule["metric_desc"] + alarm_rule["comparison_operator"] + alarm_rule["threshold"]
                alarm_project_data["alarm_rules"].append(str_rule)
          '''
            alarm_project_data["alarm_rule"] = s_alarm_rules.data

        return Response(s_alarm_projects.data, status=status.HTTP_200_OK)


class ProjectDetail(APIView):
    def get(self, request, project_id):
        '''
        action : 10.2 get project details
        :param request:
        :return:
        '''
        result = get_alarm_project_byid(project_id)
        return Response(result, status=status.HTTP_200_OK)

    def put(self, request, project_id):
        '''
        action: 10.4 update data for specific alarm project
        :param request:
        :param project_id:
        :return:
        '''
        # convert alarm_group_ids list to string with ',' delimiter
        alarm_group_ids = request.DATA["alarm_group_ids"]
        list_alarm_group_ids = []
        for alarm_group_id in alarm_group_ids:
            list_alarm_group_ids.append(str(alarm_group_id))
        str_alarm_group_ids = ",".join(list_alarm_group_ids)
        # add attribute alarm_group_ids for alarm_project data
        request.DATA["alarm_project"]["alarm_group_ids"] = str_alarm_group_ids
        # insert alarm_group information
        alarm_project = get_project(project_id)
        s_alarm_project = serializers.CmAlarmProjectSerializer(alarm_project, data=request.DATA["alarm_project"])
        if s_alarm_project.is_valid():
            s_alarm_project.save()
        else:
            return Response({"error": "不合理的请求数据!"}, status=status.HTTP_400_BAD_REQUEST)

        # delete all the rules for the specific project id
        # d_alarm_rules = get_alarm_rules(project_id)
        # d_alarm_rules.delete()
        # add new rules for the  specific project id
        insert_or_update_rules(request.DATA["alarm_rule"], s_alarm_project.data["id"])
        # delete all the rules for the specific project id
        d_alarm_mappings = get_alarm_mappings(project_id)
        d_alarm_mappings.delete()
        # fetch fixed_ips and insert to alarm_mapping tables
        insert_alarm_mapping(request.DATA["fixed_ips"], s_alarm_project.data["id"], str_alarm_group_ids)

        result = get_alarm_project_byid(project_id)
        return Response(result,status=status.HTTP_200_OK)


    def delete(self, request, project_id):
        '''
        action: 10.5 delete specified project
        :param request:
        :param group_id:
        :return:
        '''
        # delete all the rules for the specific project id
        d_alarm_rules = get_alarm_rules(project_id)
        d_alarm_rules.delete()
        # delete all the rules for the specific project id
        d_alarm_mappings = get_alarm_mappings(project_id)
        d_alarm_mappings.delete()
        # delete alarm project data for the specific project id
        d_alarm_project = get_project(project_id)
        d_alarm_project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlarmHistoryViewset(viewsets.ModelViewSet):
    """
    actions: alarm history viewsets
    """
    queryset = models.CmAlarmHistory.objects.order_by("-alarm_time")
    serializer_class = serializers.CmAlarmHistorySerializer

    @list_route(methods=['get'])
    def month_count(self, request):
        users = models.CmAlarmHistoryMonth.objects.all()
        serializer = serializers.CmAlarmHistoryMonthSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    # @link()
    def verify(self, request, pk):
        try:
            verify_ah = models.CmAlarmHistory.objects.get(pk=pk)
            verify_ah.is_verify = 1
            verify_ah.save()
            rule_id = verify_ah.alarm_rule_id
            fixed_ip = verify_ah.fixed_ip
            models.CmAlarmDisabled.objects.filter(alarm_rule_id=rule_id, fixed_ip=str(fixed_ip)).update(expired=0)
            return Response({"result": "Verify OK!"}, status=status.HTTP_200_OK)
        except:
            return Response({"result": "确认失败!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @list_route(methods=['get'])
    def count(self, request):
        return Response({"count": len(self.queryset)}, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def paginator(self, request):
        '''
        is request param status is 2 ,return all history data
        :param request:
        :return:
        '''
        try:
            verify_status = request.GET.get('status')
            if int(verify_status)==2:
                history_set = self.queryset
            else:
                history_set = self.queryset.filter(is_verify=verify_status)
            offset = request.GET.get('offset') or settings.PAGE_COUNT
            paginator = Paginator(history_set, offset)
            page_index = request.GET.get('index')
            if int(page_index)>paginator.num_pages:
                page_index = 1
            try:
                alarm_historys = paginator.page(page_index)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                alarm_historys = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                alarm_historys = paginator.page(paginator.num_pages)
            serializer = serializers.CmAlarmHistorySerializer(alarm_historys, many=True)
            resp_data ={}
            resp_data['offset']=offset
            resp_data['index'] = page_index
            resp_data['total_page'] = paginator.num_pages
            resp_data['history_data'] =  serializer.data
            #serializer.data["num_pages"] = paginator.num_pages
            return Response(resp_data, status=status.HTTP_200_OK)
        except:
            raise Http404


class ProjectCountView(APIView):
    """
    A view that returns the count of active users.
    """
    def get(self, request, format=None):
        project_count = models.CmAlarmProject.objects.count()
        content = {'count': project_count}
        return Response(content, status=status.HTTP_200_OK)


class allCountView(APIView):
    """
    A view that returns the count of active users.
    """

    def get(self, request, format=None):
        content = {}
        project_count = models.CmAlarmProject.objects.count()
        content['project_count'] = project_count
        history_count = models.CmAlarmHistory.objects.count()
        content['history_count'] = history_count
        user_count = models.CmAlarmUser.objects.count()
        content['user_count'] = user_count
        obj_bond_count = models.CmAlarmMapping.objects.values('fixed_ip').distinct().count()
        content['obj_bonded_count'] = obj_bond_count
        obj_total_count = models.Mappings.objects.count()
        content['obj_total_count'] = obj_total_count
        return Response(content, status=status.HTTP_200_OK)

class RuleDetail(APIView):
    def delete(self, request, rule_id):
        try:
            d_alarm_rules = models.CmAlarmRule.objects.get(id=rule_id)
            d_alarm_rules.delete()
        except models.CmAlarmRule.DoesNotExist:
            raise Http404
        return Response(status=status.HTTP_200_OK)
