import requests
import json
import configparser
import os


###以下是地图服务器配置常量  需要与config.ini保持一致
baidu_map_service = "baidu"
gaode_map_service = "gaode"
tencent_map_service = "tencent"

class onlineConvert():
    def __init__(self):
        self.baidu_url = "http://api.map.baidu.com/location/ip"
        self.gaode_url = "https://restapi.amap.com/v3/ip"
        self.tencent_url = "https://apis.map.qq.com/ws/location/v1/ip"
        self.ali_url = "http://iploc.market.alicloudapi.com/v3/ip"
        config = self.get_map_service()
        self.map_service = config["map_service"]

        self.map_key = config["map_key"]




    def get_map_service(self):
        config = configparser.ConfigParser()
        config_path = os.path.split(os.path.realpath(__file__))[0].split("package")[0]+"/config/config.ini"
        config.read(config_path)

        sections = config.sections()  # 得到所有sections--目前只有一个section，为config
        options = config.options("config")  # 获取config区域的所有配置项key
        items = config.items('config')  # 获取config区域的所有的items key value

        map_service = config.get('config', 'map_service')
        map_key = config.get('config', 'map_key')
        return {
            "map_service": map_service,
            "map_key": map_key
        }

    def baidu_ip_convert(self,ip):
        url = self.baidu_url
        parms = {
            "ak": self.map_key,
            "ip": ip,
            "coor":"",
        }
        res = requests.get(url,parms)
        result = json.loads(res.text)
        if(result["status"]==0):#百度地图0表示成功
            return {
                "province":result["content"]["address_detail"]["province"],
                "city":result["content"]["address_detail"]["city"]
            }
        else:
            return False
            
    def ali_ip_convert(self, ip):
        url = self.ali_url
        parms = {
            "ip": ip
        }
        headers = {'Authorization': 'APPCODE '+self.map_key}
        res = requests.get(url, parms, headers=headers)
        result = json.loads(res.text)

        if (result["status"] == "1"):#高德地图"1"表示成功
            return {
                "province": result["province"],
                "city": result["city"]
            }
        else:
            return False

    def gaode_ip_convert(self, ip):
        url = self.gaode_url
        parms = {
            "key": self.map_key,
            "ip": ip,
            "sig": "",
            "output": "json",
        }
        res = requests.get(url, parms)
        result = json.loads(res.text)

        if (result["status"] == "1"):#高德地图"1"表示成功
            return {
                "province": result["province"],
                "city": result["city"]
            }
        else:
            return False

    def tencent_ip_convert(self,ip):
        url = self.tencent_url
        parms = {
            "key": self.map_key,
            "ip": ip,
            "output": "json",
            "callback": None,#回调函数 非必须项
        }
        res = requests.get(url, parms)
        result = json.loads(res.text)
        if (result["status"] == 0):  # 腾讯地图0表示成功
            return {
                "province": result["result"]["ad_info"]["province"],
                "city": result["result"]["ad_info"]["city"]
            }
        else:
            return False

    def online_ip_covert_by_config(self,ip):
        switcher = {
            baidu_map_service: self.baidu_ip_convert(ip),
            gaode_map_service: self.gaode_ip_convert(ip),
            tencent_map_service: self.tencent_ip_convert(ip),
            ali_map_service:self.ali_ip_convert(ip)
        }
        return switcher.get(self.map_service, False)

