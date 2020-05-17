# encoding: UTF-8
# 基于conda env:py35(opencv)

# 寻找过滤有效的rtmp,or,rtsp直播地址
# python xx.py rtmp,rtsp https://www.optbbs.com/thread-3439203-1-1.html
# 步骤
# 1,下载页面：https://www.optbbs.com/thread-3439203-1-1.html（避免使用csdn等，需点击触发显示全部的网页）
# 2,正则匹配：rtmp://, rtsp://等地址
# 3,[rtmp;//xx.com,rtsp://yy.com]使用ping+cv2.read()验证有效性

import datetime
import re
import sys
from multiprocessing import cpu_count, Pool
import cv2
import requests

headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Sec-Fetch-Dest': 'empty',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://www.baidu.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,tr;q=0.6,fr;q=0.5,zh-TW;q=0.4',
    'Cookie': 'BIDUPSID=8C26E1690527F4CB4ED508565EBE810E; PSTM=1586487982; BAIDUID=8C26E1690527F4CBE9EBFA9A228B6F9B:FG=1; BD_HOME=1; H_PS_PSSID=30971_1422_21088_30839_31186_31217_30823_31163; BD_UPN=123353'
}


def process(url):
    try:
        response = requests.get(url, headers=headers, timeout=(3, 7))
        if not response.ok:
            return None, list()
        content = response.text.replace(" ", "")
        res_url = r"((rtmp://[^'\"\?><]+)|(rtsp://[^'\"\?><]+))"
        urls = re.findall(res_url, content, re.I | re.S | re.M)
        return [x[0] for x in urls]
    except Exception as e:
        pass
    return list()


formatStr = 'rtmp,rtsp'
webpageUrl = 'https://www.optbbs.com/thread-3439203-1-1.html'

# formatStr = str(sys.arhttps://www.optbbs.com/thread-3439203-1-1.htmlgv[1]).split(',')
# webpageUrl = sys.argv[2]
print('params:' + str(sys.argv[1:]))
waitUrls = process(webpageUrl)
validUrls = list()
for url in waitUrls:
    try:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        if frame:
            validUrls.append(url)
    except:
        pass
print('validUrls:%s' % str(validUrls))
