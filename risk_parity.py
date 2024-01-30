import pandas as pd
import numpy as np
from scipy.optimize import minimize
import efinance as ef
import akshare as ak

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 可配置参数
ASSET_LIST = ['000082', '161119', '513500', '518880']
ASSET_NAMES = ['嘉实研究阿尔法', '易方达中债新综指', '标普500ETF', '黄金ETF']

# ASSET_LIST = ['159934', '159941', '510880']
# ASSET_NAMES = ['黄金ETF', '纳指ETF', '红利ETF']

# 获取数据并处理
def get_data(assets):
    data_frames = []
    for code in assets:
        data = ef.fund.get_quote_history(code)[['日期', '累计净值']]
        data.columns = ['日期', code]
        data.set_index('日期', inplace=True)
        data.sort_index(inplace=True)
        data_frames.append(data)
    df_merged = pd.concat(data_frames, axis=1, join='inner')
    df_merged.index = pd.to_datetime(df_merged.index)
    return df_merged

# 计算协方差矩阵
def calculate_cov_matrix(df):
    df = df / df.iloc[0] * 100
    returns_df = df.pct_change().dropna()
    one_cov_matrix = returns_df.cov() * 240
    return np.matrix(one_cov_matrix)

# 获取训练集
def get_train_set(change_time, df):
    df = df.loc[df.index < change_time]
    df = df.iloc[-240:] # 使用调仓日前240个交易日的数据
    return df 

# 计算风险贡献
def calculate_risk_contribution(weight, cov_matrix):
    weight = np.matrix(weight)
    portfolio_volatility = np.sqrt(weight * cov_matrix * weight.T)
    MRC = cov_matrix * weight.T / portfolio_volatility
    RC = np.multiply(MRC, weight.T)
    return RC

# 风险平价优化
def naive_risk_parity(weight, parameters):
    cov_matrix, target_rc_ratio = parameters
    portfolio_volatility = np.sqrt(weight * cov_matrix * np.matrix(weight).T)
    target_rc = np.asmatrix(np.multiply(portfolio_volatility, target_rc_ratio))
    actual_rc = calculate_risk_contribution(weight, cov_matrix)
    error = np.sum(np.square(actual_rc - target_rc.T))
    return error 

# 计算资产权重
def calculate_portfolio_weight(cov_matrix, objective):
    num_assets = len(ASSET_LIST)
    x0 = np.array([1.0 / num_assets] * num_assets)
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},)
    RC_target_ratio = np.array([1.0 / num_assets] * num_assets)
    options = {'ftol': 1e-20, 'maxiter': 2000}
    
    result = minimize(objective, x0, args=[cov_matrix, RC_target_ratio], method='SLSQP', 
                      bounds=bounds, constraints=constraints, options=options)
    return result.x


# 计算权重主函数
def get_weight_matrix(data, method='naive_risk_parity'):
    period_type = 'M'
    df_weight = pd.DataFrame(index=data.index, columns=ASSET_LIST)
    df_weight= data.resample(period_type).last()
    df_weight = df_weight[df_weight.index>='2013-12-31']

    for change_time in df_weight.index:
        train_set = get_train_set(change_time, data)
        if train_set.empty:
            continue  # Skip if there's no data in the training set
        cov_matrix = calculate_cov_matrix(train_set)
        if isinstance(cov_matrix, np.matrix) and cov_matrix.size > 0:
            weights = calculate_portfolio_weight(cov_matrix, naive_risk_parity)
            df_weight.loc[change_time] = weights
    return df_weight

# 使用示例
data = get_data(ASSET_LIST)
weights_matrix = get_weight_matrix(data)
print(weights_matrix)


def get_backtest_set(change_time,next_change_time,df):
    """返回回测样本数据"""
    #change_time: 调仓时间
    #next_change_time: 下一次调仓时间
    df = df.loc[(change_time<=df.index)&(df.index<next_change_time)]
    return df 

def get_backtest(df_weight, df, transaction_fee_ratio=0.0002):
    change_time_list = df_weight.index.to_list()
    df_b = df.loc[df.index >= change_time_list[0]]  # 截取回测区间内的数据
    df_b = df_b / df_b.iloc[0] * 100  # 统一缩放到100为基点
    backtest = pd.DataFrame(index=df_b.index, columns=df_b.columns)  # 创建一个空DataFrame，用于插入回测数据
    
    cash = 100  # 初始现金(基点)
    weights = df_weight.iloc[0]  # 初始权重

    for i in range(len(change_time_list) - 1):
        start = change_time_list[i]  # 起始调仓日期
        end = change_time_list[i + 1]  # 结束调仓日期
        period_data = df_b.loc[start:end]

        # 如果不是第一段时间，计算调仓时的资产价值
        if i > 0:
            values = period_data.iloc[0] * weights  # 各资产价值
            cash = values.sum()  # 重新计算总价值
            
        new_weights = df_weight.loc[start]  # 新权重
        target_values = cash * new_weights  # 目标资产价值
        trades = target_values - values if i > 0 else target_values

        # 减去手续费
        fees = np.abs(trades) * transaction_fee_ratio
        cash -= fees.sum()  # 更新现金
        
        # 根据实际交易后资金调整权重
        adjusted_values = target_values - fees
        weights = adjusted_values / cash
        
        # 计算回测期间的表现
        period_returns = period_data.multiply(weights, axis=1)
        backtest.loc[start:end] = period_returns
        
    return backtest

# 使用修改后的get_backtest函数运行回测

backtest = get_backtest(weights_matrix, data)  


def get_return_df(df):
    returns_df = (df-df.shift(1))/df.shift(1) # 简单收益率
    # returns_df = np.log(df/df.shift(1)) # 对数收益率
    returns_df.dropna(axis='index', inplace=True) # 删除空数据
    return returns_df

# 计算最大回撤
def max_draw_down(ret): 
    ret = np.array(ret)
    index_j = np.argmax(np.maximum.accumulate(ret) - ret)  # 结束位置
    index_i = np.argmax(ret[:index_j])  # 开始位置
    dd = ret[index_i] - ret[index_j]  # 最大回撤
    dd = dd/ret[index_i]
    return dd,index_i,index_j

def get_eval_indicator(ret):
    """各种评价指标"""
    eval_indicator = pd.Series(index=['累计收益率','年化收益率','年化波动率','最大回撤','sharpe比率','Calmar比率'])
    return_df = get_return_df(ret)
    #累计收益率
    eval_indicator['累计收益率'] = ret.iloc[-1]/ret.iloc[0] - 1
    #年华收益率  
    annual_ret = (ret.iloc[-1]/ret.iloc[0])**(240/ret.shape[0])-1
    eval_indicator['年化收益率'] = annual_ret
    #annual_ret = np.power(1+return_df.mean(), 250)-1 # 几何年化收益
    #年华波动率
    sigma = return_df.std() * (240**0.5)
    eval_indicator['年化波动率'] = sigma
    # 最大回撤
    dd, dd_index_start, dd_index_end = max_draw_down(ret)
    eval_indicator['最大回撤'] = dd
    #夏普比率  无风险利率是3%
    bench_annual_ret = 0.03
    sharpe = (annual_ret-bench_annual_ret)/sigma
    eval_indicator['sharpe比率'] = sharpe
    #Calmar比率=年化收益率/最大历史回撤
    calmar = annual_ret/dd
    eval_indicator['Calmar比率'] = calmar
    return eval_indicator

def get_eval_portfolio(backtest_res):
    """返回各个模型回测的评价结果"""
    eval_portfolio = pd.DataFrame(columns=backtest_res.columns)
    for name in eval_portfolio.columns:
        ret = backtest_res[name]
        eval_portfolio[name] = get_eval_indicator(ret)
    return eval_portfolio


r = {'RP': backtest.sum(axis=1)}
backtest_res = pd.DataFrame(r)
print(np.around(get_eval_portfolio(backtest_res)*100,2))