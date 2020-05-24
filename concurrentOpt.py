# encoding: UTF-8
# 环境:py35(gevent)
# 测试不同并发下载算法的效率

import datetime
import re
import sys
from multiprocessing import cpu_count, Pool, Queue

import gevent
import requests
import pandas as pd

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

rootUrl = 'https://hexo.yuanjh.cn'
suffix = '/links'
maxCount = 5


def process(url):
    try:
        response = requests.get(url, headers=headers, timeout=(3, 7))
        if not response.ok:
            return url, list()
        content = response.text.replace(" ", "")
        res_url = r"href=[\"\'](https?://[^/'\"\?><]+)"
        urls = re.findall(res_url, content, re.I | re.S | re.M)
        return url, urls
    except Exception as e:
        pass
    return url, list()


def down(method='map'):
    waitQueue = Queue()
    waitQueue.put(rootUrl + suffix)
    waitQueueSet = set(rootUrl + suffix)
    successSet = set()
    faultSet = set()

    results_tmp = list()
    results = list()
    firstPageSet = set()
    while len(successSet) < maxCount and waitQueue.qsize():
        if method == 'map':
            pool = Pool(processes=max(1, cpu_count() - 1))
            results = pool.map(process, [waitQueue.get() for x in range(min(cpu_count() - 1, waitQueue.qsize()))])
        elif method == 'apply_async':
            pool = Pool(processes=max(1, cpu_count() - 1))
            results_tmp = [pool.apply_async(process, (waitQueue.get(),)) for _ in
                           range(min(cpu_count() - 1, waitQueue.qsize()))]
            pool.close()
            pool.join()
            results = [x.get() for x in results_tmp]
        # elif method == 'gevent':
        #     results_tmp = [gevent.spawn(process, waitQueue.get()) for _ in
        #                    range(min(cpu_count() - 1, waitQueue.qsize()))]
        #     gevent.joinall(results_tmp)
        #     results = [x.get() for x in results_tmp]
        # 只处理此域名下url
        successSet = successSet.union(rootUrl for rootUrl, urls in results if len(urls) > 0)
        faultSet = faultSet.union(rootUrl for rootUrl, urls in results if len(urls) == 0)
        addWaitQueueSet = set([url + suffix for rootUrl, urls in results for url in urls])
        [waitQueue.put(url) for url in (addWaitQueueSet - waitQueueSet)]
        waitQueueSet = waitQueueSet.union(addWaitQueueSet)
        print('waitSet len:%s successSet:%s faultSet:%s' % (waitQueue.qsize(), len(successSet), len(faultSet)))
#
#
# def down_callback():
#     # 满足这个pattern的认为是本站文章
#     waitQueue = Queue()
#     waitQueue.put(rootUrl + suffix)
#     waitQueueSet = set(rootUrl + suffix)
#     successSet = set()
#     faultSet = set()
#
#     results_tmp = list()
#     results = list()
#     firstPageSet = set()
#
#     def handle_data(result):
#         nonlocal waitQueueSet
#         url, urls = result
#         if len(urls) > 0:
#             successSet.add(url)
#         else:
#             faultSet.add(url)
#
#         addWaitQueueSet = set([url + suffix for url in urls])
#         [waitQueue.put(url) for url in (addWaitQueueSet - waitQueueSet)]
#         waitQueueSet = waitQueueSet.union(addWaitQueueSet)
#
#     while len(successSet) < maxCount and waitQueue.qsize():
#         # 挪外面最好，但未有合适处理方案（close无法open）
#         pool = Pool(processes=max(1, cpu_count() - 1))
#         results_tmp = [pool.apply_async(process, (waitQueue.get(),), callback=handle_data) for _ in
#                        range(min(cpu_count() - 1, waitQueue.qsize()))]
#         pool.close()
#         pool.join()
#         print('waitSet len:%s successSet:%s faultSet:%s' % (waitQueue.qsize(), len(successSet), len(faultSet)))


time_map = dict()
for _ in range(3):
    t1 = datetime.datetime.now()
    down(method='map')
    t2 = datetime.datetime.now()
    down(method='apply_async')
    t3 = datetime.datetime.now()
    # down(method='gevent')
    # t4 = datetime.datetime.now()
    # down_callback()
    # t5 = datetime.datetime.now()

    time_map['map'] = time_map.get('map', list()) + [(t2 - t1).total_seconds()]
    time_map['apply_async'] = time_map.get('apply_async', list()) + [(t3 - t2).total_seconds()]
    # time_map['gevent'] = time_map.get('gevent', list()) + [(t4 - t3).total_seconds()]
    # time_map['down_callback'] = time_map.get('down_callback', list()) + [(t5 - t4).total_seconds()]

time_series = pd.Series(time_map)
time_series.plot()
