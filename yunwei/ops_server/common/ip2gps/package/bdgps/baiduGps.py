#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 16:32:39 2020

@author: wulinli
"""
#import sys
import os
import json
import ipdb
import pandas as pd
import geoip2.database

#sys.path.append("..")
from common.ip2gps.package.conver import conver



class baiduGps():
    def __init__(self ,ip_address):
        self.ip_address = ip_address
        self.geo_city_mmdb = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeoLite2-City.mmdb')
        self.ipipfree_ipdb = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ipipfree.ipdb')
        self.ip_to_addr_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ipToAddress.json')


    def getCityNameByIp(self, ip_address):
        db = ipdb.City("./package/bdgps/ipipfree.ipdb")
        region_name = db.find_info(ip_address, "CN").region_name
        city_name = db.find_info(ip_address, "CN").city_name
        return {
            "region_name": region_name,
            "city_name": city_name
        }

    def ip2gps_from_geo_city_mmdb(self,ip_address):
        '''
        使用geo_city_mmdb将ip转换为gps
        :return:
        '''
        reader = geoip2.database.Reader(self.geo_city_mmdb)
        response = reader.city(ip_address)
        reader.close()
        if response.location.latitude:
            bd = conver.gcj02tobd09(response.location.longitude, response.location.latitude);
            return {
                "lat": bd[1],
                "lng": bd[0]
            }
        return False

    def getBaiDuGpsByPosition(self, ip_address):  # 百度GPS
        position = self.getCityNameByIp(ip_address)
        region_name = position["region_name"]
        city_name = position["city_name"]
        return self.getBaiduGpsByProvinceAndCity(region_name, city_name)

    def getBaiduGpsByProvinceAndCity(self, region_name, city_name):
        with open(self.ip_to_addr_json, 'r', encoding='utf-8') as f:
            city_infos = json.load(f)
        for city_info in city_infos:
            if region_name in city_info.get('city', '') and city_name in city_info.get('city', ''):
                lat_lng = {
                    "province": region_name,
                    "city": city_name,
                    "lat": float(city_info.get('lat')),
                    "lng": float(city_info.get('lng'))
                }
                return lat_lng
        lat_lng = self.ip2gps_from_geo_city_mmdb(self.ip_address)
        if lat_lng:
            return {
                    "province":region_name,
                    "city":city_name,
                    "lat": lat_lng['lat'],
                    "lng": lat_lng['lng']
                }
        return False


