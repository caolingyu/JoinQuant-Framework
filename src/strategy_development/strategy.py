# 策略部分
import numpy as np
from src.backtesting_framework import *
from src.strategy_development import *
from src.data_processing import *



# 初始化函数，设定基准等等
def initialize(context):
    # 设定002624作为基准
    set_bench_mark('159919')
    # 510180 上证180
    # 159919 沪深300
    # 159922 中证500
    # 159915 创业板
    # 513100 纳指
    g.stock_pool = ['510180', '159915', '513100', '159922']
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


#2-1 择时模块-计算线性回归统计值
#对输入的自变量每日最低价x(series)和因变量每日最高价y(series)建立OLS回归模型,返回元组(截距,斜率,拟合度)
def get_ols(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    r2 = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
    return (intercept, slope, r2)


#2-2 择时模块-设定初始斜率序列
#通过前M日最高最低价的线性回归计算初始的斜率,返回斜率的列表
def initial_slope_series():
    data = attribute_history(g.ref_stock, g.N + g.M, ['high', 'low'])
    return [get_ols(data.low[i:i+g.N], data.high[i:i+g.N])[1] for i in range(g.M)]


#2-3 择时模块-计算标准分
#通过斜率列表计算并返回截至回测结束日的最新标准分
def get_zscore(slope_series):
    mean = np.mean(slope_series)
    std = np.std(slope_series)
    return (slope_series[-1] - mean) / std

#1-1 选股模块-动量因子轮动 
#基于股票年化收益和判定系数打分,并按照分数从大到小排名
def get_rank():
    score_list = []
    for stock in g.stock_pool:
        data = attribute_history(stock, g.momentum_day, ['close'])
        y = data['log'] = np.log(data.close)
        x = data['num'] = np.arange(data.log.size)
        slope, intercept = np.polyfit(x, y, 1)
        annualized_returns = math.pow(math.exp(slope), 250) - 1
        r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
        score = annualized_returns * r_squared
        score_list.append(score)
    stock_dict=dict(zip(g.stock_pool, score_list))
    sort_list=sorted(stock_dict.items(), key=lambda item:item[1], reverse=True) #True为降序
    code_list=[]
    for i in range((len(g.stock_pool))):
        code_list.append(sort_list[i][0])
    rank_stock = code_list[0:g.stock_num]
    return rank_stock


#2-4 择时模块-计算综合信号
#1.获得rsrs与MA信号,rsrs信号算法参考优化说明，MA信号为一段时间两个端点的MA数值比较大小
#2.信号同时为True时返回买入信号，同为False时返回卖出信号，其余情况返回持仓不变信号
def get_timing_signal(stock):
    #计算MA信号
    close_data = attribute_history(g.ref_stock, g.mean_day + g.mean_diff_day, ['close'])
    today_MA = close_data.close[g.mean_diff_day:].mean() 
    before_MA = close_data.close[:-g.mean_diff_day].mean()
    #计算rsrs信号
    high_low_data = attribute_history(g.ref_stock, g.N, ['high', 'low'])
    intercept, slope, r2 = get_ols(high_low_data.low, high_low_data.high)
    g.slope_series.append(slope)
    rsrs_score = get_zscore(g.slope_series[-g.M:]) * r2
    #综合判断所有信号
    if rsrs_score > g.score_threshold and today_MA > before_MA:
        print('BUY')
        return "BUY"
    elif rsrs_score < -g.score_threshold and today_MA < before_MA:
        print('SELL')
        return "SELL"
    else:
        print('KEEP')
        return "KEEP"



#4-1 交易模块-自定义下单
#报单成功返回报单(不代表一定会成交),否则返回None,应用于
def order_target_value_(security, value):
	if value == 0:
		print("Selling out %s" % (security))
	else:
		print("Order %s to value %f" % (security, value))
	# 如果股票停牌，创建报单会失败，order_target_value 返回None
	# 如果股票涨跌停，创建报单会成功，order_target_value 返回Order，但是报单会取消
	# 部成部撤的报单，聚宽状态是已撤，此时成交量>0，可通过成交量判断是否有成交
	return order_target_value(security, value)

#4-2 交易模块-开仓
#买入指定价值的证券,报单成功并成交(包括全部成交或部分成交,此时成交量大于0)返回True,报单失败或者报单成功但被取消(此时成交量等于0),返回False
def open_position(security, value):
	order = order_target_value_(security, value)
	if order != None and order.filled > 0:
		return True
	return False

#4-3 交易模块-平仓
#卖出指定持仓,报单成功并全部成交返回True，报单失败或者报单成功但被取消(此时成交量等于0),或者报单非全部成交,返回False
def close_position(position):
	security = position.security
	print('closing position')
	order = order_target_value_(security, 0)  # 可能会因停牌失败
	if order != None:
		if order.status == OrderStatus.held and order.filled == order.amount:
			return True
	return False

#4-4 交易模块-调仓
#当择时信号为买入时开始调仓，输入过滤模块处理后的股票列表，执行交易模块中的开平仓操作
def adjust_position(context, buy_stocks):
	for stock in context.portfolio.positions:
		print('stock', stock)
		print('buy_stocks', buy_stocks)
		if stock not in buy_stocks:
			print("[%s]已不在应买入列表中" % (stock))
			position = context.portfolio.positions[stock]
			close_position(position)
		else:
			print("[%s]已经持有无需重复买入" % (stock))
	# 根据股票数量分仓
	# 此处只根据可用金额平均分配购买，不能保证每个仓位平均分配
	# position_count = len(context.portfolio.positions)
	position_count = 0
	for k, v in context.portfolio.positions.items():
		if v.total_amount >0:
			position_count += 1

	print('position_count', position_count)
	if g.stock_num > position_count:
		value = context.portfolio.available_cash / (g.stock_num - position_count)
		
		for stock in buy_stocks:
			if context.portfolio.positions.get(stock, None) == None:
				context.portfolio.positions[stock] = Position(stock)
			print(context.portfolio.positions)
			if context.portfolio.positions[stock].total_amount == 0:
				print('enter open_position', value)
				if open_position(stock, value):
					if len(context.portfolio.positions) == g.stock_num:
						break

def handle_data(context):
    check_out_list = get_rank()
    print('今日自选股:{}'.format(check_out_list))
    #获取综合择时信号
    timing_signal = get_timing_signal(g.ref_stock)
    print('今日择时信号:{}'.format(timing_signal))
    #开始交易
    if timing_signal == 'SELL':
        for stock in context.portfolio.positions:
            position = context.portfolio.positions[stock]
            close_position(position)
    elif timing_signal == 'BUY' or timing_signal == 'KEEP':
        adjust_position(context, check_out_list)
    else:
        pass