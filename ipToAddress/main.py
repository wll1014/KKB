#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from package.randompoint import point,pointG;
from package.randompoint import point, pointG;
from package.bdgps import baiduGps
from package.onlineIpConvert import onlineConvert


ip_address = "112.22.2.62"#ip地址
radius_dis = 5 #随机点取值范围，单位km
baiduGpsCls = baiduGps.baiduGps()
gps = baiduGpsCls.getBaiDuGpsByPosition(ip_address)

lng = gps['lng']#百度坐标经度
lat = gps['lat']#百度坐标纬度


print("lng:",lng)
print("lat:",lat)


#转换坐标（若坐标为gps需要转换成百度坐标）
#po=conver.gcj02tobd09(120.5954,31.3041)
#po=conver.gcj02tobd09(lng,lat)#gps转百度坐标转
#print(po)


#方法一：坐标位置获取随机点
#longitude_, latitude_ = point.generate_random_gps(base_log=120.7, base_lat=30, radius=10)
longitude_, latitude_ = point.generate_random_gps(base_log=lng, base_lat=lat, radius=radius_dis)
print(longitude_) # 经度
print(latitude_)  # 纬度




#方法二：坐标位置获取随机点
#gps = (100,45)#经度 纬度
getRandomPositionCls = pointG.generateRandomGpsByPosition((lng,lat),radius_dis)
gps_result = getRandomPositionCls.getRandomPosition()
print(gps_result)








