#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 17:22:18 2020

@author: wulinli
"""
import random
from math import sin, cos, pow, sqrt, asin, pi


class generateRandomGpsByPosition():
    def __init__(self, gps, distance):
        self.gps = gps
        self.distance = distance

    def rad(self, d):  # 转化为弧度
        return d * pi / 180.0

    def findNeighPositoin(self):  # 返回一个范围内的四个点，最小纬度和经度，最大纬度和经度
        gps = self.gps
        distance = self.distance
        # distance 单位 千米
        r = 6378.137  # 地球半径千米
        (longitude, latitude) = gps  # 经度、纬度
        dlng = 2 * asin(sin(distance / (2 * r)) / cos(latitude * pi / 180))
        dlng = dlng * 180.0 / pi  # 角度转换为弧度
        dlat = distance / r
        dlat = dlat * 180.0 / pi
        minlat = latitude - dlat
        maxlat = latitude + dlat
        minlng = longitude - dlng
        maxlng = longitude + dlng
        return {
            "minlat": minlat,
            "maxlat": maxlat,
            "minlng": minlng,
            "maxlng": maxlng
        }

    def getDistance(self, gps1, gps2):  # 获取gps1和gps2之间的距离
        EARTH_RADIUS = 6378.137  # 单位千米
        (lng1, lat1) = gps1  # 经度纬度
        (lng2, lat2) = gps2
        radLat1 = self.rad(lat1)
        radLng1 = self.rad(lng1)
        radLat2 = self.rad(lat2)
        radLng2 = self.rad(lng2)
        a = radLat1 - radLat2
        b = radLng1 - radLng2
        result = 2 * asin(sqrt(pow(sin(a / 2), 2) + cos(radLat1) * cos(radLat2) * pow(sin(b / 2), 2))) * EARTH_RADIUS
        return result

    def getRandomPosition(self):
        while (True):
            neighPosition = self.findNeighPositoin()
            minlat = neighPosition["minlat"]
            maxlat = neighPosition["maxlat"]
            minlng = neighPosition["minlng"]
            maxlng = neighPosition["maxlng"]

            lat = random.uniform(minlat, maxlat)  # 纬度
            lng = random.uniform(minlng, maxlng)  # 经度

            gps1 = self.gps
            gps2 = (lng, lat)
            dis = self.getDistance(gps1, gps2)
            if dis < self.distance:
                return gps2


'''            
gps = (100,45)#经度 纬度
distance = 5

getRandomPositionCls = generateRandomGpsByPosition(gps,distance)
gps_result = getRandomPositionCls.getRandomPosition()
print(gps_result)
'''