# coding:utf-8
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import serializers
import models
import json
from django.db.models import Q


class UserList(APIView):
    def get(self, request):
        '''
        action : 9.6 get users list
        :param request:
        :return:
        '''
        users = models.CmAlarmUser.objects.all()
        serializer = serializers.CmAlarmUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        acrtion: 9.7 create a new alarm user
        :param request:
        :return:
        '''
        serializer = serializers.CmAlarmUserSerializer(data=request.DATA)
        if serializer.is_valid():
            # duplicated user filter
            d_user_count=models.CmAlarmUser.objects.filter(phone=serializer.data["phone"]).count()
            if d_user_count == 0:
                serializer.save()
                #insert default data to mapping table
                mapping_data={}
                mapping_data["alarm_user_id"] = serializer.data["pk"]
                mapping_data["alarm_user_name"] = serializer.data["alarm_user_name"]
                mapping_data["alarm_config"] = 1
                mapping_data["alarm_group_id"] = 1
                mapping_data["alarm_group_name"] = 'group1'
                mapping_serializer = serializers.CmUserGroupMappingSerializer(data=mapping_data)
                if mapping_serializer.is_valid():
                    mapping_serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response("手机号码已经存在!", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    """
    Retrieve, update or delete a alarm_group_user instance.
    """

    def get_object(self, user_id):
        try:
            return models.CmAlarmUser.objects.get(pk=user_id)
        except models.CmAlarmUser.DoesNotExist:
            raise Http404

    def get(self, request, user_id):
        '''
        action: 9.8 get details for specified user
        :param request:
        :param user_id:
        :return:
        '''
        alarm_group = self.get_object(user_id)
        serializer = serializers.CmAlarmUserSerializer(alarm_group)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self, request, user_id):
        '''
        action: 9.9 modify details for specified user
        :param request:
        :param user_id:
        :return:
        '''
        d_user_count=models.CmAlarmUser.objects.filter(~Q(pk=user_id),phone=request.DATA["phone"],).count()
        if d_user_count == 0:
            alarm_group = self.get_object(user_id)
            serializer = serializers.CmAlarmUserSerializer(alarm_group, data=request.DATA)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
             return Response("手机号码已存在!", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        '''
        action: 9.10 delete details for specified user
        :param request:
        :param user_id:
        :return:
        '''
        alarm_group = self.get_object(user_id)
        alarm_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupUserMappingList(APIView):
    def get(self, request):
        '''
        action : 9.1	get alarm groups
        :param request:
        :return:
        '''
        groups =  models.CmAlarmGroup.objects.all()
        serializer = serializers.CmAlarmGroupSerializer(groups, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request):
        '''
        action: 9.2	create alarm groups
        create a alarm group with user bonded
        '''
        post_data = {}
        # insert alarm_group information
        s_alarm_group = serializers.CmAlarmGroupSerializer(data=request.DATA["alarm_group"])
        if s_alarm_group.is_valid():
            alarm_groups =  models.CmAlarmGroup.objects.filter(alarm_group_name=request.DATA["alarm_group"]["alarm_group_name"])
            if alarm_groups.count() == 0:
                s_alarm_group.save()
            else:
                return Response({"error": "重复的报警组名!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "不合理的请求数据!"}, status=status.HTTP_400_BAD_REQUEST)

        # rebuild post data for  CmUserGroupMappingSerializer and save the result
        users = request.DATA["alarm_group_user_mapping"]
        for user in users:
            post_data["alarm_user_id"] = user["alarm_user_id"]
            post_data["alarm_user_name"] = user["alarm_user_name"]
            post_data["alarm_config"] = user["alarm_config"]
            post_data["alarm_group_id"] = s_alarm_group.data["pk"]
            post_data["alarm_group_name"] = s_alarm_group.data["alarm_group_name"]
            serializer = serializers.CmUserGroupMappingSerializer(data=post_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": "OK"}, status=status.HTTP_201_CREATED)


class GroupUserMappingDetail(APIView):
    """
    Retrieve, update or delete a alarm_group_user instance.
    """

    def get_mappings(self, group_id):
        try:
            return  models.CmUserGroupMapping.objects.filter(alarm_group_id=group_id)
        except  models.CmUserGroupMapping.DoesNotExist:
            raise Http404

    def get_group(self, group_id):
        try:
            return  models.CmAlarmGroup.objects.get(pk=group_id)
        except  models.CmAlarmGroup.DoesNotExist:
            raise Http404


    def get(self, request, group_id):
        '''
        for action 9.5	get details for specified group
        :param request:
        :param group_id:
        :return:
        '''
        data = {}
        # get group data for result
        alarm_group = self.get_group(group_id)
        serializer = serializers.CmAlarmGroupSerializer(alarm_group)
        alarm_group_data = serializer.data
        data["alarm_group"] = alarm_group_data
        # get user&&group mapping data for result
        user_group_mappings = self.get_mappings(group_id)
        mapping_serializer = serializers.CmUserGroupMappingSerializer(user_group_mappings, many=True)
        data["alarm_group_user_mapping"] = mapping_serializer.data

        user_pks = []
        for item in user_group_mappings:
            user_pks.append(item.alarm_user_id)
        if len(user_pks) == 0:
            data["alarm_users"] = []
        else:
            alarm_users =  models.CmAlarmUser.objects.filter(pk__in=user_pks)
            user_serializer = serializers.CmAlarmUserSerializer(alarm_users, many=True)
            data["alarm_users"] = user_serializer.data
        return Response(data,status=status.HTTP_200_OK)

    def put(self, request, group_id):
        '''
        action : 9.3	modify specified group details
        :param request:
        :param group_id:
        :return:
        '''
        post_data = {}
        # update data for group table
        alarm_group = self.get_group(group_id)
        s_alarm_group = serializers.CmAlarmGroupSerializer(alarm_group, data=request.DATA["alarm_group"])
        if s_alarm_group.is_valid():
            s_alarm_group.save()
        else:
            return Response({"error": "不合理的请求数据!"}, status=status.HTTP_400_BAD_REQUEST)

        # update data for mapping table
        # rebuild post data for  CmUserGroupMappingSerializer and save the result
        users = request.DATA["alarm_group_user_mapping"]
        for user in users:
            post_data["alarm_user_id"] = user["alarm_user_id"]
            post_data["alarm_user_name"] = user["alarm_user_name"]
            post_data["alarm_config"] = user["alarm_config"]
            post_data["alarm_group_id"] = s_alarm_group.data["pk"]
            post_data["alarm_group_name"] = s_alarm_group.data["alarm_group_name"]

            user_group_mapping =  models.CmUserGroupMapping.objects.get(alarm_group_id=group_id,
                                                                alarm_user_id=user["alarm_user_id"])
            serializer = serializers.CmUserGroupMappingSerializer(user_group_mapping, data=post_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": "OK"}, status=status.HTTP_205_RESET_CONTENT)

    def delete(self, request, group_id):
        '''
        action: 9.4	delete specified group
        :param request:
        :param group_id:
        :return:
        '''
        # delete data from cm_user_group_mapping table
        user_group_mappings = self.get_mappings(group_id)
        user_group_mappings.delete()
        # delete data from cm_group table
        alarm_group = self.get_group(group_id)
        alarm_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserCountView(APIView):
    """
    A view that returns the count of active users.
    """
    def get(self, request, format=None):
        user_count =  models.CmAlarmUser.objects.count()
        content = {'count': user_count}
        return Response(content,status=status.HTTP_200_OK)

class GroupCountView(APIView):
    """
    A view that returns the count of active users.
    """
    def get(self, request, format=None):
        group_count =  models.CmAlarmGroup.objects.count()
        content = {'count': group_count}
        return Response(content,status=status.HTTP_200_OK)