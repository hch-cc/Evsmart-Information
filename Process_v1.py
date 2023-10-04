# 获取日本https://evsmart.net/上的充电桩基本信息
# 多进程版本
# 写入多个信息，带图片
# encoding = utf-8
import time
import requests as rq
from openpyxl import load_workbook
from bs4 import BeautifulSoup as bs
from multiprocessing import Process, Queue, Lock


def get_info(url, order, header):
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
    return [order, area_1, station_name, interface, address, tel]


def get_p(url, ord_name, lock, header):
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
            with open("E:/picture/test/{}.jpg".format(str(ord_name) + "-" + str(num)), "wb") as f:
                img = rq.get(p_url, timeout=20)
                f.write(img.content)
                num += 1
            lock.release()
        except:
            continue
        if num > 5:
            break


def read_url(path):
    with open(path, "r") as f:
        url = f.readlines()
    return url


def sava_data(data):
    global wb_name
    wb1 = load_workbook(wb_name)
    sheet1 = wb1["Sheet1"]
    sheet1.append(data)
    wb1.save(wb_name)
    wb1.close()


def mypro(q, q1, q2, lock, header):
    while 1:
        if not q.empty():
            u = q.get()
            order = q1.get()
            info = get_info(u, order, header)
            if info is None:
                continue
            q2.put(info)
            lock.acquire()
            sava_data(q2.get())
            lock.release()
            get_p(u + "comments", order, lock, header)  # 这是获取评论区图片
            print("第", order, u)

        else:
            break


# 全局常量
wb_name = "test.xlsx"  # 要写入excel路径的名称，这里是本工程文件下的文件

if __name__ == "__main__":
    start = time.time()
    print("---主进程开始---")
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.41"}

    path = "E:/url/{}.txt".format(2)  # 存放url的文件地址
    urls = read_url(path)  # 打开文件并读入数据
    url_len = len(urls)    # url的数量
    print(url_len)

    q = Queue(url_len)  # url队列
    q1 = Queue(url_len)  # 序列队列
    q2 = Queue()  # 将子进程的数据写入此队列
    lock = Lock()
    p_list = []
    for each in urls:
        q.put(each.replace("\n", ""))  # url写入队列，replace("\n", "")去掉尾巴的回车符
    for i in range(1, url_len + 1):
        q1.put(i)
    print("正在爬取{}.txt".format(2))
    for i in range(10):  # 进程数目
        p = Process(target=mypro, args=(q, q1, q2, lock, header), name="子进程{}".format(i))
        p_list.append(p)
        p.start()
        print("%s开始" % p.name)
    for i in p_list:
        i.join()
        print("%s结束" % i.name)
    print("---主进程结束---")

    print("文件{}.txt爬取完成".format(2))
    end = time.time()
    print("运行信息写入完毕")
    print("总共耗时：{}秒".format(end - start))
