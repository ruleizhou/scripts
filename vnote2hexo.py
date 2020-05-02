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
        findAll = re.findall(r"([\d_]+\.(png|jpg|jpeg|gif))", content, re.I | re.S | re.M)
        if findAll:
            return [k for k, v in findAll]
    return list()


# vnote_dir = '/home/john/文档/vnote_notebooks/vnote'
# hexo_source_dir = '/home/john/my_hexo/source'
# filter_reg = '\[博\].*\.md'

print('params:' + str(sys.argv[1:]))

vnote_dir = sys.argv[1]
hexo_source_dir = sys.argv[2]
filter_reg = sys.argv[3]
hexo_md_paths = list()
lost_imgs = list()
for dirpath, dirnames, filenames in os.walk(vnote_dir):
    for name in filenames:
        if re.search(filter_reg, name, re.M | re.I):
            # 采集文中图片
            img_paths = [dirpath + '/_v_images/' + img for img in getImgs(dirpath + '/' + name)]
            # 文章copy到文章文件夹
            hexo_md_dir = hexo_source_dir + '/_posts'
            hexo_img_dir = hexo_source_dir + '/images'
            shutil.copy(dirpath + '/' + name, hexo_md_dir)
            # 图片copy到图片文件夹
            if img_paths:
                try:
                    list(map(lambda img_path: shutil.copy(img_path, hexo_img_dir), img_paths))
                except Exception as e:
                    lost_imgs.append(e.filename)
            # 文章内部修改图片引用路径
            hexo_md_path = hexo_md_dir + '/' + name
            hexo_md_paths.append(hexo_md_path)
            with open(hexo_md_path, 'r+', encoding='utf-8') as f:
                content = ''.join(f.readlines())
                # _v_images => images
                content = content.replace('_v_images', 'images')
                # (xx.png =500x) => (xx.png)
                content = re.sub(r"(png|jpg|jpeg|gif) =\d+x", r"\1", content)
                f.seek(0)
                f.truncate()
                f.seek(0)
                f.write(content)
print('hexo_md_paths:\n%s \n %d' % ('\n'.join(hexo_md_paths), len(hexo_md_paths)))
print('hexo_img_lost:\n%s \n %d' % ('\n'.join(lost_imgs), len(lost_imgs)))
