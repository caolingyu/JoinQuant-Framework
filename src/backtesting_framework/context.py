import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import dateutil
import numpy as np
import akshare as ak
import math

from src.backtesting_framework.portfolio_management import *


# 获取各大交易所交易日历数据
def ak_trade_cal():
    df = ak.tool_trade_date_hist_sina()
    # print(df)
    # 转换为日期格式
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    # 设置'trade_date'为索引
    # df.set_index('trade_date', inplace=True)
    # 存储为csv文件
    # df.to_csv('./trade_cal.csv')
    return df

# 下载并保存交易日历数据
trade_cal = ak_trade_cal()


# 全局变量用
class G:
    pass


# 全局变量用
g = G()


# 上下文数据
class Context:
    def __init__(self, cash, start_date, end_date):
        # 资金
        self.cash = cash
        # 开始时间
        self.start_date = start_date
        # 结束时间
        self.end_date = end_date
        # 持仓标的信息
        self.positions = {}
        # 基准
        self.benchmark = None
        # 交易日期
        self.date_range = trade_cal[(trade_cal['trade_date'] >= start_date) &
                                    (trade_cal['trade_date'] <= end_date)]['trade_date'].values
        # 回测今天日期
        self.dt = dateutil.parser.parse(start_date)
        # self.portfolio = Portfolio()
        self.portfolio = Portfolio(0.0, 10000.0, 10000.0, 0.0, {}, 0.0, 10000.0, 0.0)






# 实例化上下文数据Context
context = Context(cash=100000, start_date='2022-03-01', end_date='2023-06-01')

