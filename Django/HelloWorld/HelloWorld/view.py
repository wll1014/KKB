# # 未配置模板
# from django.http import  request
from django.http import HttpResponse,JsonResponse
# def hello(request):
#     return HttpResponse("hello world")
# 配置模板
from django.shortcuts import render
def hello(request):
    context={
        "hello":"hello world!"
    }
    return render(request,"hello.html",context)
# class xx_Serializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = xx_model
#         fields = ('id', 'username', 'email', 'is_staff')
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = xx_model.objects.all()
#     serializer_class = xx_Serializer
#
#     def list(self, request, *args, **kwargs):
#         return Response({"data":'balalalal'})

from rest_framework import status
from TestModel import models
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

class LoginModelSerializer(serializers.BaseSerializer):
    def __init__(self,data):
        self.data=data

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Test  # 设置关联模型     model就是关联模型
        fields = '__all__'  # fields设置字段   __all__表示所有字段


import json
class Login(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # data = LoginModelSerializer({'username':'wulinli'}).data
            # print(data)
            # ser = serializers.BaseSerializer(request=request,data="wulinli")
            # print(ser.data)
            # print(models.Test.objects.get(id=2))
            # a = TestSerializer(models.Test.objects.get(id=2),many=True)
            #
            # print(a.data)
            # return Response(a.data)
            # return HttpResponse("ser.data")
            # return HttpResponse(json.dumps({
            #     "username":"wulinli"
            # }))
            return JsonResponse({
                "username":"wulinli"
            })
        except Exception as e:

            return Response({})