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
import akshare
import pandas as pd

def get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, fill_na=True):
    """
    获取一支或者多只股票的行情数据，按天或者按分钟。
    :param security: 一支股票代码或者一个股票代码的list
    :param start_date: 字符串或者 datetime.datetime/datetime.date 对象, 开始时间
    :param end_date: 格式同上, 结束时间，默认是今天
    :param frequency: 单位时间长度, 几天或者几分钟, 现在支持'd'（等同于'daily'）,'min'(等同于'minute')
    :param fields: 字符串list, 选择要获取的行情数据字段
    :param fill_na: 是否对缺失值进行填充，默认为True；True表示用pre_close价格填充；False 表示使用NAN填充。
    :return: pd.DataFrame 或 pd.MultiIndex DataFrame，包含所选股票的行情数据
    """
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')
    
    if isinstance(security, str):
        panel = False
        security = [security]
    elif isinstance(security, list):
        panel = True
    else:
        raise ValueError('Invalid security type, should be str or list.')
    
    df_list = []
    for code in security:
        try:
            if frequency == 'daily' or frequency == 'd':
                df = ak.fund_etf_hist_em(symbol=code, start_date=start_date, end_date=end_date, adjust='qfq').rename(
                    columns={
                        "日期": "date",
                        "开盘": "open",
                        "收盘": "close",
                        "最高": "high",
                        "最低": "low",
                        "成交量": "volume",
                    }
                )
                print(df)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.sort_index(inplace=True)
            elif frequency == 'minute' or frequency == 'min':
                df = akshare.stock_zh_a_minute(symbol=code, period='1', adjust='qfq', start_date=start_date, end_date=end_date)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
                df.sort_index(inplace=True)
            else:
                raise ValueError('Invalid frequency value, should be one of "d", "daily", "min", "minute".')
            
            if fields is not None:
                df = df[fields]
            
            if fill_na:
                last_close = pd.Series(df['close'].iloc[0], index=df.index[df.index < df.index[0]])
                df['close'].fillna(last_close, inplace=True)
                df.fillna(method='ffill', inplace=True)
            
            df_list.append(df)
        except Exception as e:
            print(f"Error fetching data for {code}: {str(e)}")

    if panel:
        result = pd.concat(df_list, axis=1, keys=security)
    else:
        result = df_list[0]
        result.columns = [security[0] + '_' + col for col in result.columns]
    
    return result
