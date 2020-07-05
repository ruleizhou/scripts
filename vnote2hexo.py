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
import subprocess
from collections import defaultdict, Counter


def getImgsAndTags(file_path):
    imgs = list()
    tags = list()
    with open(file_path, 'r') as f:
        lines = f.readlines()
        tags = lines[5].strip().replace('tags: ', '').replace('[', '') \
            .replace(']', '').replace('\'', '').replace('\"', '').split(',')

        content = ''.join(lines[9:])
        findAllImgs = re.findall(r"([\d_]+\.(png|jpg|jpeg|gif))", content, re.I | re.S | re.M)
        if findAllImgs:
            imgs = [k for k, v in findAllImgs]

    return imgs, tags


# 添加水印
def waterMark(file_path, water_path):
    if not water_path:
        return
    ffmpeg_cmd = "ffmpeg -i %s -i %s -filter_complex 'overlay=main_w-overlay_w-10 : main_h-overlay_h-10' %s -y" % (
        file_path, water_path, file_path)
    subprocess.call(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# vnote_dir = '/home/john/文档/vnote_notebooks/vnote'
# hexo_source_dir = '/home/john/my_hexo/source'
# filter_reg = '\[博\].*\.md'
# water_path = '/home/john/my_hexo/source/images_out/water.png'
#
print('params:' + str(sys.argv[1:]))

vnote_dir = sys.argv[1]
hexo_source_dir = sys.argv[2]
filter_reg = sys.argv[3]
water_path = sys.argv[4]

print('清空hexo文件夹_posts,images')
hexo_md_dir = hexo_source_dir + '/_posts'
hexo_img_dir = hexo_source_dir + '/images'
clean_hexo_cmd = 'rm -rf %s/*' % (hexo_md_dir)
subprocess.call(clean_hexo_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

hexo_md_paths = list()
lost_imgs = list()
new_imgs = list()
hexo_exist_imgs = set(os.listdir(hexo_img_dir))
pathTagsMap = defaultdict(list)
for dirpath, dirnames, filenames in os.walk(vnote_dir):
    if dirpath.find('_v_recycle_bin') > -1:
        continue
    for name in filenames:
        if re.search(filter_reg, name, re.M | re.I):
            # 采集文中图片
            img_names, tags = getImgsAndTags(dirpath + '/' + name)
            # 文章copy到文章文件夹
            shutil.copy(dirpath + '/' + name, hexo_md_dir)
            # 图片copy到图片文件夹
            img_names = list(set(img_names) - set(hexo_exist_imgs))
            if img_names:
                try:
                    vnote_img_dir = dirpath + '/_v_images'
                    # 图片复制
                    list(map(lambda img_name: shutil.copy(vnote_img_dir + '/' + img_name, hexo_img_dir), img_names))
                    # 图片加水印
                    list(map(lambda img_name: waterMark(hexo_img_dir + '/' + img_name, water_path), img_names))
                    new_imgs.extend(img_names)
                except Exception as e:
                    lost_imgs.append(e.filename)
            # 文章内部修改图片引用路径
            hexo_md_path = hexo_md_dir + '/' + name
            hexo_md_paths.append(hexo_md_path)
            with open(hexo_md_path, 'r+', encoding='utf-8') as f:
                content = ''.join(f.readlines())
                # _v_images => images
                content = content.replace('_v_images/', '/images/')
                # (xx.png =500x) => (xx.png)
                content = re.sub(r"(png|jpg|jpeg|gif) =\d+x", r"\1", content)
                f.seek(0)
                f.truncate()
                f.seek(0)
                f.write(content)

            # 收集各路径下的tags
            pathTagsMap[dirpath].extend(tags)
for key,value in pathTagsMap.items():
    pathTagsMap[key]=Counter(value)
print('标签信息')
import pandas as pd
tagDf=pd.DataFrame(columns=['path1','path2','tags'])
for key,count_map in pathTagsMap.items():
    keys=key.split('/')
    tagDf.loc[tagDf.shape[0]]=[keys[1],keys[2],','.join(['<a href="/tags/%s" >%s(%s)</a>'%(tag,tag,value) for tag,value in count_map.items()])]

print('hexo_md_paths:\n%s \n %d' % ('\n'.join(hexo_md_paths), len(hexo_md_paths)))
print('hexo_img_new:\n%s \n %d' % ('\n'.join(new_imgs), len(new_imgs)))
print('hexo_img_lost:\n%s \n %d' % ('\n'.join(lost_imgs), len(lost_imgs)))
print('records')
print(tagDf.to_dict('records'))