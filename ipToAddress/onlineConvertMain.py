from package.onlineIpConvert import onlineConvert

ip_address = "153.34.133.233"#ip地址
radius_dis = 5 #随机点取值范围，单位km


###以下是在线获取坐标方式
### 获取省份和城市
online_convert_cls = onlineConvert.onlineConvert()
res = online_convert_cls.online_ip_covert_by_config(ip_address)


print("map_service is :",online_convert_cls.map_service)
print("the province and city are :",res)

'''
baiduGpsCls = baiduGps.baiduGps()

region_name = res["province"]#省份
city_name = res["city"]#城市
# region_name = gaode_res["province"]#省份
# city_name = gaode_res["city"]#城市
# region_name = tencent_res["province"]#省份
# city_name = tencent_res["city"]#城市

### 根据省份和城市获取百度坐标
gps = baiduGpsCls.getBaiduGpsByProvinceAndCity(region_name=region_name, city_name=city_name)


lng = gps['lng']#百度坐标经度
lat = gps['lat']#百度坐标纬度
#方法一获取坐标

longitude_, latitude_ = point.generate_random_gps(base_log=lng, base_lat=lat, radius=radius_dis)
print("方法1转换结果")
print(longitude_) # 经度
print(latitude_)  # 纬度

# 方法二获取坐标
getRandomPositionCls = pointG.generateRandomGpsByPosition((lng,lat),radius_dis)
gps_result = getRandomPositionCls.getRandomPosition()
print("方法2转化结果")
print(gps_result)
'''