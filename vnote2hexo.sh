#!/bin/bash
# 删除hexo已有的文章和附件
echo "删除hexo博客下的文件夹_posts,images"
rm $2/_posts/* 
rm $2/images/*

# 创建临时目录
echo "创建临时目录"
mkdir -p ~/tmp_hexo/tmp_png/;cd ~/tmp_hexo

# 需发布到hexo文件路径写到md_file_loc.txt中,并且生成copy命令列表
echo "生成hexo的文件copy命令"
find $1/ -path $1/_v_recycle_bin -prune -o  -name "$3" -print | grep -v total >md_file_loc.txt
sed -i 's/(/\\(/g;s/)/\\)/g'   md_file_loc.txt
awk  -v  to="$2/_posts/" '{cmd="cp  "$0" "to ; system(cmd)}'  md_file_loc.txt

# 将hexo文件中的图片地址,提取到md_file_loc.txt中
echo "hexo文件中的图片地址,提取到md_file_loc.txt中"
find $1/ -path $1/_v_recycle_bin -prune -o  -regex ".*\.jpg\|.*\.png" -print | grep -v total > tmp_png.txt
awk  -v  to="~/tmp_hexo/tmp_png/" '{cmd="cp  "$0" "to ; system(cmd)}'  tmp_png.txt
awk -F / -v patten="'[0-9_]+\.png'"  -v mdPath="$2/_posts/" '{cmd= "grep -o -E " patten " " mdPath $NF;system(cmd)}' md_file_loc.txt | grep -v total > tmp_png_choose.txt
awk -v from="./tmp_png/" -v to="$2/images/" '{cmd="mv "from $1 " " to ;system(cmd)}' tmp_png_choose.txt

# 替换文件路径(vnote图片位于_v_images下，而hexo图片位置为images)
echo "替换文件路径"
awk -F / -v newPath="$2/_posts/" -v sedCmd="'s/_v_images/\\\\/images/g'"  '{cmd= "sed -i "  sedCmd " " newPath $NF;system(cmd) }' md_file_loc.txt
awk -F / -v newPath="$2/_posts/" -v sedCmd="'s/ =[0-9]\+x)/)/g'"  '{cmd= "sed -i "  sedCmd " " newPath $NF;system(cmd) }' md_file_loc.txt

# 删除临时目录
echo "删除临时目录"
rm md_file_loc.txt  tmp_png.txt tmp_png_choose.txt
rm -rf tmp_png/*

# 发布到hexo
echo "发布到hexo"
cd $2/../;hexo g && hexo deploy
echo "完成"
