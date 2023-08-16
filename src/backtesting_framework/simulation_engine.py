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
from src.backtesting_framework.context import *
from src.data_processing import *

# from src.strategy_development import *
# from src.data_processing import *



# 设置基准
def set_bench_mark(security):
    context.benchmark = security


def set_benchmark(security):
    context.benchmark = security


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
    print(security)
    try:
        hold_value = context.portfolio.positions.get(security).total_amount * today_data['open'].values[0]
    except:
        context.portfolio.positions[security] = Position(security=security)
        hold_value = hold_value = context.portfolio.positions.get(security).total_amount * today_data['open'].values[0]
    print('hold_value', hold_value)
    delta_value = value - hold_value
    print('delta_value', delta_value)

    order_value(security, delta_value)


import datetime

# def run_daily(func, time, reference_security='000001.XSHE'):
    
#     def wrapper(context):
#         now = context.current_dt.time()
#         if now >= datetime.time(hour=9,minute=15) and now <= datetime.time(hour=15,minute=0):
#             # 在交易时间内
#             if time == 'every_bar':
#                 # 每分钟运行
#                 func(context)
#             else:
#                 # 指定时间运行
#                 if now.strftime("%H:%M") == time:
#                     func(context)
#         else:
#             # 不在交易时间内
#             if time == 'every_bar':
#                 pass 
#             else:
#                 # 规定时间已过,调用函数
#                 func(context)
    
#     # 返回wrapper函数  
#     return wrapper


def run_daily(func, time, reference_security='159919'):
    config = {
        'func': func,
        'time': time,
        'reference_security': reference_security
    }
    context.run_daily_config.append(config)