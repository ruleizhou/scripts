# coding=utf-8
# 基于conda env:py35

# 类似下面的文件前缀
# ---
# title: 01_原因
# date: 2019-11-30 00:00:01
# categories:
#  - 技术
#  - java
# ---

# 用法 python md2hexo 目录
#   递归查询目录下所有md文件，生成md文件的前缀信息
# 用法 python md2hexo ./目录1/目录2/文件.md(x)
#   生成文件的前缀，此时文件的cate=目录1,目录2
# 用法 python md2hexo 文件.md
#   生成文件的前缀，此时文件的cate=空
import sys
import os
import time
import io
from aip import AipNlp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')


""" 你的 APPID AK SK """
APP_ID = '18685503'
API_KEY = '4GrRGHgohbxaoPY8xG1WKQGa'
SECRET_KEY = 'goGoz3Y71gLgv4ZOAmNGWEnwZZqpjVce'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)


# 时间戳转换
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


def getFileDatetime(fullFilePath):
    return TimeStampToTime(os.path.getctime(fullFilePath))


def getFileCategories(fullFilePath):
    return filter(lambda x: x != '.' and x != '/' and x != '', fullFilePath.split('/')[:-1])


def getFileTags(title, content):
    retJson=client.keyword(str(title.encode("GBK",'ignore')), str(content.encode("GBK",'ignore')))
    return [item.get('tag') for item in retJson.get('items',[])][:5]


class MdArticle(object):
    # 从文件中初始化
    def __init__(self, fullFilePath=''):
        self.fullFilePath = fullFilePath
        self.title = ''
        self.date = ''
        self.categories = ''
        self.tags = ''
        self.data = []
        if self.fullFilePath.strip():
            # 操作文件
            with open(self.fullFilePath, 'r+') as f:
                endLineNum = 0
                lines = f.readlines()
                if len(lines) > 0 and lines[0] == '---\n':
                    for i in range(1, len(lines)):
                        if lines[i] != '---\n':
                            if lines[i].startswith('title: '):
                                self.title = lines[i][7:].strip()
                            elif lines[i].startswith('date: '):
                                self.date = lines[i][6:].strip()
                            elif lines[i].startswith('categories: '):
                                self.categories = lines[i][12:].strip()
                            elif lines[i].startswith('tags: '):
                                self.tags = lines[i][5:].strip()
                        else:
                            endLineNum = i
                            break
                # 拼接新文件
                if endLineNum == 0:
                    self.data.extend(lines[0:])
                else:
                    self.data.extend(lines[endLineNum +  1:])
                f.close()
        return

    # 填充修改自身信息
    def fillInfo(self):
        (filePath, fullFileName) = os.path.split(self.fullFilePath)
        (fileName, fileExtension) = os.path.splitext(fullFileName)

        self.title = fileName
        if not self.date:
            self.date = getFileDatetime(self.fullFilePath)
        self.categories = str(list(getFileCategories(self.fullFilePath)))
        if len(self.tags) <= 2:  # str形式list,至少含有[]2个字符
            self.tags = str(getFileTags(title=self.title, content=','.join(self.data)))

        return

    # 保存到文件中
    def save(self):
        # 获得文章date和tags(优先使用原有数据)
        filePrefixLines = ['---\n']
        # 文件名，填充title
        filePrefixLines.append('title: %s  \n' % self.title)
        # 文件创建时间，填充date
        filePrefixLines.append('date: %s  \n' % self.date)
        # 文件相对路径，填充categories
        filePrefixLines.append('categories: %s  \n' % str(self.categories))
        filePrefixLines.append('tags: %s  \n' % str(self.tags))
        # 收尾
        filePrefixLines.append('toc: true  \n')
        if self.title.find('密') > -1:
            filePrefixLines.append('password: xxxxyyyy  \n')
        filePrefixLines.append('\n---\n')
        # 标题也重新生成,标题不重新生成
        #filePrefixLines.append('# %s\n' % self.title)
        filePrefixLines.extend(self.data)

        # 操作文件
        with open(self.fullFilePath, 'r+') as f:
            f.truncate()
            f.writelines(filePrefixLines)
            f.flush()
            f.close()
        return

# 处理单文件
def handleFile(fullFilePath):
    if not fullFilePath.endswith('.md'):
        return
    print(fullFilePath)

    mdArticle = MdArticle(fullFilePath)
    mdArticle.fillInfo()
    mdArticle.save()


# 处理目录
def handleDir(fileDir):
    # for root, dirs, files in os.walk(fileDir):
    #     for file in files:
    #         print(os.path.join(root, file))
    allFullFilePath = [os.path.join(root, file) for root, dirs, files in os.walk(fileDir) for file in files]
    [handleFile(fullFilePath) for fullFilePath in allFullFilePath]


# fullFilePath = '/home/john/abc.md'
# handleFile(fullFilePath)
# fileDir = './test1/test2/'
# handleDir(fileDir)
# fullFilePath = 'abc.md'
# handleFile(fullFilePath)

param = sys.argv[1]
if os.path.isdir(param):
    handleDir(param)
elif os.path.isfile(param):
    handleFile(param)


