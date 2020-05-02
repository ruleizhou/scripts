# coding=utf-8
# 基于conda env:py35
# 功能说明
# 基于vnote的自动发布
# 将vnote中的符合条件的文章（.md文件）,复制到hexo/source/_posts/,
# 符合条件的md文章里面涉及的图片，复制到hexo/source/images/(并修改其内部引用路径格式)

# 用法说明和举例
# 使用方法:python vnote2hexo.py /home/john/文档/vnote_notebooks/vnote /home/john/my_hexo/source "*发布*.md"
import os, sys, re
import shutil


def getImgs(file_path):
    with open(file_path, 'r') as f:
        content = ''.join(f.readlines())
        return re.findall(r"([\d_]+\.(png|jpg|jpeg|gif))", content, re.I | re.S | re.M)[0]
    return list()


vnote_dir = '/home/john/文档/vnote_notebooks/vnote'
hexo_source_dir = '/home/john/my_hexo/source'
filter_reg = '\[博\].*\.md'

for dirpath, dirnames, filenames in os.walk(vnote_dir):
    for name in filenames:
        if re.search(filter_reg, name, re.M | re.I):
            # 采集文中图片
            img_paths = [dirpath + '/' + img for img in getImgs(dirpath + '/' + name)]
            # 文章copy到文章文件夹
            shutil.copy(dirpath + '/' + name, vnote_dir)
            # 图片copy到图片文件夹
            if img_paths:
                map(lambda x: shutil.copy(img_path, vnote_dir + '/images'), img_paths)
            # 文章内部修改图片引用路径
            hexo_md_path = vnote_dir + '/' + name
            with open(hexo_md_path, 'w') as f:
                content = ''.join(f.readlines())
                # _v_images => images
                content = content.replace('_v_images', 'images')
                # (xx.png =500x) => (xx.png)
                content = re.sub(r"(png|jpg|jpeg|gif) =\d+x", r"\1", content)
                f.write(content)

# # 发布到hexo
# echo "发布到hexo"
# cd $2/../;hexo g && hexo deploy
# echo "完成"
