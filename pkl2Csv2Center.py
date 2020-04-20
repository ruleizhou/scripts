# encoding: UTF-8
# 基于conda env:vnpy19(含有pandas即可)

# 将pkl转为csv格式(方便直接导入数据库等）
# python xx.py pklPath raname_map
# python pkl2Csv2Center.py ~/下载/dd_price_vp_20190601_20200421.pkl '{"index":"datetime","minor_xs":"code","volume":"vol"}'
# 步骤
# 1,依次取得pkl文件minor_xs轴维度 as df
# 2,df.reset_index(),df.dropna(),df拼接为all_df
# 3,all_df.rename()
# 4,all_df.to_csv(index=False)


import os
import sys
import pandas as pd


# 获取文件路径、文件名、后缀
def file_path_split(filename):
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def pkl2Csv(file_path_pkl, rename_map=None):
    filepath, shotname, extension = file_path_split(file_path_pkl)
    file_path_csv = '%s/%s.%s' % (filepath, shotname, 'csv')
    print('to csv file:%s' % file_path_csv)
    future_data = pd.read_pickle(file_path_pkl)
    all_df = pd.DataFrame()  # columns=['datetime', 'open', 'high', 'low', 'close', 'vol', 'code']
    for minor_xs in future_data.minor_axis:
        print('symbol', minor_xs)
        try:
            df = future_data.minor_xs(minor_xs)
            if df is None:
                print("None %s" % minor_xs)
                continue
            df['minor_xs'] = minor_xs
            df = df.reset_index()
            # df.rename(columns={'index': 'datetime', 'volume': 'vol'}, inplace=True)
            df = df.dropna()
            all_df = all_df.append(df)
        except:
            pass
    if rename_map:
        all_df.rename(columns=rename_map, inplace=True)
    all_df.to_csv(file_path_csv, index=False)


# file_path_pkl = '/home/john/下载/dd_price_vp_20190601_20200421.pkl'
# rename_map = {'index': 'datetime', 'volume': 'vol'}

print('params:' + str(sys.argv[1:]))
file_path_pkl = sys.argv[1]
rename_map = eval(str(sys.argv[2]))
pkl2Csv(file_path_pkl, rename_map)
