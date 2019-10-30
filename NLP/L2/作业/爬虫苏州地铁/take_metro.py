import math
import networkx as nx


import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False



class take_metro_cls:
    def __init__(self,location_station):
        self.location_station = location_station



#begin:绘制地图
# station_graph = nx.Graph(Graph)
# plt.figure(figsize=(30,20),dpi=80) # figsize设置图片大小，dpi设置清晰度
# nx.draw(station_graph,location_station,with_labels = True,node_size =20)
#
# location_station_graph = nx.Graph()
# location_station_graph.add_nodes_from(list(location_station.keys()))
# plt.figure(figsize=(30,20),dpi=80)
# nx.draw(location_station_graph,location_station,with_labels = True,node_size =30)
#end:绘制地图

#begin:定义通过经纬度获取位置之间的距离
    def geo_distance(self, origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d



    # 广度优先搜索算法
    def take_metro_way(self,metro_graph,start,target,take_strategy):
        if not start in metro_graph.keys() or not target in metro_graph.keys():
            print("<",start,">或者<",target,">不是地铁站点，请输入正确的站点")
            return []
        pathes = [[start]]
        while(pathes):
            path = pathes.pop(0)
            frontier = path[-1]
            candidate = metro_graph[frontier]
            for item in candidate:
                if item in path:continue
                new_path = path+[item]
                pathes.append(new_path)
            pathes = take_strategy(pathes)
            if pathes[0][-1]==target:
                return pathes[0]





    def take_strategy_by_station_num(self,pathes):#定义搜索策略-----根据站点数目排序
        return sorted(pathes,key=self.get_station_num_of_path)

    def get_station_num_of_path(self,path):
        return len(path)



    def get_station_distance(self,station1,station2):#定义搜索策略-----根据站点距离排序
        return self.geo_distance(self.location_station[station1],self.location_station[station2])

    def take_strategy_by_distance(self,pathes):
        return sorted(pathes,key=self.get_distance_of_path)

    def get_distance_of_path(self,path):
        distance = 0
        for i,_ in enumerate(path[:-1]):
            distance += self.get_station_distance(path[i],path[i+1])
        return distance




