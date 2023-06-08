import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import dateutil
import numpy as np
import akshare as ak
import math

from backtesting_framework import *
from strategy_development import *


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


# 实例化上下文数据Context
context = Context(cash=100000, start_date='2023-01-01', end_date='2023-06-01')


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



# 设置基准
def set_bench_mark(security):
    context.benchmark = security


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


# 买卖订单基础函数
def _order(today_data, security, amount):
    # 股票价格
    p = today_data['open'].values[0]
    # 停牌
    if len(today_data) == 0:
        print("今日停牌")
        return
    # 现金不足
    if context.portfolio.available_cash - amount * p < 0:
        amount = int(context.portfolio.available_cash / p / 100) * 100
        print("现金不足,已调整为%d" % amount)
    # 100的倍数
    if amount % 100 != 0:
        if amount != -context.portfolio.positions.get(security).total_amount:
            amount = int(amount / 100) * 100
            print("不是100的倍数,已调整为%d" % amount)
    # 卖出数量超过持仓数量
    if context.portfolio.positions.get(security).total_amount < -amount:
        amount = -context.portfolio.positions.get(security).total_amount
        print("卖出数量不能超过持仓数量,已调整为%d" % amount)
    # 将买卖股票数量存入持仓标的信息
    context.portfolio.positions.get(security).total_amount = context.portfolio.positions.get(security).total_amount + amount
    print('剩余持仓', context.portfolio.positions.get(security).total_amount)
    # 剩余资金
    context.portfolio.available_cash -= amount * p
    print('剩余资金', context.portfolio.available_cash)

    # 如果一只股票持仓为0，则删除上下文数据持仓标的信息中该股信息
    if context.portfolio.positions.get(security).total_amount == 0:
        context.portfolio.positions.get(security).total_amount = 0


# 按股数下单
def order(security, amount):
    today_data = get_today_data(security)
    _order(today_data, security, amount)


# 目标股数下单
def order_target(security, amount):
    if amount < 0:
        print("数量不能为负，已调整为0")
        amount = 0
    today_data = get_today_data(security)
    hold_amount = context.positions.get(security, 0)
    delta_amount = amount - hold_amount
    _order(today_data, security, delta_amount)


# 按价值下单
def order_value(security, value):
    today_data = get_today_data(security)
    amount = int(value / today_data['open'].values[0])
    _order(today_data, security, amount)


# 目标价值下单
def order_target_value(security, value):
    if value < 0:
        print("价值不能为负，已调整为0")
        value = 0
    today_data = get_today_data(security)
    hold_value = context.portfolio.positions.get(security).total_amount * today_data['open'].values[0]
    print('hold_value', hold_value)
    delta_value = value - hold_value
    print('delta_value', delta_value)

    order_value(security, delta_value)

