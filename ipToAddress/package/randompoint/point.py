# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import random
from math import  cos, sin, sqrt, pi


#  参数含义
# base_log：经度基准点，
# base_lat：维度基准点，
# radius：距离基准点的半径
EARTH_RADIUS = 6378.137;
def generate_random_gps(base_log=None, base_lat=None, radius=None):
    radius_in_degrees = radius / (EARTH_RADIUS*pi/180)
    u = float(random.uniform(0.0, 1.0))
    v = float(random.uniform(0.0, 1.0))
    w = radius_in_degrees * sqrt(u)
    t = 2 * pi * v
    x = w * cos(t)
    y = w * sin(t)
    longitude = y + base_log
    latitude = x + base_lat
    # 这里是想保留14位小数
    loga = '%.14f' % longitude
    lata = '%.14f' % latitude
    return loga, lata

'''
longitude_, latitude_ = generate_random_gps(base_log=120.7, base_lat=30, radius=10)


print(longitude_) # 经度
print(latitude_)  # 纬度
#计算两个坐标点之间得距离
def geodistance(lng1,lat1,lng2,lat2):
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]); # 经纬度转换成弧度
    dlon=lng2-lng1;
    dlat=lat2-lat1;
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2;
    distance=2*asin(sqrt(a))*EARTH_RADIUS*1000 # 地球平均半径，6371km
    distance=round(distance/1000,3);
    return distance
dist = geodistance(120.7,30,longitude_,latitude_)

print(dist) 
'''