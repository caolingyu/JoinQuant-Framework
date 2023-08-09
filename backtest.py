import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import akshare as ak

from src.backtesting_framework import *
# from src.strategy_development.strategy_4 import *
from config import STRATEGY_CONFIG
from src.data_processing import *

# 定义手续费和滑点
config = {
    'commission_rate': 2 / 10000,  # 手续费
    'slippage': 0.002  # 滑点
}

def load_strategy(strategy_name):
    module_path = STRATEGY_CONFIG.get(strategy_name)
    if module_path:
        strategy_module = __import__(module_path, fromlist=["*"])
        return strategy_module  # 返回整个策略模块
    else:
        raise ValueError("Invalid strategy name")


# 框架主体函数
def run(strategy):
    # 创建收益数据表
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range), columns=['value'])
    # 初始资金
    init_value = context.portfolio.available_cash
    strategy.initialize(context)
    last_price = {}
    high_watermark = [init_value]

    
    # 模拟每个bar运行
    for dt in context.date_range:
        dt = np.datetime_as_string(dt).split('T')[0]  # 提取日期部分
        dt = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
        context.dt = dt

        # handle_data(context)
        print(dt)
        try:
            strategy.handle_data(context)
        except Exception as e:
            print(f"skip {dt}")
            continue

        # 计算手续费和滑点
        commission = 0
        slippage = 0
        for stock, position in context.portfolio.positions.items():
            try:
                today_data = get_today_data(stock)
            except:
                today_data = []
            # 停牌
            if len(today_data) == 0:
                # 停牌前一交易日股票价格
                p = last_price[stock]
            else:
                p = today_data['open'].values[0]
                # 存储为停牌前一交易日股票价格
                last_price[stock] = p
                # 计算手续费和滑点
                commission += p * position.total_amount * config['commission_rate']
                slippage += p * position.total_amount * config['slippage']

        value = context.portfolio.available_cash
        # 计算持仓价值
        for stock, position in context.portfolio.positions.items():
            try:
                today_data = get_today_data(stock)
            except:
                today_data = []
            # 停牌
            if len(today_data) == 0:
                # 停牌前一交易日股票价格
                p = last_price[stock]
            else:
                p = today_data['open'].values[0]
                # 存储为停牌前一交易日股票价格
                last_price[stock] = p
            value += p * context.portfolio.positions[stock].total_amount

        # 扣除手续费和滑点
        value -= commission + slippage
        plt_df.loc[dt, 'value'] = value

    # 计算收益率
    # 收益率 = (总价值 - 初始资金 - 手续费 - 滑点) / 初始资金
    plt_df['ratio'] = (plt_df['value'] - init_value - commission - slippage) / init_value

    ## 计算基准收益率
    bm_df = attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['open'][0]
    plt_df['benckmark_ratio'] = (bm_df['open'] - bm_init) / bm_init

    # 计算每日收益率
    daily_returns = plt_df['ratio'].diff()
    # 去除第一天的NaN值
    daily_returns = daily_returns[1:]
    cumulative_returns = (1 + daily_returns).cumprod()
    # 计算最大回撤
    max_drawdown = (cumulative_returns.cummax() - cumulative_returns).max()

    # 年化收益率
    annual_return = pow((plt_df['value'][-1] / init_value), 252 / len(context.date_range)) - 1
    # 年化波动率
    annual_volatility = daily_returns.std() * np.sqrt(252)


    # 输出回测结果
    print('回测结果')
    print('-' * 60)
    print(f'初始资金: {init_value:.2f}元')
    print(f'总价值: {plt_df["value"][-1]:.2f}元')
    print(f'收益率: {plt_df["ratio"][-1] * 100:.2f}%')
    print(f'年化收益率: {annual_return * 100:.2f}%')
    print(f'年化波动率: {annual_volatility * 100:.2f}%')
    print(f'最大回撤: {max_drawdown * 100:.2f}%')

    # 绘制收益率曲线
    plt.plot(plt_df['ratio'], label="ratio")
    # 绘制基准收益率曲线
    plt.plot(plt_df['benckmark_ratio'], label="benchmark_ratio")
    # 添加图例
    plt.legend()
    # 添加标题和轴标签
    plt.title('Backtesting Result')
    plt.xlabel('Date')
    plt.ylabel('Return')

    now_time = time.strftime("%Y%m%d%H%M%S")
    plt.savefig(f"img/{now_time}.png")

    # 显示图形
    plt.show()


if __name__ == "__main__":
    selected_strategy = "strategy_1"  # 根据需要选择不同的策略名称
    strategy = load_strategy(selected_strategy)
    run(strategy)

