import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import dateutil
import numpy as np
import akshare as ak
import math

from src.backtesting_framework import *
from src.strategy_development import *

from typing import Dict, List
import datetime





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
    # 创建收益数据表
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range), columns=['value'])
    # 初始资金
    init_value = context.portfolio.available_cash
    initialize(context)
    last_price = {}
    
    # 模拟每个bar运行
    for dt in context.date_range:

        dt = np.datetime_as_string(dt).split('T')[0]  # 提取日期部分
        dt = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
        context.dt = dt

        handle_data(context)
        
        value = context.portfolio.available_cash

        # 遍历每支股票计算股票价值
        for stock, position in context.portfolio.positions.items():
            today_data = get_today_data(stock)
            # 停牌
            if len(today_data) == 0:
                # 停牌前一交易日股票价格
                p = last_price[stock]
            else:
                p = today_data['open'].values[0]
                # 存储为停牌前一交易日股票价格
                last_price[stock] = p
            value += p * context.portfolio.positions[stock].total_amount
        plt_df.loc[dt, 'value'] = value

    print(plt_df)
    # fname 为你的字体库路径和字体名
    # 图形中文显示， Matplotlib 默认情况不支持中文
    # zhfont1 = matplotlib.font_manager.FontProperties(fname="SourceHanSansSC-Bold.otf")

    # 设置中文字体
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False

    # 收益率
    plt_df['ratio'] = (plt_df['value'] - init_value) / init_value
    bm_df = attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['open'][0]
    # 基准收益率
    plt_df['benckmark_ratio'] = (bm_df['open'] - bm_init) / bm_init
    plt.title("Performance Report")
    # 绘制收益率曲线
    plt.plot(plt_df['ratio'], label="ratio")
    # 绘制基准收益率曲线
    plt.plot(plt_df['benckmark_ratio'], label="benckmark_ratio")
    # fontproperties 设置中文显示用字体，fontsize 设置字体大小
    plt.xlabel("Date")
    plt.ylabel("Yield")
    # x坐标斜率
    plt.xticks(rotation=46)
    # 添加图注
    plt.legend()
    # 保存图片
    now_time = time.strftime("%Y%m%d%H%M%S")
    plt.savefig(f"img/{now_time}.png")
    # 显示
    plt.show()


run()