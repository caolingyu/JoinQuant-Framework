import numpy as np
import pandas as pd
from src.backtesting_framework import *
from src.strategy_development import *
from src.data_processing import *

# #初始化函数 
# def initialize(context):
#     # 设定基准
#     set_benchmark('000300.XSHG')
#     # 用真实价格交易
#     set_option('use_real_price', True)
#     # 打开防未来函数
#     set_option("avoid_future_data", True)
#     # 设置滑点 https://www.joinquant.com/view/community/detail/a31a822d1cfa7e83b1dda228d4562a70
#     set_slippage(FixedSlippage(0.000))
#     # 设置交易成本
#     set_order_cost(OrderCost(open_tax=0, close_tax=0, open_commission=0.0002, close_commission=0.0002, close_today_commission=0, min_commission=5), type='fund')
#     # 过滤一定级别的日志
#     log.set_level('system', 'error')
#     # 参数
#     g.etf_pool = [
#         '518880.XSHG', #黄金ETF（大宗商品）
#         '513100.XSHG', #纳指100（海外资产）
#         '159915.XSHE', #创业板100（成长股，科技股，中小盘）
#         '510180.XSHG', #上证180（价值股，蓝筹股，中大盘）
#     ]
#     g.m_days = 25 #动量参考天数
#     run_daily(trade, '9:30') #每天运行确保即时捕捉动量变化


# 初始化函数，设定基准等等
def initialize(context):
    # 设定002624作为基准
    set_bench_mark('159919')
    # 510180 上证180
    # 159919 沪深300
    # 159922 中证500
    # 159915 创业板
    # 513100 纳指
    # 159934 黄金ETF

    g.etf_pool = ['510180', '159915', '513100', '159934']

    g.ref_stock = '159919' #用ref_stock做择时计算的基础数据
    g.m_days = 25 #动量参考天数



def get_rank(etf_pool):
    score_list = []
    for etf in etf_pool:
        df = attribute_history(etf, g.m_days, ['close'])
        y = df['log'] = np.log(df.close)
        x = df['num'] = np.arange(df.log.size)
        slope, intercept = np.polyfit(x, y, 1)
        annualized_returns = math.pow(math.exp(slope), 250) - 1
        r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
        score = annualized_returns * r_squared
        score_list.append(score)
    df = pd.DataFrame(index=etf_pool, data={'score':score_list})
    df = df.sort_values(by='score', ascending=False)
    rank_list = list(df.index)    
    # print(df)
    # record(黄金 = round(df.loc['518880.XSHG'], 2))
    # record(纳指 = round(df.loc['513100.XSHG'], 2))
    # record(成长 = round(df.loc['159915.XSHE'], 2))
    # record(价值 = round(df.loc['510180.XSHG'], 2))
    return rank_list

# 交易
def handle_data(context):
    # 获取动量最高的一只ETF
    target_num = 1    
    target_list = get_rank(g.etf_pool)[:target_num]
    # 卖出    
    hold_list = list(context.portfolio.positions)
    for etf in hold_list:
        if etf not in target_list:
            order_target_value(etf, 0)
            print('卖出' + str(etf))
        else:
            print('继续持有' + str(etf))
    # 买入
    hold_list = list(context.portfolio.positions)
    if len(hold_list) < target_num:
        value = context.portfolio.available_cash / (target_num - len(hold_list))
        for etf in target_list:
            if context.portfolio.positions.get(etf, None) == None:
                context.portfolio.positions[etf] = Position(etf)
            if context.portfolio.positions[etf].total_amount == 0:
                order_target_value(etf, value)
                print('买入' + str(etf))

