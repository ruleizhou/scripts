# encoding: UTF-8
# 环境:py35(gevent)
# 测试不同并发下载算法的效率

import datetime
import re
import sys
from multiprocessing import cpu_count, Pool, Queue

import gevent
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

rootUrl = 'https://hexo.yuanjh.cn'
suffix = '/links'
maxCount = 50
import pandas as pd

# rootUrl = sys.argv[1]
# suffix = sys.argv[2]
# maxCount = int(sys.argv[3])
#
# print('params:' + str(sys.argv[1:]))


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


urls = ['http://www.1688.com/links', 'https://www.aye.ink/links', 'https://cherrycat.gitee.io/links',
        'https://mmyyll.ml/links', 'http://www.alibabagroup.com/links', 'https://www.jsdelivr.com/links',
        'https://iwalyou.com/links', 'http://www.oschina.net/links', 'https://www.etuan.com/links',
        'https://developer.aliyun.com/links', 'http://www.fezhu.top/links', 'https://yiki.tech/links',
        'https://saky.site/links', 'http://www.tuicool.com/links', 'https://maka.im/links',
        'https://www.cnblogs.com/links', 'http://www.alipay.com/links', 'http://help.baidu.com/links',
        'https://starrycat.me/links', 'https://status.qiniu.com/links', 'https://career.qiniu.com/links',
        'https://ctz45562.github.io/links', 'http://tieba.baidu.com/links', 'https://bestzuo.cn/links',
        'https://www.ktbear.top/links', 'https://www.legends-killer.cq.cn/links', 'http://qingting.baidu.com/links',
        'https://hfanss.com/links', 'https://huadonghu.com/links', 'https://leetcode-cn.com/links',
        'http://lovefc.cn/links', 'https://zfans.xyz/links', 'http://career.qiniu.com/links',
        'https://blog.badapple.pro/links', 'https://worktile.com/links', 'https://portal.qiniu.com/links',
        'https://market.aliyun.com/links', 'https://pbas.club/links', 'https://sg.alibabacloud.com/links',
        'https://us.alibabacloud.com/links', 'https://qoogle.top/links', 'https://perry96.com/links',
        'https://www.ilovea.asia/links', 'https://blog.qiniu.com/links', 'http://github.com/links',
        'http://weibo.com/links', 'https://blog.ojhdt.com/links', 'https://au.alibabacloud.com/links',
        'https://love109.cn/links', 'http://jianyi.baidu.com/links', 'https://www.wolfdan.cn/links',
        'https://www.gugugu.dev/links', 'http://wenku.baidu.com/links', 'https://xwmrcj.com/links',
        'https://cf.cndrew.cn/links', 'https://gitee.com/links', 'https://www.aliyun.com/links',
        'https://www.alibabacloud.com/links', 'https://my.alibabacloud.com/links', 'https://sso.qiniu.com/links',
        'https://hasaik.com/links', 'https://et.aliyun.com/links', 'http://www.cocoachina.com/links',
        'http://unlcedemon.online/links', 'https://hk.alibabacloud.com/links', 'https://boiltask.com/links',
        'https://www.w3cschool.cn/links', 'https://crosschannel.cc/links', 'http://image.baidu.com/links',
        'https://www.julydate.com/links', 'http://www.lostfawn.cn/links', 'http://www.dragonbaby308.com/links',
        'https://www.orchid-any.cf/links', 'http://v.baidu.com/links', 'https://lruihao.cn/links',
        'https://weibo.com/links', 'https://jambing.cn/links', 'https://www.xiongtianci.com/links',
        'http://absi2011.is-programmer.com/links', 'https://blog.berd.moe/links', 'https://www.qiniu.com/links',
        'https://wblog.tech/links', 'https://www.zhihu.com/links', 'https://tongji.baidu.com/links',
        'https://9527dhx.top/links', 'https://www.dreamwings.cn/links', 'http://www.baidu.com/links',
        'https://www.hojun.cn/links', 'http://zhidao.baidu.com/links']


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
            results = pool.map(process, waitSet)
        elif method == 'apply_async':
            pool = Pool(processes=max(1, cpu_count() - 1))
            results_tmp = [pool.apply_async(process, (waitQueue.get(),)) for _ in
                           range(min(cpu_count() - 1, waitQueue.qsize()))]
            pool.close()
            pool.join()
            results = [x.get() for x in results_tmp]
        elif method == 'gevent':
            results_tmp = [gevent.spawn(process, waitQueue.get()) for _ in
                           range(min(cpu_count() - 1, waitQueue.qsize()))]
            gevent.joinall(results_tmp)
            results = [x.get() for x in results_tmp]
        # 只处理此域名下url
        successSet = successSet.union(rootUrl for rootUrl, urls in results if len(urls) > 0)
        faultSet = faultSet.union(rootUrl for rootUrl, urls in results if len(urls) == 0)
        addWaitQueueSet = set([url + suffix for rootUrl, urls in results for url in urls])
        [waitQueue.put(url) for url in (addWaitQueueSet - waitQueueSet)]
        waitQueueSet = waitQueueSet.union(addWaitQueueSet)
        if not firstPageSet:
            # rootUrl 已有友联
            firstPageSet = addWaitQueueSet


time_map = dict()
for _ in range(10):
    t1 = datetime.datetime.now()
    down(method='map')
    t2 = datetime.datetime.now()
    down(method='apply_async')
    t3 = datetime.datetime.now()
    down(method='gevent')
    t4 = datetime.datetime.now()
    time_map['map'] = time_map.get('map', list()) + [(t2 - t1).total_seconds()]
    time_map['apply_async'] = time_map.get('apply_async', list()) + [(t3 - t2).total_seconds()]
    time_map['gevent'] = time_map.get('gevent', list()) + [(t4 - t3).total_seconds()]

time_series = pd.Series(time_map)
time_series.plot()
