# scripts
依赖conda环境（默认）：py35   


## 06,hexoAddr2Vnote.py
功能说明  
将hexo文件夹_post里面的.md文件里面的abbrlink提取出来，写入到自己的md编辑工具的文件夹下（本人使用vnote编辑md，故vnote举例），避免后续修改文章title导致生成网页链接变化的问题  
问题场景：之前使用hexo-abbrlink插件自动生成abbr属性（对应网页的html地址）  
但是存在问题，如果修改文档标题，则会导致新生成abbr和原有abbr不同，意味着原来搜索引擎的索引将会无效  
问题解决：  
1，将hexo生成的abbr，会写到vnote的原始md中，这样即使修改标题，也不会重新计算abbr（继承方式使用）  
2，在python脚本中生成abbr，不在依赖hexo-abbrlink脚本，主要是每次发布文章，都要跑一遍hexo g(生成addr=>hexo.md,hexo.md=>vnote.md，)麻烦  
不如直接vnote.md=>vnote.md，生成title等头部信息时生成abbr(同时避免重复）  

用法说明和举例  
python hexoAddr2Vnote.py hexo_post_dir vnote_dir line_num  
hexo_post_dir hexo的_post文件夹路径  
vnote_dir vnote的md文件夹路径  
line_num 写到vnote里面md文件的第几行，一般第一行是---,第二行是title: xxx,看自己文件情况  
实例：python hexoAddr2Vnote.py '/home/john/my_hexo/source/_posts' '/home/john/文档/vnote_notebooks/vnote' 3  

## 08,concurrentOpt.py,concurrentOptGevent.py(concurrent/opt.py,concurrent/optGevent.py)     
并发网页下载的效率测试  

| concurrentOpt | 进程or线程 | 同步or异步(不大确定) | 阻塞or非阻塞(不大确定) |  平均时间   |
| ------------- | -------- | ----------------- | ------------------ | ---------- |
| thread_multi  | 多线程     | 异步              | 非阻塞              | 8.0576371  |
| thread_map    | 线程池     | (批)同步           | 阻塞                | 10.4831831 |
| thread_async  | 线程池     | 异步              | 非阻塞              | 9.8210853  |
| process_multi | 多进程     | 异步              | 非阻塞              | 8.0897814  |
| process_map   | 进程池     | （批）同步          | 阻塞                | 11.2688131 |
| process_async | 进程池     | 异步              | 非阻塞              | 11.1745724 |


| concurrentOptGevent | 进程or线程 | 同步or异步(不大确定) | 阻塞or非阻塞(不大确定) |  平均时间  |
| ------------------ | -------- | ----------------- | ------------------ | --------- |
| thread_multi        | 多线程     | 异步              | 非阻塞              | 6.7499353 |
| thread_map          | 线程池     | （批）同步          | 非阻塞              | 9.0923011 |
| thread_async        | 线程池     | 异步              | 非阻塞              | 8.9605548 |
| process_multi       | 多进程     | 异步              | 非阻塞              | 7.1163604 |
| process_map         | 进程池     | （批）同步          | 非阻塞              | 卡住      |
| process_async       | 进程池     | 异步              | 非阻塞              | 卡住      |
| gevent_test         | 协程      | 异步              | 非阻塞              | 5.956831 |

结论:  
01，启用gevent后，除了卡住的，线程和进程均加快1s左右时间  
02，协程在线程程序中是最快的  
03，多线程程序下载速度弱优于多进程  
04，不论是进程还是线程，使用thread_async都快于map  
05，不考虑协程时，多线程较线程池速度更快，多进程较进程池速度更快，这一点不大符合理论，个人感觉和url数量少有关.  

至于进程池在启用gevent后卡住的问题，网上也没查到相关的靠谱资料，哪位大牛晓得的话，求解释～  

## 09,concurrent/threadShare.py  
线程数据共享，测试代码  
