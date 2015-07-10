from __future__ import division
from django.http import HttpResponse
import json
import rrdtool, collections, time, ConfigParser, logging, os
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rrdapi.forms import RRDForm
import models
from django.conf import settings
import pdb

class RRD:
    def __init__(self):
        pass

    resolution = None
    cf = None
    time_format = None
    metric_file = None
    metric = None
    data = None
    end_time = 'now'
    timestamp = None

    def rra_mapping(self, timestamp):
        cp = ConfigParser.ConfigParser()
        conf_dir = os.path.dirname(__file__)
        conf_file = os.path.join(conf_dir, 'rra_api.conf')
        cp.read(conf_file)
        if timestamp in cp.sections():
            self.resolution = cp.get(timestamp, "resolution")
            self.cf = cp.get(timestamp, "cf")
            self.time_format = cp.get(timestamp, "time_format")

    def set_metric_file(self,monitor_type, target, metric):
        if monitor_type == "vm":
            target = settings.RRD_BASE_PATH + "HOST-VMS/" + target
        elif monitor_type == "vmware":
            target = settings.RRD_BASE_PATH + "VMware-instances/" + target
        elif monitor_type == "user":
            # mis_user =models.MisUmuser.objects.get(pk=target)
            # mis_org = models.MisUmorg.objects.get(pk = mis_user.org_id)
            target = settings.RRD_BASE_PATH + "GroupSummary/user/" + target
        elif monitor_type == "org":
            # mis_org = models.MisUmorg.objects.get(pk=target)
            target = settings.RRD_BASE_PATH + "GroupSummary/depart/" + target
        else:
            target = settings.RRD_BASE_PATH + "HOST-VMS/__SummaryInfo__"

        metric_file = target + "/" + metric + ".rrd"
        return metric_file


    def single_or_muli(self,tuple_value):
        if len(tuple_value) == 1:
            return tuple_value[0]
        else:
            return tuple_value

    def single_or_muli_none(self,tuple_value):
        if len(tuple_value) == 1:
            return 0
            # if self.metric == 'cpu_idle':
            #     return 100
            # else:
            #     return 0
        else:
            return 0, 1
            # if self.metric == 'cpu_idle':
            #     return 100, 1
            # else:
            #     return 0, 1
    @property
    def calc_final_data_echart(self):
        '''
        Comment: self.data format example:
        ((1410739200, 1413417600, 86400), ('sum', 'num'), [(None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (None, None), (198.4215866152919, 2.0), (198.42999999999472, 2.0), (198.42999999999472, 2.0), (198.42999999999483, 2.0), (None, None)])
        :return:
        '''
        try:
            if not os.path.exists(self.metric_file):
                return 'Can\'t fetch the specific rrd data file , please check your params!'
            self.data = rrdtool.fetch(self.metric_file.encode("utf-8"), self.cf.encode("utf-8"), "--resolution",
                                      self.resolution.encode("utf-8"),
                                      "--start", self.start_time.encode("utf-8"), "--end", self.end_time)
            instance_datas = collections.OrderedDict()
            instance_datas["time"] =[]
            instance_datas["value"] = []
            if not hasattr(self, 'data'):
                return 'Can\'t fetch the data, please check your params!'
            starttime = self.data[0][0]
            endtime = self.data[0][1]
            step = self.data[0][2]
            timelists = range(starttime + step, endtime + step, step)
            time_str_lists = []
            result_lists = []
            value = self.data[2]

            flag = False  # flag is for reverse None data values filtering
            data_value = None
            none_count = 0
            for i in range(len(value) - 1, -1, -1):
                # comment: range(1,5,1) --> [1, 2, 3, 4]
                if value[i][0] is None and flag is False:
                    none_count += 1
                    # if continuous None values more than five counts , set the flag to true
                    if none_count >= 5:
                        flag = True
                    continue
                elif value[i][0] is None and flag is True:
                    # set the default value for None data
                    data_value=self.single_or_muli_none(value[i])
                else:
                    flag = True
                    # summary data values: rra [sum]/[num], normal data values: rra [sum]
                    data_value = self.single_or_muli(value[i])
                time_time = time.localtime(timelists[i])
                time_str_lists.append(time.strftime(self.time_format, time_time))
                # convert round style for specific metric
                # modified by lijun 2015-1-16
                if self.metric == 'bytes_in' or  self.metric == 'bytes_out':
                    if isinstance(data_value,tuple):
                        data_value =(round(data_value[0]/1024,2), data_value[1])
                    else:
                        data_value = round(data_value/1024,2)

                result_lists.append(data_value)
            # if [1sec] section selected , return the last date
            if self.timestamp == '1sec':
                instance_datas["time"].append(time_str_lists[0])
                instance_datas["value"].append(result_lists[0])
            else:
                time_str_lists.reverse()
                result_lists.reverse()
                instance_datas["time"] = time_str_lists
                instance_datas["value"] = result_lists
            return instance_datas
        except Exception as err:
            # logging.error(err)
            raise err


    def check_params(self, form):
        """
        check post form data ,and rebuild the parameters as required
        :type self: object
        """
        # logging.info("  begin to check form parameters...")
        monitor_type = form.cleaned_data["monitor_type"]
        target = form.cleaned_data["target"]
        self.metric = form.cleaned_data["metric"]
        self.timestamp = form.cleaned_data["timestamp"]
        self.rra_mapping(self.timestamp)
        # specify monitor_type hypervisor ,vms or user, maybe different path
        self.metric_file = self.set_metric_file(monitor_type, target, self.metric)
        #fetch timestamp format
        if self.timestamp == '1sec':
            self.start_time = "end-10min"
        else:
            self.start_time = "end-" + self.timestamp

class RRDDataDetail(APIView):
    """
    Get rrd data.
    """
    def post(self, request, format=None):
        # logging.debug(request.DATA)
        form = RRDForm(request.DATA)
        serializer = None
        if form.is_valid():
            rrd = RRD()
            rrd.check_params(form)
            rrd_data = rrd.calc_final_data_echart
            return HttpResponse(json.dumps(rrd_data), content_type='application/json', status=status.HTTP_200_OK)
        else:
            # logging.error("form is not valid!")
            return Response("form is not valid!", status=status.HTTP_400_BAD_REQUEST)

