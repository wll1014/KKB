#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import json
from rest_framework import serializers
from platreport.models import DailyReportModel


class DailyReportSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = DailyReportModel


class DailyReportListSerializers(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        exclude = ('id',)
        model = DailyReportModel

    report_data = serializers.SerializerMethodField()

    def get_report_data(self, obj):
        try:
            data = json.loads(obj.report_data)
        except:
            data = obj.report_data

        return data
