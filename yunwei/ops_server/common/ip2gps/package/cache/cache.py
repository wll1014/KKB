#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 3 16:32:39 2020

@author: wulinli
"""
import pandas as pd
import os
import time

from common.ip2gps.package.data import resultData

success = resultData.resultData().success
fail = resultData.resultData().fail
ip1="153.34.133.233"
ip2="153.34.133.234"
ip3="153.34.133.236"
ip = ip3

class cache:
    def __init__(self,min_day=30):
        self.min_day = min_day
        self.csv_name = os.path.split(os.path.realpath(__file__))[0] + "/ip_cache.csv"

    def get_ip_in_cache(self, ip):
        df = pd.read_csv(self.csv_name)
        df_res = df[df.ip == ip]

        if df_res.shape[0]<=0:
            return fail(res={
                "index": df.shape[0],
                "ip":ip
            },msg="the ip is not in the cache")

        else:
            index = df_res.index[0]
            return success(res={
                "index":index,
                "ip":df_res.ip[index],
                "lng":df_res.lng[index],
                "lat":df_res.lat[index],
                "update_time":df_res.update_time[index]
            })


    def get_diff_time(self,cache_time):#单位天
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        diff = time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")) - time.mktime(
            time.strptime(cache_time, "%Y-%m-%d %H:%M:%S"))
        day = diff / 60 / 60 / 24
        return day


    def update_ip_item(self,result):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        df = pd.read_csv(self.csv_name)
        df.loc[result["index"], "update_time"] = current_time
        df.to_csv(self.csv_name)



    def add_ip_item(self,result):
        print(result)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        df = pd.read_csv(self.csv_name)
        print(df)
        print([result["ip"], result["lng"], result["lat"], current_time])
        print(result["index"])
        df.loc[result["index"]] = [result["ip"], result["lng"], result["lat"], current_time]
        df.to_csv(self.csv_name)

