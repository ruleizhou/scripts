# encoding: UTF-8
# 基于conda env:vnpy19(含有pandas即可)

# 将pkl转为csv格式(方便直接导入数据库等）
# python xx.py pklPath raname_map
# python pkl2csv.py ~/下载/dd_price_vp_20190601_20200421.pkl '{"index":"datetime","minor_xs":"code","volume":"vol"}'
# 步骤
# 1,依次取得pkl文件minor_xs轴维度 as df
# 2,df.reset_index(),df.dropna(),df拼接为all_df
# 3,all_df.rename()
# 4,all_df.to_csv(index=False)
import argparse
import os
import sys
from contextlib import suppress
from typing import Dict

import pandas as pd
import logging
logger = logging.getLogger()

# 获取文件路径、文件名、后缀
def file_path_split(filename: str):
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def pkl2csv(file_path_pkl: str, rename_map: Dict[str, str] = None):
    filepath, shotname, extension = file_path_split(file_path_pkl)
    file_path_csv = '%s/%s.%s' % (filepath, shotname, 'csv')
    logger.info('to csv file:%s' % file_path_csv)
    future_data = pd.read_pickle(file_path_pkl)
    all_df = pd.DataFrame()  # columns=['datetime', 'open', 'high', 'low', 'close', 'vol', 'code']
    for minor_xs in future_data.minor_axis:
        logger.info('symbol', minor_xs)
        with suppress(Exception):
            df = future_data.minor_xs(minor_xs)
            df['minor_xs'] = minor_xs
            df = df.reset_index()
            # df.rename(columns={'index': 'datetime', 'volume': 'vol'}, inplace=True)
            df = df.dropna()
            all_df = all_df.append(df)
    if rename_map:
        all_df.rename(columns=rename_map, inplace=True)
    all_df.to_csv(file_path_csv, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_path', type=str, help='pkl file path')
    parser.add_argument('-m', '--rename_map', type=dict, action="store", help='rename dataframe column ')

    # file_path_pkl = '/home/john/下载/dd_price_vp_20200809_20200818.pkl'
    # rename_map = {'index': 'datetime', 'volume': 'vol'}

    args = parser.parse_args()
    rename_map = eval(str(args.rename_map))
    pkl2csv(args.file_path, rename_map)
