from package.onlineIpConvert import onlineConvert

ip_address = "153.34.133.233"#ip地址

radius_dis = 5 #随机点取值范围，单位km

from package.ipToAddress import ipToAddress

ip_address_cls = ipToAddress.ipToAddress(ip_address,radius_dis)
result = ip_address_cls.get_address_by_way()
print(result)