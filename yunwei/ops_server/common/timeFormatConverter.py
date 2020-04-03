#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import datetime
from django.utils import timezone


def localstr2utctimestamp(s):
    """
    :param s: local str --> utc timestamp
    :return:
    """
    ts = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    ts = timezone.get_current_timezone().localize(ts)
    return int(ts.timestamp()*1000)


def utcstr2utctimestamp(s):
    """
    :param s: utc str --> utc timestamp
    :return:
    """
    ts = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    ts = ts.replace(tzinfo=datetime.timezone.utc)
    return int(ts.timestamp()*1000)


def unixtimestamp2str(i):
    """
    :param i: int
    :return:
    """
    return datetime.datetime.fromtimestamp(i/1000).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def utcstr2localstr(s):
    """
    :param s: utc str --> local str
    :return:
    """
    ts = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    ts = ts.replace(tzinfo=datetime.timezone.utc)
    ts = datetime.datetime.fromtimestamp(ts.timestamp(), tz=timezone.get_current_timezone())
    return ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
