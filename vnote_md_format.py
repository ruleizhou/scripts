# coding=utf-8
# 基于conda env:py35

# 功能说明
# 将vnote的md格式转为hexo的md格式，生成类似下面的文件前缀(同时，删除文件正文首行的title)  
# ---
# title: 理财_保险[博]  
# date: 2019-12-02 15:24:52  
# categories: ['生活', '其他']  
# tags: []  
# toc: true  
# 
# ---

# 用法说明和举例
# 用法 python vnote_md_format.py 目录
#   递归查询目录下所有md文件，生成md文件的前缀信息
# 用法 python vnote_md_format.py ./目录1/目录2/文件.md(x)
#   生成文件的前缀，此时文件的cate=目录1,目录2
# 用法 python vnote_md_format.py 文件.md
import argparse
import io
import os
import re
# 生成文件的前缀，此时文件的cate=空
import sys
import time

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.nlp.v20190408 import nlp_client, models
import hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

# 访问凭证去腾讯找，参考：https://console.cloud.tencent.com/nlp/basicguide
cred = credential.Credential("xxx", "yyy")
http_profile = HttpProfile()
http_profile.endpoint = "nlp.tencentcloudapi.com"

client_profile = ClientProfile()
client_profile.httpProfile = http_profile
client = nlp_client.NlpClient(cred, "ap-guangzhou", client_profile)
req = models.KeywordsExtractionRequest()

# 记录addr对应文章，用于输出冲突文章，手工处理
abbr_map = dict()


# 时间戳转换
def timestamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def get_file_datetime(fullFilePath: str):
    return timestamp_to_time(os.path.getctime(fullFilePath))


def get_file_categories(fullFilePath: str):
    return filter(lambda x: x != '.' and x != '/' and x != '', fullFilePath.split('/')[:-1])


def get_file_keywords(title: str):
    title = re.sub(r'\[.*?\]', r'', title).replace('_', ',')  # 去除[]中的东西
    title = re.sub(r'\d+', r'', title)
    params = '{"Num":10,"Text":"%s"}' % title
    req.from_json_string(params)
    resp = client.KeywordsExtraction(req)
    return [item.Word for item in resp.Keywords]


def get_file_abbr(title: str):
    return hashlib.md5(title.encode('utf-8')).hexdigest()[-8:]


class MdArticle(object):
    # 从文件中初始化
    def __init__(self, full_file_path=''):
        self.full_file_path = full_file_path
        self.title = ''
        self.date = ''
        self.categories = ''
        self.tags = ''
        self.keywords = ''
        self.abbrlink = ''
        self.data = []
        if self.full_file_path.strip():
            # 操作文件
            with open(self.full_file_path, 'r+') as f:
                end_line_num = 0
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
                            elif lines[i].startswith('keywords: '):
                                self.keywords = lines[i][9:].strip()
                            elif lines[i].startswith('tags: '):
                                self.tags = lines[i][5:].strip()
                            elif lines[i].startswith('abbrlink: '):
                                self.abbrlink = lines[i][10:].strip()
                        else:
                            end_line_num = i
                            break
                # 拼接新文件
                if end_line_num == 0:
                    self.data.extend(lines[0:])
                else:
                    self.data.extend(lines[end_line_num + 1:])
                f.close()
        return

    # 填充修改自身信息
    def fill_info(self):
        (file_path, full_filename) = os.path.split(self.full_file_path)
        (filename, file_extension) = os.path.splitext(full_filename)

        self.title = filename.replace('[博]', '')
        if not self.date:
            self.date = get_file_datetime(self.full_file_path)
        self.categories = str(list(get_file_categories(self.full_file_path)))
        if len(self.keywords) <= 0:
            self.keywords = ','.join(get_file_keywords(title=file_path.replace('/', ',') + ',' + self.title))

        if len(self.tags) <= 2:  # str形式list,至少含有[]2个字符
            self.tags = '[' + self.keywords + ']'

        if len(self.abbrlink.strip()) == 0:
            self.abbrlink = str(get_file_abbr(self.title))
        abbr_map[self.abbrlink] = abbr_map.get(self.abbrlink, list()) + [filename]
        return

    # 保存到文件中
    def save(self):
        # 获得文章date和tags(优先使用原有数据)
        file_prefix_lines = ['---\n']
        # 文件名，填充title
        file_prefix_lines.append('title: %s  \n' % self.title)
        # 文件创建时间，填充date
        file_prefix_lines.append('date: %s  \n' % self.date)
        # 文件相对路径，填充categories
        file_prefix_lines.append('categories: %s  \n' % str(self.categories))
        file_prefix_lines.append('keywords: %s  \n' % str(self.keywords))
        file_prefix_lines.append('tags: %s  \n' % str(self.tags))
        # 收尾
        file_prefix_lines.append('toc: true  \n')
        file_prefix_lines.append('abbrlink: %s  \n' % self.abbrlink)
        if self.title.find('[密]') > -1:
            file_prefix_lines.append('password: xxxxyyyy  \n')
        file_prefix_lines.append('\n---\n')
        # 标题也重新生成,标题不重新生成
        # filePrefixLines.append('# %s\n' % self.title)
        file_prefix_lines.extend(self.data)

        # 操作文件
        with open(self.full_file_path, 'r+') as f:
            f.truncate()
            f.writelines(file_prefix_lines)
            f.flush()
            f.close()
        return


# 处理单文件
def handle_file(full_file_path: str):
    if not full_file_path.endswith('.md'):
        return
    print(full_file_path)

    md_article = MdArticle(full_file_path)
    md_article.fill_info()
    md_article.save()


# 处理目录
def handle_dir(file_dir: str):
    # for root, dirs, files in os.walk(fileDir):
    #     for file in files:
    #         print(os.path.join(root, file))
    all_full_file_path = [os.path.join(root, file) for root, dirs, files in os.walk(file_dir) for file in files]
    [handle_file(full_file_path) for full_file_path in all_full_file_path]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_or_dir_list', type=str, nargs='+', help='file or dir list')

    args = parser.parse_args()
    file_or_dir_list = args.file_or_dir_list

    print('params: %s' % file_or_dir_list)
    for param in file_or_dir_list:
        if os.path.isdir(param):
            handle_dir(param)
        elif os.path.isfile(param):
            handle_file(param)
    abbr_conflict_map = {k: v for k, v in abbr_map.items() if len(v) > 1}
    print('abbr_conflict_map: %s' % str(abbr_conflict_map))
