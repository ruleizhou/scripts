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
import matplotlib.pyplot as plt

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
urls = ['http://www.zentao.net/links', 'http://www.mopaas.com/links', 'https://www.moeq.com.cn/links',
        'https://www.jsdelivr.com/links', 'http://huanghc.cn/links', 'http://www.mikecrm.com/links',
        'https://raycoder.me/links', 'http://unlcedemon.online/links', 'https://956898603.qzone.qq.com/links',
        'https://riohsc.github.io/links', 'https://www.d4j.cn/links', 'https://hexo.yuanjh.cn/links',
        'http://status.dreamwings.cn/links', 'https://9527dhx.top/links', 'https://leafjame.github.io/links',
        'https://music.163.com/links', 'https://www.fezhu.top/links', 'https://zkpeace.com/links',
        'https://www.asplun.cn/links', 'https://www.liaofuzhan.com/links', 'https://www.gugugu.dev/links',
        'https://mmyyll.ml/links', 'https://www.yunyoujun.cn/links', 'https://wnjxyk.tech/links',
        'https://wblog.tech/links', 'https://www.myblog.city/links', 'https://iwalyou.com/links',
        'http://github.com/links', 'http://yufanboke.top/links', 'http://www.tuicool.com/links',
        'http://43.248.127.15/links', 'https://code004.ml/links', 'https://xiangjunhong.com/links',
        'https://www.hojun.cn/links', 'https://afdian.net/links', 'https://blog.mayuko.cn/links',
        ]

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


def down_map():
    waitQueue = Queue()
    [waitQueue.put(url + suffix) for url in urls]
    while waitQueue.qsize():
        pool = Pool(processes=max(1, cpu_count() - 1))
        results = pool.map(process, [waitQueue.get() for x in range(min(cpu_count() - 1, waitQueue.qsize()))])


def down_apply_async():
    waitQueue = Queue()
    [waitQueue.put(url + suffix) for url in urls]
    while waitQueue.qsize():
        pool = Pool(processes=max(1, cpu_count() - 1))
        results_tmp = [pool.apply_async(process, (waitQueue.get(),)) for _ in
                       range(min(cpu_count() - 1, waitQueue.qsize()))]
        pool.close()
        pool.join()
        results = [x.get() for x in results_tmp]


def down_gevent():
    waitQueue = Queue()
    [waitQueue.put(url + suffix) for url in urls]
    while waitQueue.qsize():
        results_tmp = [gevent.spawn(process, waitQueue.get()) for _ in
                       range(min(cpu_count() - 1, waitQueue.qsize()))]
        gevent.joinall(results_tmp)
        results = [x.get() for x in results_tmp]


time_map = dict()
for _ in range(4):
    t1 = datetime.datetime.now()
    down_map()
    print('down_map')
    t2 = datetime.datetime.now()
    down_apply_async()
    print('down_apply_async')
    t3 = datetime.datetime.now()
    down_gevent()
    print('down_gevent')
    t4 = datetime.datetime.now()

    time_map['map'] = time_map.get('map', list()) + [(t2 - t1).total_seconds()]
    time_map['apply_async'] = time_map.get('apply_async', list()) + [(t3 - t2).total_seconds()]
    time_map['gevent'] = time_map.get('gevent', list()) + [(t4 - t3).total_seconds()]

time_df = pd.DataFrame(time_map)
time_df.plot()
plt.show()
