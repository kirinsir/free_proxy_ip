import datetime
import time

import requests
import json
import re
from lxml import etree
from queue import Queue
import threading
import pymysql
con=pymysql.connect(host='localhost',port=3306,db='ip',password='123456',user='root')
cur=con.cursor()
headers = {
    'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    ' (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}
strat=time.time()
q=Queue()

w=open('ok.txt', 'a+', encoding='utf-8')
# 校验ip是否可用存入数据库
def get_good_ip():
    global cur
    global w
    while True:
        if q.qsize() == 0:
            break
        ip_port = q.get()
        proxies = {
            'http': f'http://{ip_port}',
            'https': f'http://{ip_port}'
        }
        try:
            res = requests.get("https://666cc.cn", timeout=5, proxies=proxies)
            if res.status_code == 200:
                # 可用代理ip 执行储存逻辑
                cur.execute(f'''insert into iptab values(null,'{ip_port}')''')
                w.writelines(ip_port+'\n')
                print('可用', ip_port)
        except Exception as e:
            print('错误或超时=> ', ip_port, e)


# ip切割判断 符合返回ip和端口，不符合返回None
def replace_n(ass):
    if len(ass) > 8:
        p = ass.replace('\r', '')
        return p


# 获取http
def get_proxy_list_http():
    url="https://www.proxy-list.download/api/v1/get?type=http"
    a=requests.get(url=url,headers=headers)
    s=a.text.split("\n")
    proxy_list_ip_port=list(map(replace_n,s))
    return proxy_list_ip_port


# 获取https
def get_proxy_list_https():
    url="https://www.proxy-list.download/api/v1/get?type=https"
    a=requests.get(url=url,headers=headers)
    s=a.text.split("\n")
    proxy_list_ip_port=list(map(replace_n,s))
    return proxy_list_ip_port


def get_proxy_ip():

    gp=get_proxy_list_http()
    gps=get_proxy_list_https()
    ad=gp+gps
    for x in ad:
        if x is not None:
            q.put(x)

#


def threading_run(num=50):
    for x in range(num):
        t=threading.Thread(target=get_good_ip,)
        t.start()
    t.join()


# https://api.superfastip.com/ip/freeip?page=1
def get_sup_ip():
    a=requests.get(url='https://api.superfastip.com/ip/freeip?page=1',headers=headers,verify=False)

    if a.status_code==200:
        js = json.loads(a.text)
        for x in js['freeips']:
            q.put(x['ip']+":"+x['port'])
    time.sleep(2)
    a = requests.get(url='https://api.superfastip.com/ip/freeip?page=2', headers=headers,verify=False)

    if a.status_code == 200:
        js = json.loads(a.text)
        for x in js['freeips']:
            q.put(x['ip'] + ":" + x['port'])

# https://checkerproxy.net/archive/2021-04-16
def get_checkerproxy_ip():
    dat=datetime.datetime.now().strftime("%Y-%m-%d")
    url=f'https://checkerproxy.net/api/archive/{dat}'
    print(url)
    a=requests.get(url=url,headers=headers)
    if a.status_code==200:
        js=json.loads(a.text)
        for x in js:
            q.put(x['addr'])

# get_checkerproxy_ip()
def get_jiangxianli_ip():
    for x in range(1, 15):
        url = f'https://ip.jiangxianli.com/api/proxy_ips?page={x}'
        st = json.loads(requests.get(url=url, headers=headers).text)
        print('抓取第 ', x, ' 页')
        for ip_port in st['data']['data']:
            q.put(ip_port['ip'] + ":" + ip_port['port'])
        time.sleep(1)


def threading_runAll():
    t=threading.Thread(target=get_jiangxianli_ip,)
    t1=threading.Thread(target=get_checkerproxy_ip,)
    t2=threading.Thread(target=get_sup_ip,)
    t3=threading.Thread(target=get_proxy_ip,)
    lis=[t,t1,t2,t3]
    for x in lis:
        x.start()
    for x in lis:
        x.join()


if __name__ == '__main__':
    threading_runAll()
    time.sleep(5)
    threading_run()
    # while True:
    #     if q.qsize()==0:
    #         try:
    #             con.commit()
    #             break
    #         except Exception as e:
    #             print('错误',e)
    print('结束了')
    con.commit()
    print(time.time()-strat)

# ip去除\r特殊符号 用map省内存



