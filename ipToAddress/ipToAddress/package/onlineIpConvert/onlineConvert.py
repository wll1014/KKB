"""
Created on Thu Mar 19 09:22:18 2020

@author: wulinli
"""
import requests
import json
import configparser
import os

from package.data import resultData
success = resultData.resultData().success
fail = resultData.resultData().fail

class onlineConvert():
    def __init__(self):
        self.baidu_url = "http://api.map.baidu.com/location/ip"
        self.gaode_url = "https://restapi.amap.com/v3/ip"
        self.tencent_url = "https://apis.map.qq.com/ws/location/v1/ip"
        self.iplocAli_url = "http://iploc.market.alicloudapi.com/v3/ip"
        self.saipAli_url = "http://saip.market.alicloudapi.com/ip"

        config = self.get_map_service()
        self.map_service = config["map_service"]

        self.map_key = config["map_key"]

        ###以下是地图服务器配置常量  需要与config.ini保持一致
        self.baidu_map_service = "baidu"
        self.gaode_map_service = "gaode"
        self.tencent_map_service = "tencent"
        self.saipAli_map_service = "saipAli"  # 精确搜索
        self.iplocAli_map_service = "iplocAli"  # 范围搜索
        ###一下是延迟时间
        self.timeout = 2 #单位秒





    def get_map_service(self):
        config = configparser.ConfigParser()
        config_path = os.path.split(os.path.realpath(__file__))[0].split("package")[0]+"/config/config.ini"
        config.read(config_path,encoding='utf-8')

        sections = config.sections()  # 得到所有sections--目前只有一个section，为config
        options = config.options("map_config")  # 获取config区域的所有配置项key
        items = config.items('map_config')  # 获取config区域的所有的items key value

        map_service = config.get('map_config', 'map_service')
        map_key = config.get('map_config', 'map_key')
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
        try:
            res = requests.get(url, parms, timeout=self.timeout)
            result = json.loads(res.text)
            if(result["status"]==0):#百度地图0表示成功
                return success(res = {
                        "province":result["content"]["address_detail"]["province"],
                        "city":result["content"]["address_detail"]["city"],
                        "map_service":self.baidu_map_service
                    })
            else:
                return fail(res=res["status"],msg="错误码为"+res["status"])

        except Exception:
            return fail(msg="please check your net work")
            
    def iplocAli_ip_convert(self, ip):
        url = self.iplocAli_url
        parms = {
            "ip": ip,
        }
        headers = {'Authorization': 'APPCODE '+self.map_key}
        try:
            res = requests.get(url, parms, headers=headers,timeout=self.timeout)
            result = json.loads(res.text)

            if (result["status"] == "1"):#阿里地图"1"表示成功
                return success(res = {
                        "province": result["province"],
                        "city": result["city"],
                        "map_service":self.iplocAli_map_service
                    })
            else:
                return fail(msg="failed")
        except Exception:
            return fail(msg="please check your net work")


    def saipAli_ip_convert(self, ip):
        url = self.saipAli_url
        parms = {
            "ip": ip,
        }
        headers = {'Authorization': 'APPCODE '+self.map_key}

        try:
            res = requests.get(url, parms, headers=headers, timeout=self.timeout)
            result = json.loads(res.text)
            if (result["showapi_res_code"] == 0):#阿里地图"0"表示成功
                return success(res = {
                        "province": result["showapi_res_body"]["region"],
                        "city": result["showapi_res_body"]["city"],
                        "lnt": result["showapi_res_body"]["lnt"],
                        "lat": result["showapi_res_body"]["lat"],
                        "map_service":self.saipAli_map_service
                    })

            else:
                return fail(msg="failed")

        except Exception:
            return fail(msg="please check your net work")

    def gaode_ip_convert(self, ip):
        url = self.gaode_url
        parms = {
            "key": self.map_key,
            "ip": ip,
            "sig": "",
            "output": "json",
        }
        try:
            res = requests.get(url, parms,timeout=self.timeout)
            result = json.loads(res.text)

            if (result["status"] == "1"):#高德地图"1"表示成功
                return success(res={
                        "province": result["province"],
                        "city": result["city"],
                        "map_service":self.gaode_map_service
                    })
            else:
                return fail(msg=res["info"])

        except Exception:
            return fail(msg="please check your net work")

    def tencent_ip_convert(self,ip):
        url = self.tencent_url
        parms = {
            "key": self.map_key,
            "ip": ip,
            "output": "json",
            "callback": None,#回调函数 非必须项
        }
        try:
            res = requests.get(url, parms, timeout=self.timeout)
            result = json.loads(res.text)
            if (result["status"] == 0):  # 腾讯地图0表示成功
                return success(res={
                        "province": result["result"]["ad_info"]["province"],
                        "city": result["result"]["ad_info"]["city"],
                        "map_service":self.tencent_map_service
                    })
            else:
                return fail(msg=res["message"])
        except Exception:
            return fail(msg="please check your net work")

    def online_ip_covert_by_config(self,ip):
        switcher = {
            self.baidu_map_service: self.baidu_ip_convert(ip),
            self.gaode_map_service: self.gaode_ip_convert(ip),
            self.tencent_map_service: self.tencent_ip_convert(ip),
            self.saipAli_map_service:self.saipAli_ip_convert(ip),
            self.iplocAli_map_service:self.iplocAli_ip_convert(ip)
        }
        return switcher.get(self.map_service, False)

