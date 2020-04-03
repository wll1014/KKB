#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import ipaddress
import logging


from common.ip2gps.package.ipToAddress import ipToAddress
from common.ip2gps.package.cache import cache

logger = logging.getLogger('ops.' + __name__)


def ip2gps(ipv4_addr, radius_dis=5):
    '''
    ip转换百度gps
    :param ipv4_addr: ipv4地址
    :param radius_dis: 随机点取值范围，单位km
    :return: (经度,纬度) 元组，未获取的返回False
    '''
    try:
        ip = ipaddress.IPv4Address(ipv4_addr)
    except ipaddress.AddressValueError:
        logger.error('%s is not a ipv4 addr' % ipv4_addr)
        return False
    else:
        if ip.is_global:
            ip_address_cls = ipToAddress.ipToAddress(ipv4_addr, radius_dis)
            result = ip_address_cls.get_address()
            if result["success"]:
                res = result["res"]
                gps_result=(res["lng"],res["lat"])
                return gps_result
            else:
                return False
        else:
            # 私网地址，返回空字符串
            logger.debug('%s is not a global addr' % ipv4_addr)
            return False


print(ip2gps("153.34.133.236"))