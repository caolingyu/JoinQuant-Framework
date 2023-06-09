import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import dateutil
import numpy as np
import akshare as ak
import math


from src.backtesting_framework.context import *





def ak_daily(security, start_date, end_date, fields=('open', 'close', 'high', 'low', 'volume')):
    # print('security', security)
    # print('start_date', start_date)
    # print('end_date', end_date)

    # df = ak.stock_zh_a_daily(symbol=security, start_date=start_date, end_date=end_date, adjust="qfq")
    df = ak.fund_etf_hist_em(symbol=security, start_date=start_date, end_date=end_date, adjust='qfq').rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }
    )

    # 转换为日期格式
    df['date'] = pd.to_datetime(df['date'])
    # 设置'date'为索引
    df.set_index('date', inplace=True)
    return df[list(fields)]


# 获取历史数据
def attribute_history(security, count, fields=('open', 'close', 'high', 'low', 'volume')):
    end_date = (context.dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = trade_cal[(trade_cal['trade_date'] <= end_date)][-count:].iloc[0, :][
        'trade_date'].strftime('%Y-%m-%d')
    return attribute_daterange_history(security, start_date, end_date, fields)


# 获取历史数据基础函数
def attribute_daterange_history(security, start_date, end_date, fields=('open', 'close', 'high', 'low', 'volume')):
    # 尝试读取本地数据
    # 2022-10-18 转换为 20221018
    time_array1 = time.strptime(start_date, '%Y-%m-%d')
    start_date = time.strftime('%Y%m%d', time_array1)
    time_array2 = time.strptime(end_date, '%Y-%m-%d')
    end_date = time.strftime('%Y%m%d', time_array2)
    df = ak_daily(security, start_date, end_date)

    return df[list(fields)]


# 今天日线行情
def get_today_data(security, fields=('open', 'close', 'high', 'low', 'volume')):
    today = context.dt.strftime('%Y%m%d')
    # df = ak.stock_zh_a_daily(symbol=security, start_date=today, end_date=today, adjust="qfq")
    df = ak.fund_etf_hist_em(symbol=security, start_date=today, end_date=today, adjust='qfq').rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }
    )
    # print('today_df', df.head())
    # 转换为日期格式
    df['date'] = pd.to_datetime(df['date'])
    # 设置'date'为索引
    df.set_index('date', inplace=True)
    return df[list(fields)]


# def get_realtime_quotes():
#     data = ak.stock_zh_a_spot_em()
#     return data
