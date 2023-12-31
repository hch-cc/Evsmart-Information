# 获取https://evsmart.net/所有地区的站点信息的url
# encoding = utf-8
import re
import requests as rq
from bs4 import BeautifulSoup as bs

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.41"}


def join_href(head, tail):
    new_href = []
    for t in tail:
        new_href.append(head + t)
    return new_href


def get_area():  # 获得所有区域
    url = "https://evsmart.net"
    html = rq.get(url, headers=header)
    soup = bs(html.text, "html.parser")
    map_s = soup.find("div", class_="map")
    area = map_s.find_all("ul", class_="list-pref")

    j = 0
    area_href = []
    for i in area:
        j += 1
        hrefs = i.find_all("a")
        for href in hrefs:
            area_href.append(href["href"])

    area_href = join_href(url, area_href)
    return area_href


def get_city(url):  # 获得每个城市的链接
    html = rq.get(url, headers=header)
    soup = bs(html.text, "html.parser")
    city_list = soup.find("ul", class_="list-spot")
    city = city_list.find_all("a")
    city_href = []
    for i in city:
        temp = i["href"]
        if temp == "#":
            continue
        try:
            judge = i.find("span").text
            num = re.split("[()]", judge)[1]
        except:
            continue
        if int(num) <= 20:
            city_href.append(temp)
        elif int(num) <= 50:
            city_href.append(temp + "?p=1&l=50&o=1")
        else:
            city_href.append(temp + "?p=1&l=100&o=1")
    city_data = join_href("https://evsmart.net", city_href)
    return city_data


def get_station(url):  # 获得每个站点的名称
    html = rq.get(url, headers=header)
    soup = bs(html.text, "html.parser")
    art = soup.find_all("article", class_="spot-box")
    station_href = []
    for i in art:
        station_href.append(i.find("a")["href"])
    station_data = join_href("https://evsmart.net", station_href)
    station_data1 = list(set(station_data))  # 去除重复的链接
    print(len(station_data), len(station_data1))
    return station_data1


def save_data(file_name, data):
    with open(file_name, "a") as f:
        for each_data in data:
            f.write(each_data)
            f.write("\n")


area1 = get_area()
num_area = len(area1)
name = 1
error_name = []
for each_area in area1:
    city1 = get_city(each_area)
    station_urls = []
    print("当前爬取", each_area.split("/")[-2])
    try:
        for each_city in city1:
            station_urls = get_station(each_city) + station_urls
        file_name = "E:/url/" + str(name) + ".txt"  # 保存文件的位置
        save_data(file_name, station_urls)
        name += 1
    except:
        print("出现未知错误！")
        error_name.append(each_area.split("/")[-2])  # 记录错误的地方
        continue
print(error_name)
