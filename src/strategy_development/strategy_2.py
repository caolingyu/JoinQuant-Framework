# 克隆自聚宽文章：https://www.joinquant.com/post/42675
# 标题：wywy1995 ETF策略最小方差组合轮动
# 作者：开心

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from src.backtesting_framework import *
from src.strategy_development import *
from src.data_processing import *


#初始化函数 
def initialize(context):
    # 设定基准
    # set_benchmark('000300.XSHG')
    set_bench_mark('159919')

    # 用真实价格交易
    # set_option('use_real_price', True)
    # 打开防未来函数
    # set_option("avoid_future_data", True)
    # 设置滑点 https://www.joinquant.com/view/community/detail/a31a822d1cfa7e83b1dda228d4562a70
    # set_slippage(FixedSlippage(0.002))
    # 设置交易成本
    # set_order_cost(OrderCost(open_tax=0, close_tax=0, open_commission=0.0002, close_commission=0.0002, close_today_commission=0, min_commission=5), type='fund')
    # 过滤一定级别的日志
    # log.set_level('system', 'error')
    # 参数

    # g.etf_pool = [
    #     '518880.XSHG', #黄金ETF（大宗商品）
    #     '513100.XSHG', #纳指100（海外资产）
    #     #'159915.XSHE', #创业板100（成长股，科技股，题材性，中小盘）
    #     '510880.XSHG', #红利ETF（价值股，蓝筹股，防御性，中大盘）
    # ]
    # 黄金ETF：159934

    g.etf_pool = ['159934', '513100', '159915', '510880']
    g.etf_dict = {
        '159934': "黄金ETF",
        '513100': "纳指100",
        '159915': "创业板100",
        '510880': "红利ETF"
    }
    # run_monthly(trade, 1, '10:00') #每天运行确保即时捕捉动量变化
    context.last_month = -1

# 计算投资组合方差的函数
def portfolio_variance(weights, cov_matrix):  # 定义投资组合方差函数
    return np.dot(weights.T, np.dot(cov_matrix* 250, weights))  # 计算并返回投资组合方差

# 优化投资组合的函数
def optimize_portfolio(returns):  # 定义优化投资组合函数
    # 计算协方差矩阵
    print(returns)
    cov_matrix = returns.cov()  # 计算收益的协方差矩阵
    # 投资组合中的资产数量
    num_assets = len(returns.columns)  # 计算投资组合中的资产数量
    # 初始权重（平均分配）
    init_weights = np.array([1/num_assets] * num_assets)  # 设置初始权重
    # 约束条件
    weight_sum_constraint = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}  # 权重和约束
    bounds = [(0, 1) for _ in range(num_assets)]  # 权重范围约束
    # 优化
    result = minimize(portfolio_variance, init_weights, args=(cov_matrix), bounds=bounds, constraints=weight_sum_constraint)  
    return result.x  # 返回优化结果

# 定义获取数据并调用优化函数的函数
def run_optimization(stocks, start_date, end_date):
    # prices = get_price(stocks, count=250, end_date=end_date, frequency='daily', fields=['close'])['close']
    prices = get_price(stocks, start_date=None, count=250, end_date=end_date, frequency='daily', fields=['close'])['close']

    returns = prices.pct_change().dropna() # 计算收益率
    weights = optimize_portfolio(returns)
    return weights
    
# 交易
def handle_data(context):
    # end_date = context.previous_date
    start_date = context.start_date
    end_date = context.end_date
    # # 按周为频率调仓
    # if context.dt.weekday() == 0:
    #     weights = run_optimization(g.etf_pool, start_date, end_date)
    #     print("weights", weights)
    #     if weights is None:
    #         return
    #     total_value = context.portfolio.total_value # 获取总资产
    #     index = 0
    #     for w in weights:
    #         value = total_value * w # 确定每个标的的权重
    #         print(value)
    #         order_target_value(g.etf_pool[index], value) # 调整标的至目标权重
    #         index+=1

    # 按月为频率调仓
    if context.dt.month != context.last_month:
        print(context.dt.month)
        context.last_month = context.dt.month
        
        weights = run_optimization(g.etf_pool, start_date, end_date)
        print("weights", weights)
        if weights is None:
            return
        total_value = context.portfolio.total_value # 获取总资产
        index = 0
        for w in weights:
            value = total_value * w # 确定每个标的的权重
            print(value)
            order_target_value(g.etf_pool[index], value) # 调整标的至目标权重
            index+=1


    
def handle_data_daily(context):
    # end_date = context.previous_date
    start_date = context.start_date
    end_date = context.dt
    print("start_date", start_date)
    print("end_date", end_date)
    weights = run_optimization(g.etf_pool, start_date, end_date)
    print("weights", weights)
    if weights is None:
        return
    # total_value = context.portfolio.total_value # 获取总资产
    index = 0
    operation = ""
    for w in weights:
        # value = total_value * w # 确定每个标的的权重
        # print(value)
        # order_target_value(g.etf_pool[index], value) # 调整标的至目标权重
        operation += f"{g.etf_dict[g.etf_pool[index]]}: {round(w, 2)} \n"
        index+=1
    return operation

