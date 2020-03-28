# scripts

## vnote2hexo.sh
将vnote中的符合条件的文章（.md文件）,复制到hexo/source/_posts/  
符合条件的md文章里面涉及的图片，复制到hexo/source/images/  
使用方法：  
```
./vnote2hexo.sh ~/文档/vnote_notebooks/vnote ~/my_hexo/source "*发布*.md"
```
大概执行路径：  
find   
vnote笔记本路径：~/文档/vnote_notebooks/vnote   
找出其中文明名符合:"*发布*.md"  
的md文件，将其copy到  
hexo的source文件夹(路径):~/my_hexo/source/_posts/(后面的_posts脚本写死的)  
同时,符合条件的md文件里面的*.png,*.jpeg等文件会复制到  
hexo的source文件夹(路径):~/my_hexo/source/images/(后面的images脚本写死的)  
代码行数不多，但是较难看懂，主要是awk语法使用较多，其中很多涉及多次转义的字符  
参考本博客博文：脚本_vnote同步到hexo步骤[博]（自行搜索）  

