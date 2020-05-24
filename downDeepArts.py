# encoding: UTF-8
# 环境:py35(gevent)

# 递归采集友情链接
# python xx.py rootUrl suffix maxCount maxDepth
# python xx.py 'https://hexo.yuanjh.cn' '/links' 100 10
# 步骤
# 1,https://hexo.yuanjh.cn => https://hexo.yuanjh.cn/links
# 2,https://hexo.yuanjh.cn/links => [http://xxx.yy.com,https://zz.ff.cn]
# 3,[http://xxx.yy.com,https://zz.ff.cn] => [http://xxx.yy.com/links,https://zz.ff.cn/links]
# => [(http://xxx.yy.com/links,[页面拥有子链接（根域名形式）]),(https://zz.ff.cn/links,[页面拥有子链接（根域名形式）])]
# => handleSet=[http://xxx.yy.com/links,https://zz.ff.cn/links]
#    waitSet=[页面拥有子链接（根域名形式）,页面拥有子链接（根域名形式）,,,]
# => 循环此步骤

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
maxCount = 100
maxDepth = 10


# rootUrl = sys.argv[1]
# suffix = sys.argv[2]
# maxCount = int(sys.argv[3])
# maxDepth = int(sys.argv[4])
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


startTime = datetime.datetime.now()
print('all start:' + str(startTime))

# 满足这个pattern的认为是本站文章
waitQueue = Queue()
waitQueue.put(rootUrl + suffix)
waitQueueSet = set(rootUrl + suffix)
successSet = set()
faultSet = set()
# 按照maxDepth限制，分批次处理（想了一堆并行化方法，最后决定采用这种，（思路）简单，（并行）朴素，（代码）易懂，（综合）不易错的最老实方案）
# 核心原则：
# 01，最慢（网络）的地方采用并行化
# 02，能不采用多进程机制（锁，队列，消息等）就不采用，角度：代码复杂度，易调试度，系统的外部依赖度
results_tmp = list()
results = list()
while len(successSet) < maxCount and waitQueue.qsize():
    # 挪外面最好，但未有合适处理方案（close无法open）
    pool = Pool(processes=max(1, cpu_count() - 1))
    results = pool.map(process, [waitQueue.get() for x in range(min(cpu_count() - 1, waitQueue.qsize()))])
    pool.close()
    pool.join()

    # 只处理此域名下url
    successSet = successSet.union(rootUrl for rootUrl, urls in results if len(urls) > 0)
    faultSet = faultSet.union(rootUrl for rootUrl, urls in results if len(urls) == 0)
    addWaitQueueSet = set([url + suffix for rootUrl, urls in results for url in urls])
    [waitQueue.put(url) for url in (addWaitQueueSet - waitQueueSet)]
    waitQueueSet = waitQueueSet.union(addWaitQueueSet)
    print('waitSet len:%s successSet:%s faultSet:%s' % (waitQueue.qsize(), len(successSet), len(faultSet)))
print('successSet:%s faultSet:%s' % (len(successSet), len(faultSet)))
print('successSet:%s' % list(successSet))
endTime = datetime.datetime.now()
print('all end:' + str(endTime))
print('spend seconds:%s' % (endTime - startTime).total_seconds())
