#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from rest_framework import serializers
from ops_statistics.models import PositionModel

class PositionSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = PositionModel

