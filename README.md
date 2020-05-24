# scripts
依赖conda环境（默认）：py35   

## 01,vnoteMdFormat.py  
功能说明  
将vnote的md格式转为hexo的md格式，生成类似下面的文件前缀(同时，删除文件正文首行的title)  
```
title: 理财_保险[博]  
date: 2019-12-02 15:24:52  
categories: ['生活', '其他']  
tags: []  
toc: true  
 
```

用法说明和举例  
用法 python vnoteMdFormat 目录  
&emsp;递归查询目录下所有md文件，生成md文件的前缀信息  
用法 python vnoteMdFormat ./目录1/目录2/文件.md(x)  
&emsp;生成文件的前缀，此时文件的cate=目录1,目录2  
用法 python vnoteMdFormat 文件.md  

举例：vnote原始文件：  
路径：xxx/vnote/生活/日记20200328.md  
内容:  

```
# 天气晴，32度，心情好
## 张三给我拳头
xxxxyyyyzzz
## 我打李四一巴掌
fffzzkkk
```
执行：python vnoteMdFormat.py xxx/vnote/生活/日记20200328.md  
这里转换后会在新md添加title信息  
```
title:日记20200328(注意:title其实是文件名)
date: 2020-03-01 16:18:26
categories: ['xxx','vnote','生活'](注意:这里即使就是文件的路径，切分)
tags: ['']
toc: true
```
正文部分:  
```
## 张三给我拳头  
xxxxyyyyzzz  
## 我打李四一巴掌  
fffzzkkk  
```
主意正文部分的title没了，原因是本人采用icarus模板，此模板也认可头部的title:xxxx这里作为标题，如果下面还有标题，显示时就是双标题，导致格式错乱  
如果你采用Next模板，则不同，需稍微改下代码，保持正文首行的标题  
使用方法1,用于文件:python vnoteMdFormat.py xxxx/yyy.md  
使用方法2,用于目录:python vnoteMdFormat.py xxxx/yyyy/zzz/  
使用方法3,用于文件和目录且多个:python vnoteMdFormat.py xxxx/yyy.md  xxxx/yyyy/zzz/  xxxx/yyyy/fff/  

特殊说明：
01,文章的categories其实是文件路径切分，所以执行脚本前,vnoteMdFormat.py文件位置最好和md文件或者文件夹同级位置  
比如：脚本位置:/xxx/yyy/zzz/vnoteMdFormat.py  
你的md文件位置:/fff/mmm/kkk/vnote/生活/日记20200328.md  
此时如果你在路径:/xxx/yyy/zzz/下执行脚本,python vnoteMdFormat.py /fff/mmm/kkk/vnote/生活/日记20200328.md  
这样的话md文件的categories,是，fff,mmm,kkk,vnote,生活,但大多数情况，fff,mmm,可能是没用的，比如home/username/等无意义的  
所以建议，将vnoteMdFormat.py放到/fff/mmm/kkk/vnote/下面，在/fff/mmm/kkk/vnote/下执行:python vnoteMdFormat.py 生活/日记20200328.md  
如此的化，生成的文章的categories则为['生活'],基本符合本意  
如下命令是：  
1,vnoteMdFormat.py复制到md所在文件夹　/home/john/文档/vnote_notebooks/vnote/  
2,在md所在文件夹外执行python vnoteMdFormat.py $(ls -I _v_recycle_bin)  
3,删除第１步复制过来的vnoteMdFormat.py脚本文件  
建议使用前，单个步骤执行下，看下各个命令都什么效果，避免错了，还要在修改.md文件  
```
cp vnoteMdFormat.py /home/john/文档/vnote_notebooks/vnote/ && cd /home/john/文档/vnote_notebooks/vnote/ && conda activate py35 && python vnoteMdFormat.py $(ls -I _v_recycle_bin) && rm vnoteMdFormat.py 
```

02,阅读代码可以发现，对于文章标题(也即是文件名)如果含有[密]，则自动增加字段password: xxxxyyyy ,为了实现对文章添加密码，没有密码无法访问（需要hexo插件配合)  


## 02,vnote2hexo.sh(vnote2hexo.py)
基于vnote的自动发布  
将vnote中的符合条件的文章（.md文件）,复制到hexo/source/_posts/,  
符合条件的md文章里面涉及的图片，复制到hexo/source/images/(并修改其内部引用路径格式)  
使用方法：  
```
./vnote2hexo.sh ~/文档/vnote_notebooks/vnote ~/my_hexo/source "*发布*.md"
```
大概执行路径：  
find   
vnote笔记本路径：\~/文档/vnote_notebooks/vnote   
找出其中文明名符合:"*发布*.md"  
的md文件，将其copy到  
hexo的source文件夹(路径):\~/my_hexo/source/_posts/(后面的_posts脚本写死的)  
同时,符合条件的md文件里面的*.png,*.jpeg等文件会复制到  
hexo的source文件夹(路径):\~/my_hexo/source/images/(后面的images脚本写死的)  
代码行数不多，但是较难看懂，主要是awk语法使用较多，其中很多涉及多次转义的字符  
参考本博客博文：脚本_vnote同步到hexo步骤[博]（自行搜索）  

vnote2hexo.sh废弃(sh复杂命令调试麻烦)  

vnote2hexo.py  
用法:  
```
python vnote2hexo.py /home/john/文档/vnote_notebooks/vnote /home/john/my_hexo/source '\[博\].*\.md' '/home/john/my_hexo/source/images_out/water.png'
```

## 03,cta_machineInfo.py  
功能：显示ubuntu下cta软件获取到的机器信息（无法通过验证时，自查问题使用）  
python cta_machineInfo/cta_machineInfo.py   
```
b'2@2020-04-11 18:04:54@172.17.0.1@172.16.0.239@0242b4365d41@aced5cf6d10a@john-P95-@4.15.@@@'
c_int(90)
```

## 04,downDeepArts.py
递归采集友情链接  

## 05,pkl2Csv.py
将pkl转为csv格式(方便直接导入数据库等）  
```
python xx.py pklPath raname_map
python pkl2Csv.py ~/下载/dd_price_vp_20190601_20200421.pkl '{"index":"datetime","minor_xs":"code","volume":"vol"}'
```

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

## 07,validRtmp.py
寻找过滤有效的rtmp,or,rtsp直播地址  
python validRtmp.py rtmp,rtsp https://www.optbbs.com/thread-3439203-1-1.html  
步骤  
```
1,下载页面：https://www.optbbs.com/thread-3439203-1-1.html（避免使用csdn等，需点击触发显示全部的网页）  
2,正则匹配：rtmp://, rtsp://等地址  
3,[rtmp;//xx.com,rtsp://yy.com]使用ping+cv2.read()验证有效性  
```

## 08,concurrentOpt.py
并发网页下载的效率测试  