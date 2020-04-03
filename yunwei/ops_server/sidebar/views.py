from django.shortcuts import render

# Create your views here.
import logging
import json
import os
import sys
import subprocess
from rest_framework.views import APIView
from rest_framework.response import Response
from common import my_elastic, global_func
from sidebar.models import *
from ops.settings import BASE_DIR

logger = logging.getLogger('ops.' + __name__)


class Sidebar(APIView):
    # 获取工具栏
    def get(self, request, *args, **kwargs):
        try:
            # manage_path = os.path.join(BASE_DIR,'manage.py')
            # dumpdata_path = os.path.join(BASE_DIR,'sidebar','sidebar.json')
            # python3_path = sys.executable
            # sidebar = ModelSidebar.objects.all()
            # if not sidebar:
            #     # 不存在则加载导出的json
            #     if os.path.exists(manage_path) and os.path.exists(dumpdata_path) and os.path.exists(python3_path):
            #         subprocess.getstatusoutput('%s %s loaddata %s' % (python3_path, manage_path, dumpdata_path))
            #         logger.debug('%s %s loaddata %s' % (python3_path, manage_path, dumpdata_path))
            #         sidebar = ModelSidebar.objects.all()
            #     else:
            #         logger.error('please check %s/%s/%s is available!')

            sidebar = global_func.init_sidebar()

            data = []
            for sidebar_obj in sidebar:
                if not sidebar_obj.pid:
                    # 无父节点
                    data.append(
                        {
                            'title': sidebar_obj.title,
                            'url': sidebar_obj.url,
                            'icon': sidebar_obj.icon,
                        }
                    )
                else:
                    # 有父节点
                    for d in data:
                        # 找到父节点
                        if sidebar_obj.pid.title == d.get('title'):
                            if d.get('childnode'):
                                # 已经存在childnode
                                d.get('childnode').append(
                                    {
                                        'title': sidebar_obj.title,
                                        'url': sidebar_obj.url,
                                        'icon': sidebar_obj.icon,
                                    }
                                )
                            else:
                                # childnode不存在
                                d.update(
                                    {
                                        'childnode':[
                                            {
                                                'title': sidebar_obj.title,
                                                'url': sidebar_obj.url,
                                                'icon': sidebar_obj.icon,
                                            }
                                        ]
                                    }
                                )

            response = global_func.get_response(data=data)
            return Response(response)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0)
            return Response(response)