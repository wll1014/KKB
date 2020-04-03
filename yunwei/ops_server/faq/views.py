from django.shortcuts import render

# Create your views here.

import json
import logging
from django.db import transaction

from .models import FAQClassifications, FAQRecords
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator

logger = logging.getLogger('ops.' + __name__)


def json_response(state, **kwargs):
    """
    自定义返回json
    :param state: 操作状态 0：失败   1：成功
    :param kwargs: 自定义返回字段
    :return: 字典
    """
    if state == 0:
        kwargs.setdefault("success", 0)
        return kwargs
    else:
        kwargs.setdefault("success", 1)
        return kwargs


class FAQClassSerializers(serializers.ModelSerializer):
    """
    FAQ分类序列化
    """
    # 前端字段 classification 和后端字段 name 转换
    classification = serializers.CharField(source='name',
                                           validators=[UniqueValidator(queryset=FAQClassifications.objects.all(),
                                                                       message="分类已存在，请修改后重试！")])

    class Meta:
        model = FAQClassifications
        fields = ('id', 'classification')


class FAQRecordSerializers(serializers.ModelSerializer):
    """
    FAQ问答记录序列化, 接收前端数据序列化
    """
    class Meta:
        model = FAQRecords
        exclude = ()
        validators = [
            UniqueTogetherValidator(
                queryset=FAQRecords.objects.all(),
                message="问题已存在，请修改后重试！",
                fields=['classification', 'question']
            )
        ]


class FAQRecordSerializersB(serializers.ModelSerializer):
    """
    FAQ问答记录序列化, 返回前端数据时序列化
    """
    classification = serializers.CharField(source='classification.name')
    id = serializers.IntegerField(source='classification.id')

    class Meta:
        model = FAQRecords
        fields = ('record_id', 'classification', 'id', 'question', 'answer')
        # exclude = ('creat_time', 'creator')


class FAQRecordSerializersA(serializers.ModelSerializer):
    """
    FAQ问答记录序列化, 修改数据时序列化
    """
    class Meta:
        model = FAQRecords
        exclude = ('creat_time', 'creator')


class FAQRecordSerializersC(serializers.ModelSerializer):
    """
    FAQ问答记录序列化, 返回前端分类和问题时序列化
    """
    class Meta:
        model = FAQRecords
        fields = ('record_id', 'question')


class FAQClass(APIView):
    """
    处理 api/v1/ops/faq/classes/ 请求
    """

    def post(self, request, version):
        """
        处理POST请求，添加分类
        :param request:
        :param version: API版本号
        """

        front_data = FAQClassSerializers(data=request.data)
        if front_data.is_valid():  # 校验数据
            try:
                with transaction.atomic():
                    front_data.save()
            except Exception as err:
                logger.error(err)
                return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
            else:
                return JsonResponse(json_response(1))
        else:
            logger.error(front_data.errors)
            return JsonResponse(json_response(0, error_code=422,
                                              msg='/n'.join([key+value[0] for key,value in front_data.errors.items()])))

    def get(self, request, version):
        """
        处理GET请求, 返回全部分类信息
        :param version: API版本号
        :param request:
        """

        # 返回全部数据
        classes = FAQClassifications.objects.all()
        try:
            if classes:
                # 数据不为空正常返回数据
                classes_series = FAQClassSerializers(classes, many=True)
                return Response(data={'success': 1, 'data': classes_series.data})
            else:
                # 数据为空返回空列表
                return Response(data={'success': 1, 'data': []})
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))

    def delete(self, request, version):
        """
        处理DELETE请求，删除分类
        :param version: API版本号
        :param request:
        """

        # 获取待删除数据id的数组
        try:
            ids = json.loads(request.body.decode()).get('ids')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
        else:
            if not all([isinstance(x, int) for x in ids]):
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))

        # 执行删除
        try:
            with transaction.atomic():
                FAQClassifications.objects.filter(id__in=ids).delete()
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            return JsonResponse(json_response(1))


class FAQClassDetail(APIView):
    """
    处理 api/v1/ops/faq/classes/{id}/ 请求
    """

    def put(self, request, version, ids):
        """
        处理PUT请求，修改分类名
        :param request:
        :param version: API版本号
        :param ids: 待修改记录的id
        """

        try:
            item = FAQClassifications.objects.get(id=ids)
        except (FAQClassifications.DoesNotExist, FAQClassifications.MultipleObjectsReturned) as err:
            logger.error(err)
            return Response(data=json_response(0, error_code=424, msg='请求信息不存在'))
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            # 执行修改
            front_data = FAQClassSerializers(data=request.data, instance=item)
            if front_data.is_valid():  # 校验数据
                try:
                    with transaction.atomic():
                        front_data.save()
                except Exception as err:
                    logger.error(err)
                    JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
                else:
                    return JsonResponse(json_response(1))
            else:
                logger.error(front_data.errors)
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))


class FAQRecord(APIView):
    """
    处理 /api/v1/ops/faq/ 请求
    """

    def get(self, request, version):
        """
        处理GET请求， 返回所有分类及分类下所有问题
        :param version: API版本号
        :param request:
        """
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        class_id = params.get('id')
        question = params.get('question')

        if class_id is None:
            classes = FAQClassifications.objects.all()
        else:
            classes = FAQClassifications.objects.filter(id__exact=class_id)

        if classes:
            # 分类不为空
            data = []
            for cla in classes:
                item = {}
                item.setdefault("classification", cla.name)
                item.setdefault("id", cla.id)
                if question is not None:
                    questions = cla.classification.all().filter(question__icontains=question)
                else:
                    questions = cla.classification.all()
                if questions:
                    # 问题不为空
                    questions = FAQRecordSerializersC(questions, many=True)
                    item.setdefault("questions", questions.data)
                else:
                    # 问题为空
                    item.setdefault("questions", [])
                data.append(item)
        else:
            # 分类为空返回空列表
            return Response(data={'success': 1, 'data': []})
        return Response(data={'success': 1, 'data': data})

    def post(self, request, version):
        """
        处理POST请求，增加faq记录
        :param version: API版本号
        :param request:
        """

        # 从request.META中获取创建人
        try:
            creator = request.META.get('ssoAuth').get('account')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='授权信息错误'))

        data = request.data
        data['creator'] = creator
        front_data = FAQRecordSerializers(data=data)
        if front_data.is_valid():  # 校验数据
            try:
                with transaction.atomic():
                    front_data.save()
            except Exception as err:
                logger.error(err)
                return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
            else:
                return JsonResponse(json_response(1))
        else:
            logger.error(front_data.errors)
            return JsonResponse(json_response(0, error_code=422,
                                              msg='/n'.join([key+value[0] for key,value in front_data.errors.items()])))

    def delete(self, request, version):
        """
        处理DELETE请求, 删除faq记录
        :param version: API版本号
        :param request:
        """

        # 获取待删除数据id的数组
        try:
            ids = json.loads(request.body.decode()).get('ids')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
        else:
            if not all([isinstance(x, int) for x in ids]):
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))

        # 执行删除
        try:
            with transaction.atomic():
                FAQRecords.objects.filter(record_id__in=ids).delete()
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            return JsonResponse(json_response(1))


class FAQRecordDetail(APIView):
    """
    处理 api/v1/ops/faq/{id}/ 请求
    """

    def get(self, request, version, ids):
        """
        处理GET请求， 返回单条记录的全部信息
        :param request:
        :param version: API版本号
        :param ids: 待删除记录的ID
        """

        try:
            item = FAQRecords.objects.get(record_id=ids)
        except (FAQRecords.DoesNotExist, FAQRecords.MultipleObjectsReturned) as err:
            logger.error(err)
            return Response(data={'success': 1, 'data': []})
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            item_series = FAQRecordSerializersB(item, many=False)
            return Response(data={'success': 1, 'data': [item_series.data]})

    def put(self, request, version, ids):
        """
        处理PUT请求，修改单条faq记录
        :param request:
        :param version: API版本号
        :param ids: 待修改记录的ID
        """

        try:
            # 先查询得到要修改的记录
            item = FAQRecords.objects.get(record_id=ids)
        except (FAQRecords.DoesNotExist, FAQRecords.MultipleObjectsReturned) as err:
            logger.error(err)
            return Response(data=json_response(0, error_code=424, msg='请求信息不存在'))
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            # 修改记录
            if request.data.get('creator'):
                # 'creator'属性创建后禁止修改
                request.data.pop('creator')
            front_data = FAQRecordSerializersA(instance=item, data=request.data, partial=True)
            if front_data.is_valid():  # 校验数据
                try:
                    with transaction.atomic():
                        front_data.save()
                except Exception as err:
                    logger.error(err)
                    JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
                else:
                    return JsonResponse(json_response(1))
            else:
                logger.error(front_data.errors)
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
