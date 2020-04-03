import os
import pickle
import logging
import subprocess
import fcntl
from ops.settings import MEDIA_ROOT, BASE_DIR, VERSION_CONTROL_TYPE, FTP_PORT
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import serializers
from version_control.models import PlatFormVersionModel, OSVersionModel, TerminalVersionModel

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from common.pagination import ResultsSetPaginationOffset1

# Create your views here.

logger = logging.getLogger("ops." + __name__)
FTP_STATUS_PATH = os.path.join(MEDIA_ROOT, 'ftp_status.pk')
FTP_SCRIPT_PATH = os.path.join(BASE_DIR, 'vsftpd')

disable_script = os.path.join(FTP_SCRIPT_PATH, "disable_ops_ftpd.sh")
enable_script = os.path.join(FTP_SCRIPT_PATH, "enable_ops_ftpd.sh")
ftp_config_path = {
    "os": os.path.join(FTP_SCRIPT_PATH, "vsftpd_os.conf"),
    "platform": os.path.join(FTP_SCRIPT_PATH, "vsftpd_platform.conf"),
    "terminal": os.path.join(FTP_SCRIPT_PATH, "vsftpd_terminal.conf")
}


def enable_ftp(config_path, open_mode, port, open_path):
    """
    config ftp server and open it
    :param config_path: config file path
    :param open_mode: upload/download
    :param port: ftp server listen port
    :param open_path: login ftp server root path
    """

    def executor(config_path=config_path, open_mode=open_mode, port=port, open_path=open_path):
        cmd = "sh {} {} {} {} {}".format(enable_script, config_path, open_mode, port, open_path)
        logger.info("begin open ftp")
        logger.info(cmd)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        logger.info(result.returncode)
        logger.info("done")
        return result.returncode, result.stdout, result.stderr

    return executor


def disable_ftp():
    """
    disable the ftp server
    """
    kill_cmd = "sh " + disable_script
    logger.info("begin close ftp")
    logger.info(kill_cmd)
    kill_result = subprocess.run(kill_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)
    logger.info(kill_result.returncode)
    logger.info("done")
    return kill_result.returncode, kill_result.stdout, kill_result.stderr


class FtpStatus:
    """
    通过文件记录ftp服务状态
    """

    def __init__(self, file_path):
        self.path = file_path

    @property
    def ftp_status(self):
        """
        get ftp_status
        :return:
        """

        if not os.path.exists(self.path):
            return 0

        try:
            with open(self.path, 'rb') as f:
                fcntl.lockf(f, fcntl.LOCK_SH)
                ftp_stat = pickle.load(f)
                fcntl.lockf(f, fcntl.LOCK_UN)
        except Exception as err:
            # 0:closed/1:opening
            logger.error(err.args)
            return 0
        else:
            return ftp_stat

    @ftp_status.setter
    def ftp_status(self, stat):
        """
        store ftp_status
        :param stat: int or tuple.
                     if int, it must be 0:closed/1:opening.
                     if tuple, it must be (stat, enable_func), stat is 0:closed/1:opening,
                               enable_func is enable_ftp executor function
        :return:
        """
        if isinstance(stat, (int, tuple)):
            if isinstance(stat, int):
                enable_func = None
            else:
                stat, enable_func = stat
        else:
            raise ValueError("stat format error:{}".format(stat))

        with open(self.path, "wb") as f:
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

            if enable_func is not None:
                result_stat, result_stdout, result_stderr = enable_func()
                if result_stat != 0:
                    # open ftp failed
                    fcntl.lockf(f, fcntl.LOCK_UN)
                    logger.error(result_stderr)
                    raise RuntimeError(result_stderr)

            pickle.dump(stat, f)
            fcntl.lockf(f, fcntl.LOCK_UN)


_ftp_status = FtpStatus(FTP_STATUS_PATH)


class VersionControlFilter(filters.SearchFilter):
    search_param = 'condition'


class PlatformVersionSerializer(serializers.ModelSerializer):
    """
    平台版本序列化器
    """

    class Meta:
        model = PlatFormVersionModel
        fields = "__all__"


class OSVersionSerializer(serializers.ModelSerializer):
    """
    操作系统版本序列化器
    """

    class Meta:
        model = OSVersionModel
        fields = "__all__"


class TerminalVersionSerializer(serializers.ModelSerializer):
    """
    终端版本序列化器
    """

    class Meta:
        model = TerminalVersionModel
        fields = "__all__"


class PlatformVersionView(generics.ListAPIView):
    """
    处理 /api/v1/ops/versions/{file_type}/
    """

    lookup_field = 'pk'
    pagination_class = ResultsSetPaginationOffset1
    # 关键字查询
    filter_backends = (DjangoFilterBackend, VersionControlFilter)
    # filterset_fields = ('status', 'priority')
    # 关键字搜索
    search_fields = ('name',)

    def post(self, request, *args, **kwargs):
        """
        upload, open the ftp server
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_type = kwargs.get('file_type')

        # check if the ftp server running
        ftp_stat_cmd = "netstat -tnlp | grep '%s' | grep 'vsftp' | wc -l" % FTP_PORT
        ftp_stat_result = subprocess.run(ftp_stat_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         universal_newlines=True)
        if ftp_stat_result.returncode == 0:
            if ftp_stat_result.stdout.rstrip() != "0":
                # ftp server is running
                if _ftp_status.ftp_status == 1:
                    # another task is opening
                    return Response({
                        "success": 0,
                        "error_code": 404,
                        "msg": "ftp服务已被占用"})
                else:
                    # close the ftp server first
                    kill_returncode, kill_stdout, kill_stderr = disable_ftp()
                    if kill_returncode != 0:
                        logger.error(kill_stderr)
                        return Response({
                            "success": 0,
                            "error_code": 405,
                            "msg": "ftp服务操作失败"})
            elif ftp_stat_result.stdout.rstrip() == "0":
                # ftp server is not running
                pass
            #  open the ftp server
            ftp_conf = ftp_config_path.get(request_type)
            ftp_root_path = os.path.join(MEDIA_ROOT, "version_control", request_type)
            # ftp_root_path = ftp_root_path.replace("/", "\/")
            func = enable_ftp(ftp_conf, "upload", FTP_PORT, ftp_root_path)
            try:
                _ftp_status.ftp_status = 1, func
            except Exception as err:
                logger.error(err.args)
                return Response({
                    "success": 0,
                    "error_code": 406,
                    "msg": "ftp服务开启失败"})
            else:
                # return success
                return_ip_cmd = 'IFS=" " read -r -a ips <<< "$(hostname -I)"; echo "${ips[@]}"'
                return_ip_result = subprocess.run(return_ip_cmd, shell=True, stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  universal_newlines=True)
                ips = return_ip_result.stdout.split()
                msg = ["ftp://ftp:luban_upload@{}:{}".format(x, FTP_PORT) for x in ips]
                return Response({
                    "success": 1,
                    "msg": msg})
        else:
            logger.error(ftp_stat_result.stderr)
            return Response({
                "success": 0,
                "error_code": 403,
                "msg": "ftp服务开启失败"})

    def put(self, request, *args, **kwargs):
        """
        关闭上传 and scan new files added
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        kill_returncode, kill_stdout, kill_stderr = disable_ftp()
        if kill_returncode != 0:
            logger.error(kill_stderr)
            return Response({
                "success": 0,
                "error_code": 405,
                "msg": "ftp服务操作失败"})
        _ftp_status.ftp_status = 0


        # scan and add new files
        request_type = kwargs.get('file_type')
        scan_path = os.path.join(MEDIA_ROOT, "version_control", request_type)
        index_file_path = os.path.join(MEDIA_ROOT, "version_control", request_type, ".index.pk")
        if os.path.exists(index_file_path):
            with open(index_file_path, 'rb') as f:
                pre_exits_files = pickle.load(f)  # list
        else:
            pre_exits_files = []
        now_exits_files = os.listdir(scan_path)
        if ".index.pk" in now_exits_files:
            now_exits_files.remove(".index.pk")
        new_add_file = set(now_exits_files) - set(pre_exits_files)
        if len(new_add_file) == 0:
            # return direct
            return Response({
                "success": 1,
                "msg": []})

        # save to databases
        try:
            uploader = request.META.get('ssoAuth').get('account')
        except Exception as err:
            uploader = ""
            logger.error(err)
        else:
            if uploader is None:
                uploader = ""

        serializer = self.get_serializer_class()

        uploader = [uploader]*len(new_add_file)
        name = list(new_add_file)  # file name
        file = [os.path.join(scan_path, x) for x in name]
        keys = ['uploader', "file", 'name']
        new_item_dict = [dict(zip(keys, x)) for x in list(zip(uploader, file, name))]
        new_items = serializer(data=new_item_dict, many=True)
        if new_items.is_valid():
            new_objs = new_items.save()
            with open(index_file_path, 'wb') as f:
                pickle.dump(now_exits_files, f)
            new_objs_data = serializer(new_objs, many=True)
            return Response({
                "success": 1,
                "msg": new_objs_data.data})
        else:
            logger.error(new_items.errors)
            return Response({
                "success": 1,
                "msg": []})

    def delete(self, request, *args, **kwargs):
        """
        批量删除版本信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        ids = request.data.get('ids')
        if isinstance(ids, list):
            model_class = self.get_model_class()
            try:
                items = model_class.objects.filter(id__in=ids)
                files = [x.file for x in items]
                items.delete()
                [os.remove(x) for x in files]
            except Exception as err:
                logger.error(err)
                return Response({'success': 0, 'error_code': 403, 'msg': err.args[0]})
            else:
                return Response({'success': 1})
        else:
            return Response({'success': 0, 'error_code': 403, 'msg': "数据格式错误"})

    def get_serializer_class(self):
        request_type = self.kwargs.get('file_type')
        if request_type == 'platform':
            serializer_class = PlatformVersionSerializer
        elif request_type == "os":
            serializer_class = OSVersionSerializer
        else:
            serializer_class = TerminalVersionSerializer
        return serializer_class

    def get_model_class(self):
        request_type = self.kwargs.get('file_type')
        if request_type == 'platform':
            model_class = PlatFormVersionModel
        elif request_type == "os":
            model_class = OSVersionModel
        else:
            model_class = TerminalVersionModel
        return model_class

    def get_queryset(self):
        conditions = self.request.query_params.dict()
        conditions = dict([(k, v) for k, v in conditions.items() if v])

        begin_time = conditions.get('begin_time')
        end_time = conditions.get('end_time')

        query_filter = {}

        if begin_time and end_time:
            query_filter['upload_time__range'] = (begin_time, end_time)
        elif begin_time:
            query_filter['upload_time__gte'] = begin_time
        elif end_time:
            query_filter['upload_time__lte'] = end_time

        queryset = self.get_model_class().objects.filter(**query_filter).order_by('-id')
        return queryset


class PlatformVersionDetailView(generics.RetrieveUpdateAPIView):
    """
    处理 /api/v1/ops/versions/platform/{id}/
    """
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        """
        下载平台版本文件
        open the ftp server and return url
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_type = kwargs.get('file_type')
        request_id = kwargs.get('id')

        # check if the ftp server running
        ftp_stat_cmd = "netstat -tnlp | grep '%s' | grep 'vsftp' | wc -l"%FTP_PORT
        ftp_stat_result = subprocess.run(ftp_stat_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         universal_newlines=True)
        if ftp_stat_result.returncode == 0:
            if ftp_stat_result.stdout.rstrip() != "0":
                # ftp server is running
                if _ftp_status.ftp_status == 1:
                    # another task is opening
                    return Response({
                        "success": 0,
                        "error_code": 404,
                        "msg": "ftp服务已被占用"})
                else:
                    # close the ftp server first
                    kill_returncode, kill_stdout, kill_stderr = disable_ftp()
                    if kill_returncode != 0:
                        logger.error(kill_stderr)
                        return Response({
                            "success": 0,
                            "error_code": 405,
                            "msg": "ftp服务操作失败"})
            elif ftp_stat_result.stdout.rstrip() == "0":
                # ftp server is not running
                pass
            #  open the ftp server
            ftp_conf = ftp_config_path.get(request_type)
            ftp_root_path = os.path.join(MEDIA_ROOT, "version_control", request_type)
            func = enable_ftp(ftp_conf, "download", FTP_PORT, ftp_root_path)
            try:
                _ftp_status.ftp_status = 1, func
            except Exception as err:
                logger.error(err.args)
                return Response({
                    "success": 0,
                    "error_code": 406,
                    "msg": "ftp服务开启失败"})
            else:
                # return success
                return_ip_cmd = 'IFS=" " read -r -a ips <<< "$(hostname -I)"; echo "${ips[@]}"'
                return_ip_result = subprocess.run(return_ip_cmd, shell=True, stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  universal_newlines=True)
                ips = return_ip_result.stdout.split()
                msg = ["ftp://ftp:luban_upload@{}:{}".format(x, FTP_PORT) for x in ips]
                return Response({
                    "success": 1,
                    "msg": msg})
        else:
            logger.error(ftp_stat_result.stderr)
            return Response({
                "success": 0,
                "error_code": 403,
                "msg": "ftp服务开启失败"})

    def put(self, request, *args, **kwargs):
        """
        修改平台版本信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def get_model_class(self):
        request_type = self.kwargs.get('file_type')
        if request_type == 'platform':
            model_class = PlatFormVersionModel
        elif request_type == "os":
            model_class = OSVersionModel
        else:
            model_class = TerminalVersionModel
        return model_class

    def get_serializer_class(self):
        request_type = self.kwargs.get('file_type')
        if request_type == 'platform':
            serializer_class = PlatformVersionSerializer
        elif request_type == "os":
            serializer_class = OSVersionSerializer
        else:
            serializer_class = TerminalVersionSerializer
        return serializer_class

    def get_queryset(self):
        model = self.get_model_class()
        return model.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 402, 'msg': err.args[0]})
        return Response({'success': 1})
