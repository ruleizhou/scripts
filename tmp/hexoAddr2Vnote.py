# encoding: UTF-8

# 功能说明
# 将hexo文件夹_post里面的.md文件里面的abbrlink提取出来，写入到自己的md编辑工具的文件夹下（本人使用vnote编辑md，故vnote举例），避免后续修改文章title导致生成网页链接变化的问题
# 问题场景：之前使用hexo-abbrlink插件自动生成abbr属性（对应网页的html地址）
# 但是存在问题，如果修改文档标题，则会导致新生成abbr和原有abbr不同，意味着原来搜索引擎的索引将会无效
# 问题解决：
# 1，将hexo生成的abbr，会写到vnote的原始md中，这样即使修改标题，也不会重新计算abbr（继承方式使用），
# 2，在python脚本中生成abbr，不在依赖hexo-abbrlink脚本，主要是每次发布文章，都要跑一遍hexo g(生成addr=>hexo.md,hexo.md=>vnote.md，)麻烦
# 不如直接vnote.md=>vnote.md，生成title等头部信息时生成abbr(同时避免重复）

# 用法说明和举例
# python hexoAddr2Vnote.py hexo_post_dir vnote_dir line_num
# hexo_post_dir hexo的_post文件夹路径
# vnote_dir vnote的md文件夹路径
# line_num 写到vnote里面md文件的第几行，一般第一行是---,第二行是title: xxx,看自己文件情况
# 实例：python hexoAddr2Vnote.py '/home/john/my_hexo/source/_posts' '/home/john/文档/vnote_notebooks/vnote' 3

import os
import sys


# 读取文件abbrlink信息
def getAbbr(file_path):
    with open(file_path, encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith('abbrlink'):
                return line.split(':')[1].strip()
    return ''


# 文件指定行插入
def writeLine(path, content, line_num=0):
    lines = None
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if lines is None:
        return
    if line_num == 0:
        lines.insert(0, '{}\n'.format(content))
    else:
        lines.insert(line_num - 1, '{}\n'.format(content))
    with open(path, 'w') as f:
        f.write(''.join(lines))


# hexo_post_dir = '/home/john/my_hexo/source/_posts'
# vnote_dir = '/home/john/文档/vnote_notebooks/vnote'
# line_num = 3

print('params:' + str(sys.argv[1:]))
if len(sys.argv[1:]) != 3:
    raise Exception('need two param')

hexo_post_dir = sys.argv[1]
vnote_dir = sys.argv[2]
line_num = int(sys.argv[3])

# 读取所有hexo文件，构建 dict(filename:abbr)
file_names = os.listdir(hexo_post_dir)
file_abbrs = [getAbbr(hexo_post_dir + '/' + file_name) for file_name in file_names]
file_abbr_dict = {k: v for k, v in zip(file_names, file_abbrs)}

# 遍历vnote文件，如果dict存在文件名的abbr，则写入vnote的md中
for dirpath, dirnames, filenames in os.walk(vnote_dir):
    for name in filenames:
        if name in file_abbr_dict:
            writeLine(dirpath + '/' + name, content='abbrlink: %s  ' % file_abbr_dict.get(name, ''), line_num=line_num)

# 写入成功，则继续手工修改之前md发布脚本，title去除【博】，abbr的自动继承式填充
