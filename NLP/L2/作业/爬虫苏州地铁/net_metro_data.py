import requests
from bs4 import BeautifulSoup
from collections import defaultdict
headers = {
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
myKey =  'cf0e88145e81002303b8097b44e74d18'

class metro_data:
    def __init__(self,city):
        self.home_url = "https://dt.8684.cn"
        self.city = city    #"/suz"
        self.city_home_url = self.home_url + self.city

    def get_url(self):#返回每个地铁的路线名称和url
        city_home_html = requests.get(self.city_home_url,headers = headers)
        city_home_html.encoding = "utf-8"
        soup = BeautifulSoup(city_home_html.text,'html.parser')
        metros_li = soup.find("ul","ib-mn rl-mn ib-box").find_all("li")
        metro_line_hrefs = [(li.find("a","line-a").string,self.home_url+li.find("a","line-a")["href"]) for li in metros_li if not (li.find("font") and "未开通" in li.find("font").string)]
        return metro_line_hrefs

    def get_metro_data(self):#返回所有地铁站点对应的路线和地铁站点
        metro_line_hrefs = self.get_url()
        all_line_stations = []
        station_to_line = defaultdict()
        for metro_line in metro_line_hrefs:
            line_name = metro_line[0]
            line_url = metro_line[1]

            line_html = requests.get(line_url, headers=headers)
            line_html.encoding = "utf-8"
            soup_line = BeautifulSoup(line_html.text, 'html.parser')
            line_station_a_tags = soup_line.find("div", "routeMap").find_all("a", "cl-station")
            line_stations = [line_station_a.string for line_station_a in line_station_a_tags]
            for station in line_stations:
                station_to_line[station] = line_name
            all_line_stations.append(line_stations)
        return station_to_line,all_line_stations

    myKey = 'cf0e88145e81002303b8097b44e74d18'  # 高德地图api申请的key

    def create_metro_graph(self,all_line_stations):#构建地铁线路图
        # station_to_line, all_line_stations = self.get_metro_data()
        Graph = defaultdict(list)
        for line in all_line_stations:
            for i in range(len(line)):
                station = line[i]
                next_station = line[i + 1] if i + 1 < len(line) else ""
                pre_station = line[i - 1] if i > 0 else ""
                if pre_station and not pre_station in Graph[station]:
                    Graph[station].append(pre_station)
                if next_station and not next_station in Graph[station]:
                    Graph[station].append(next_station)
        return Graph

    def geocode(self,address):#获取某个位置的经纬度
        parameters = {'address': address, 'key': myKey}
        base = 'http://restapi.amap.com/v3/geocode/geo'
        response = requests.get(base, parameters)
        answer = response.json()
        result = answer['geocodes'][0]['location'].split(",")
        return (float(result[0]), float(result[1]))

    def get_location_station(self,city_name,station_to_line,stations):
        location_station = defaultdict(tuple)
        for station in stations:
            location_station[station] = self.geocode(city_name+ station_to_line[station] + station + "地铁站")
        return location_station