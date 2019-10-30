import net_metro_data
import take_metro

#爬虫的是苏州的地铁（人在苏州，比较熟悉苏州的地铁）
#如果想要爬虫北京，将city传值为　/bj

city_url = "/suz"
city_name = "苏州市"


metro_data = net_metro_data.metro_data(city='/suz')

station_to_line, all_line_stations = metro_data.get_metro_data()
Graph = metro_data.create_metro_graph(all_line_stations)
location_station = metro_data.get_location_station(city_name, station_to_line, list(Graph.keys()))



takeMetro = take_metro.take_metro_cls(location_station)

path1 = takeMetro.take_metro_way(Graph,"木渎","北寺塔",takeMetro.take_strategy_by_station_num)

path2 = takeMetro.take_metro_way(Graph,"木渎","北寺塔",takeMetro.take_strategy_by_distance)


print(path1)
print(path2)