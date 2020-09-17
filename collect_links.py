# encoding: UTF-8
# 环境:py35(gevent)

# 过度设计？一定程度yes，为何？大多数研发都是欠债式研发，理论上设计10，实际设计到7，然后3用补丁形式实现。等到需求变更后，之前的设计支持到3，补丁7时再重构
# 然后周而复始。开发补丁重构，开发补丁冲够
# 　设计模式目的：形式目的，高内聚，低耦合，终极目的：简单，易读，易改
# 知识点，树的先广遍历（队列），代理模式，多线程，生成者消费者，跨线程数据共享－队列（阻塞）

# 递归采集友情链接
# python collect_links.py -s 'https://hexo.yuanjh.cn' -suf '/links'
# 步骤
# 1,https://hexo.yuanjh.cn => https://hexo.yuanjh.cn/links
# 2,https://hexo.yuanjh.cn/links => [http://xxx.yy.com,https://zz.ff.cn]
# 3,[http://xxx.yy.com,https://zz.ff.cn] => [http://xxx.yy.com/links,https://zz.ff.cn/links]
# => [(http://xxx.yy.com/links,[页面拥有子链接（根域名形式）]),(https://zz.ff.cn/links,[页面拥有子链接（根域名形式）])]
# => handleSet=[http://xxx.yy.com/links,https://zz.ff.cn/links]
#    waitSet=[页面拥有子链接（根域名形式）,页面拥有子链接（根域名形式）,,,]
# => 循环此步骤
import argparse
import re
import threading
from multiprocessing import cpu_count, Pool, Queue
from typing import List, Tuple, Callable
import requests
from contextlib2 import suppress


class UniqueQueue:
    def __init__(self, maxsize: int = 0, key: Callable = None) -> None:
        """
        tool,unique queue,only put same item once

        :rtype: None
        :param maxsize: queue max size ,when empty get() or full put() will stuck as common Queue
        :param key: generate unique key func,two item have same unique key will put queue only once(first time)
        """
        self.key = key
        self.queue = Queue(maxsize=maxsize)
        self.unique_set = set()

    def put(self, item: Tuple[int,str]) -> bool:
        """
        add new item to unique queue

        :rtype: success or fail
        :param item :item[0] depth of url,item[1] url
        """
        unique_key = self.key(item) if self.key else item
        return unique_key not in self.unique_set and self.queue.put(item) or self.unique_set.add(unique_key)

    def get(self) -> Tuple[int, str]:
        return self.queue.get()

    def empty(self) -> bool:
        return self.queue.empty()


class CollectLinks:
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

    def __init__(self, seed_url: object, suffix: object, max_count: object = 100, max_depth: object = 10) -> None:
        """
        初始化实例

        :rtype: None
        :param seed_url: 种子链接
        :param suffix: 后缀
        :param max_count: 最大采集链接个数
        :param max_depth: 最大采集链接深度
        """
        self.seed_url = seed_url
        self.max_depth = max_depth
        self.max_count = max_count
        self.suffix = suffix
        self.queue = UniqueQueue(key=lambda x: x[1])
        self.success_set = set()

    def process_queue(self) -> None:
        """
        广度遍历形式解析url对应网页中的url地址,并回送到任务队列

        1,从任务队列unique queue中获取到url
        2,下载解析url,获取网页中的url地址
        3,将url地址加入到unique queue中

        """
        depth = 0
        while len(self.success_set) < self.max_count and depth < self.max_depth :
            depth, url = self.queue.get()
            content = ''
            with suppress(Exception):
                print('requests depth:%d %d url:%s' % (depth, len(self.success_set), url))
                response = requests.get(url, headers=self.headers, timeout=(3, 7))
                if not response.ok:
                    continue
                content = response.text.replace(" ", "")
            res_url = r"href=[\"\'](https?://[^/'\"\?><]+)"
            urls = re.findall(res_url, content, re.I | re.S | re.M)
            urls and self.success_set.add(url)
            [self.queue.put((depth + 1, url + self.suffix)) for url in urls]

    def collect(self)-> None:
        """
        启动多线程进行网页广度采集任务

        """
        self.queue.put((1, self.seed_url + self.suffix))
        thread_count = cpu_count()*2 - 1
        thread_list = [threading.Thread(target=self.process_queue, ) for _ in range(thread_count)]
        [thread.start() for thread in thread_list]
        [thread.join() for thread in thread_list]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seed_url', type=str, help='seed url address')
    parser.add_argument('-suf', '--suffix', type=str, help='suffix')
    parser.add_argument('-maxc', '--max_count', type=int, default=100, help='max count of url')
    parser.add_argument('-maxd', '--max_depth', type=int, default=10, help='max depth of url')

    args = parser.parse_args()
    collect_links = CollectLinks(seed_url=args.seed_url, suffix=args.suffix, max_count=args.max_count,
                                 max_depth=args.max_depth)
    collect_links.collect()
    print(collect_links.success_set)
