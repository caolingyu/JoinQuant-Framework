import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import akshare as ak

from src.backtesting_framework import *
from src.strategy_development import *
from src.data_processing import *

# 定义手续费和滑点
config = {
    'commission_rate': 2.5 / 10000,  # 手续费
    'slippage': 0.01  # 滑点
}

# 初始化函数，设定基准等等
def initialize(context):
    # 设定002624作为基准
    set_bench_mark('159919')
    g.stock_pool = ['159919', '510500', '159915', '513100']
    g.stock_num = 1 #买入评分最高的前stock_num只股票
    g.momentum_day = 29 #最新动量参考最近momentum_day的

    #rsrs择时参数
    g.ref_stock = '159919' #用ref_stock做择时计算的基础数据
    g.N = 18 # 计算最新斜率slope，拟合度r2参考最近N天
    g.M = 600 # 计算最新标准分zscore，rsrs_score参考最近M天
    g.score_threshold = 0.7 # rsrs标准分指标阈值
    #ma择时参数
    g.mean_day = 20 #计算结束ma收盘价，参考最近mean_day
    g.mean_diff_day = 3 #计算初始ma收盘价，参考(mean_day + mean_diff_day)天前，窗口为mean_diff_day的一段时间
    g.slope_series = initial_slope_series()[:-1] # 除去回测第一天的slope，避免运行时重复加入


# 框架主体函数
def run():
    init_value = context.portfolio.available_cash
    initialize(context)

    today = datetime.date.today()
    dt = today.strftime('%Y-%m-%d')
    dt = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
    print(type(dt))
    context.dt = dt

    handle_data(context)




run()

