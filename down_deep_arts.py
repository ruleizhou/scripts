# encoding: UTF-8
# 环境:py35(gevent)

# 递归采集友情链接
# python down_deep_arts.py -s 'https://hexo.yuanjh.cn' -suf '/links'
# 步骤
# 1,https://hexo.yuanjh.cn => https://hexo.yuanjh.cn/links
# 2,https://hexo.yuanjh.cn/links => [http://xxx.yy.com,https://zz.ff.cn]
# 3,[http://xxx.yy.com,https://zz.ff.cn] => [http://xxx.yy.com/links,https://zz.ff.cn/links]
# => [(http://xxx.yy.com/links,[页面拥有子链接（根域名形式）]),(https://zz.ff.cn/links,[页面拥有子链接（根域名形式）])]
# => handleSet=[http://xxx.yy.com/links,https://zz.ff.cn/links]
#    waitSet=[页面拥有子链接（根域名形式）,页面拥有子链接（根域名形式）,,,]
# => 循环此步骤
import argparse
import datetime
import re
from multiprocessing import cpu_count, Pool, Queue
from typing import List, Tuple

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


def process(url: str):
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


def handle_data(result: Tuple[str, List[str]]):
    global wait_queue_set
    url, urls = result
    if len(urls) > 0:
        success_set.add(url)
    else:
        fault_set.add(url)

    add_wait_queue_set = set([url + suffix for url in urls])
    [wait_queue.put(url) for url in (add_wait_queue_set - wait_queue_set)]
    wait_queue_set = wait_queue_set.union(add_wait_queue_set)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seed_url', type=str, help='seed url address')
    parser.add_argument('-suf', '--suffix', type=str, help='suffix')
    parser.add_argument('-maxc', '--max_count', type=int, default=100, help='max count of url')
    parser.add_argument('-maxd', '--max_depth', type=int, default=10, help='max depth of url')

    args = parser.parse_args()
    root_url = args.seed_url
    suffix = args.suffix
    max_count = args.max_count
    max_depth = args.max_depth

    start_time = datetime.datetime.now()
    print('all start:' + str(start_time))

    # 满足这个pattern的认为是本站文章
    wait_queue = Queue()
    wait_queue.put(root_url + suffix)
    wait_queue_set = set(root_url + suffix)
    success_set = set()
    fault_set = set()

    results_tmp = list()
    results = list()
    first_page_set = set()

    while len(success_set) < max_count and wait_queue.qsize():
        # 挪外面最好，但未有合适处理方案（close无法open）
        pool = Pool(processes=max(1, cpu_count() - 1))
        results_tmp = [pool.apply_async(process, (wait_queue.get(),), callback=handle_data) for _ in range(min(cpu_count() - 1, wait_queue.qsize()))]
        pool.close()
        pool.join()
        print('wait_set len:%s success_set:%s fault_set:%s' % (wait_queue.qsize(), len(success_set), len(fault_set)))
    print('successSet:%s fault_set:%s' % (len(success_set), len(fault_set)))
    print('successSet minus first_page_set:%s' % list(success_set - first_page_set))
    endTime = datetime.datetime.now()
    print('all end:' + str(endTime))
    print('spend seconds:%s' % (endTime - start_time).total_seconds())
