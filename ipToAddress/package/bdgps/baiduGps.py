#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 16:32:39 2020

@author: wulinli
"""
#import sys
import ipdb
import pandas as pd
import geoip2.database

#sys.path.append("..")
from package.conver import conver


class baiduGps():
    def __init__(self ):
        pass


    def getCityNameByIp(self, ip_address):
        db = ipdb.City("./package/bdgps/ipipfree.ipdb")
        region_name = db.find_info(ip_address, "CN").region_name
        city_name = db.find_info(ip_address, "CN").city_name
        return {
            "region_name": region_name,
            "city_name": city_name
        }

    def ip2gps(self):
        reader = geoip2.database.Reader('./package/bdgps/GeoLite2-City.mmdb')
        response = reader.city(self.ip_address)
        reader.close()
        if response.location.latitude:
            bd = conver.gcj02tobd09(response.location.longitude, response.location.latitude);
            return {
                "lat": bd[1],
                "lng": bd[0]
            }
        return False;

    def getBaiDuGpsByPosition(self, ip_address):  # 百度GPS
        position = self.getCityNameByIp(ip_address)
        region_name = position["region_name"]
        city_name = position["city_name"]
        return self.getBaiduGpsByProvinceAndCity(region_name, city_name)

    def getBaiduGpsByProvinceAndCity(self, region_name, city_name):
        sFileName = "./package/bdgps/ipToAddress2 (1).csv"  # 城市csv文件地址
        data = pd.read_csv(sFileName)
        for index in range(len(data['city'])):
            if region_name in data['city'][index] and city_name in data['city'][index]:
                # print(data['city'][index])
                return {
                    "lat": data['lat'][index],
                    "lng": data['lng'][index]
                }
        lat = self.ip2gps();
        if lat:
            return lat
        return False


