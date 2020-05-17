# encoding: UTF-8
# 基于conda env:test(opencv)

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


def process(url):
    try:
        response = requests.get(url, headers=headers, timeout=(3, 7))
        if not response.ok:
            return None, list()
        content = response.text.replace(" ", "")
        res_url = r"(rmtp://[^/'\"\?><]+)|(rstp://[^/'\"\?><]+)"
        urls = re.findall(res_url, content, re.I | re.S | re.M)
        return url, urls
    except Exception as e:
        pass
    return None, list()


formatStr = str(sys.argv[1]).split(',')
webpageUrl = sys.argv[2]
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
