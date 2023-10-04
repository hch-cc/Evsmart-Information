# 获取日本https://evsmart.net/上的充电桩基本信息
# 多线程版本
# 写入多个信息，不带图片
# encoding = utf-8
import time
import requests as rq
from openpyxl import load_workbook
from bs4 import BeautifulSoup as bs
from threading import Thread, Lock
from queue import Queue


def get_info(url, order, header):  # 获取目标网页的信息
    try:
        html = rq.get(url, headers=header, timeout=10)
    except:
        return
    soup = bs(html.text, "html.parser")
    try:
        area = soup.find("ol", attrs={"typeof": "BreadcrumbList", "class": "breadcrumb"}).find_all("span", attrs={
            "property": "name"})
        area_1 = ""

        for i in area[1:]:
            area_1 += i.text + "/"
    except:
        return

    try:
        station_name = soup.find("h1", class_="page-title").text
    except:
        return
    try:
        interface = soup.find("ul", class_="charger").text.replace(" ", "").replace("\n", "")

    except:
        return
    try:
        dl = soup.find_all("dl", class_="spot-details-dl")
        address = dl[1].find("dd").text.replace(" ", "").replace("\n", "")
    except:
        address = "None"
    try:
        tel = soup.find("a", class_="tel").text
    except:
        tel = "None"
    return [order, area_1, station_name, interface, address, tel]  # 返回序列，区域，站点名称，接口类型，地址，电话


def get_p(url, ord_name, lock, header):  # 获取评论区的href元素的 链接
    try:
        html = rq.get(url, headers=header, timeout=10)
        soup = bs(html.text, "html.parser")
        p_href = soup.find_all("a", attrs={"rel": "lightbox"})
    except:
        return
    num = 1
    for i in p_href:
        try:
            p_url = "https:" + i["href"]
            lock.acquire()
            with open("E:/picture/test/{}.jpg".format(str(ord_name) + "-" + str(num)), "wb") as f:  # 打开文件
                img = rq.get(p_url, timeout=20)  # 获取图片
                f.write(img.content)  # 写入文件
                num += 1
            lock.release()
        except:
            continue
        if num > 5:  # 最多只要五张图片
            break


def read_url(path):
    with open(path, "r") as f:
        url = f.readlines()
    return url


def sava_data(data):  # 保存数据到excel中
    global wb_name
    wb1 = load_workbook(wb_name)  # 加载工作簿
    sheet1 = wb1["Sheet1"]  # 获取Sheet
    for each in data:
        sheet1.append(each)  # 用append方法写入数据
    wb1.save(wb_name)  # 保存excel
    wb1.close()  # 关闭excel


def myThread(q, q1, lock, header):
    while 1:
        if not q.empty():
            u = q.get()  # 从队列q中获得url
            order = q1.get()  # 从队列q1中获得序列
            info = get_info(u, order, header)
            if info is None:
                continue
            global data
            lock.acquire()  # 锁住
            data.append(info)
            lock.release()  # 释放
            # get_p(u + "comments", order, lock, header) # 这是获取图片的,需要照片的可以去掉注释，建议用多进程版本的
            print("第", order)

        else:
            break


# 全局常量
wb_name = "all_information.xlsx"  # 要写入excel路径的名称，这里是本工程文件下的文件
data = []  # 每个线程产生的数据写入这里
if __name__ == "__main__":
    start = time.time()
    print("---主进程开始---")
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.41"}

    with open("run_info.txt", "r") as f:  # run_info.txt 为记录运行信息，file_name ，为url文件名称，order为序列，第一次从都从0开始
        read_run_info = f.readlines()
    file_name = int(read_run_info[0].replace("\n", ""))
    order = int(read_run_info[1].replace("\n", ""))

    path = "E:/url/{}.txt".format(file_name + 1)  # 存放url的文件地址
    urls = read_url(path)  # 打开文件并读入数据
    url_len = len(urls)    # url的数量
    print(url_len)
    q = Queue(url_len)  # url队列
    q1 = Queue(url_len)  # 序列队列
    lock = Lock()  # 锁
    t_list = []  # 线程列表
    print("正在爬取{}.txt".format(file_name + 1))
    for each in urls:
        q.put(each.replace("\n", ""))  # url写入队列，replace("\n", "")去掉尾巴的回车符
    for i in range(order + 1, order + url_len + 1):
        q1.put(i)  # 对应的编号，不用编号的可以不管这个
    for i in range(20):  # 生成线程
        t = Thread(target=myThread, args=(q, q1, lock, header), name="子线程{}".format(i))
        t_list.append(t)
        t.start()  # start
        print("%s开始" % t.name)
    for i in t_list:  # 线程阻塞
        i.join()
        print("%s结束" % i.name)
    print("---主进程结束---")

    print("文件{}.txt爬取完成".format(file_name + 1))

    with open("run_info.txt", "w") as f:
        writer_run_info = f.writelines(str(file_name + 1) + "\n")
        writer_run_info = f.writelines(str(order + url_len))

    sava_data(data)  # 保存信息
    end = time.time()
    print("运行信息写入完毕")
    print("总共耗时：{}秒".format(end - start), len(data))
