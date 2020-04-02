"""
Created on Thu Mar 19 09:22:18 2020

@author: wulinli
"""

import configparser
import os
import IPy
from package.randompoint import  pointG;
from package.bdgps import baiduGps
from package.onlineIpConvert import onlineConvert
from package.conver import conver

###resultData用于处理数据
from package.data import resultData
success = resultData.resultData().success
fail = resultData.resultData().fail

class ipToAddress():
    def __init__(self,ip,radius_dis):
        self.ip = ip
        self.radius_dis = radius_dis

    def get_way_of_convert(self):
        config = configparser.ConfigParser()
        config_path = os.path.split(os.path.realpath(__file__))[0].split("package")[0] + "/config/config.ini"
        config.read(config_path, encoding='utf-8')

        sections = config.sections()  # 得到所有sections--目前只有一个section，为config
        options = config.options("config")  # 获取config区域的所有配置项key
        items = config.items('config')  # 获取config区域的所有的items key value

        convert_way = config.get('config', 'convert_way')
        return {
            "convert_way": convert_way,
        }
    
    def online_convert(self):
        baidu_gps_cls = baiduGps.baiduGps()
        online_convert_cls = onlineConvert.onlineConvert()
        result = online_convert_cls.online_ip_covert_by_config(self.ip)
        if result["success"] == True:
            res = result["res"]
            if res["map_service"] == online_convert_cls.saipAli_map_service:
                lng = float(res['lnt'])  # 高德坐标经度
                lat = float(res['lat'])  # 高德坐标纬度
                po = conver.gcj02tobd09(lng, lat)  # 高德坐标转百度坐标转
                return  success(res={
                        "province": res["province"],
                        "city": res["city"],
                        "lng": po[0],
                        "lat": po[1]
                    })
            else:
                region_name = res["province"]  # 省份
                city_name = res["city"]  # 城市
                gps = baidu_gps_cls.getBaiduGpsByProvinceAndCity(region_name=region_name, city_name=city_name)
                lng = gps['lng']  # 百度坐标经度
                lat = gps['lat']  # 百度坐标纬度
                get_random_position_cls = pointG.generateRandomGpsByPosition((lng, lat), self.radius_dis)
                gps_result = get_random_position_cls.getRandomPosition()
                return success(res={
                        "province": res["province"],
                        "city": res["city"],
                        "lng": gps_result[0],
                        "lat": gps_result[1]
                    })
        else:
            return fail(msg=result["msg"])

    def local_convert(self):
        baidu_gps_cls = baiduGps.baiduGps()
        gps = baidu_gps_cls.getBaiDuGpsByPosition(self.ip)
        lng = gps['lng']  # 百度坐标经度
        lat = gps['lat']  # 百度坐标纬度
        get_random_position_cls = pointG.generateRandomGpsByPosition((lng, lat), self.radius_dis)
        gps_result = get_random_position_cls.getRandomPosition()
        if gps_result==False:
            return fail(msg="through the local way, we do not find the location by ip")
        else:
            return success(res={
                    "province": gps["province"],
                    "city": gps["city"],
                    "lng": gps_result[0],
                    "lat": gps_result[1]
                })
    def before_convert(self):
        try:
            ip_type = IPy.IP(self.ip).iptype()
            if ip_type == "PRIVATE":
                return fail(msg="your ip address is private ip")
            else:
                return success()
        except Exception:
            return fail(msg="your ip address is illegal")


    def get_address_by_way(self):
        convert_way = self.get_way_of_convert()["convert_way"]
        check_result = self.before_convert()#检测ip是否为合法或者是私有ip
        if not check_result["success"]:
            return check_result

        if convert_way=="online" :
            result = self.online_convert()
            if result["success"]==True:
                return result
            else:
                return self.local_convert()
        else:
            if convert_way=="local":
                return self.local_convert()
