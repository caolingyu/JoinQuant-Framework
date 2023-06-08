from typing import Dict, List
import datetime

class Position:
    def __init__(self, 
                 security: str, 
                 price: float=0, 
                 acc_avg_cost: float=0, 
                 avg_cost: float=0, 
                 hold_cost: float=0, 
                 init_time: datetime.datetime=datetime.datetime.now(), 
                 transact_time: datetime.datetime=datetime.datetime.now(), 
                 locked_amount: float=0, 
                 total_amount: float=0, 
                 closeable_amount: float=0, 
                 today_amount: float=0, 
                 value: float=0, 
                 side: str='long'):
        self.security = security
        self.price = price
        self.acc_avg_cost = acc_avg_cost
        self.avg_cost = avg_cost
        self.hold_cost = hold_cost
        self.init_time = init_time
        self.transact_time = transact_time
        self.locked_amount = locked_amount
        self.total_amount = total_amount
        self.closeable_amount = closeable_amount
        self.today_amount = today_amount
        self.value = value
        self.side = side

class Portfolio:
    def __init__(self, 
                 inout_cash: float, 
                 available_cash: float, 
                 transferable_cash: float, 
                 locked_cash: float,
                 positions: Dict[str, Position], 
                 returns: float, 
                 starting_cash: float, 
                 positions_value: float):
        self.inout_cash = inout_cash
        self.available_cash = available_cash
        self.transferable_cash = transferable_cash
        self.locked_cash = locked_cash
        self.positions = positions
        self.long_positions = {k:v for k,v in positions.items() if v.side == 'long'}
        self.short_positions = {k:v for k,v in positions.items() if v.side == 'short'}
        self.returns = returns
        self.starting_cash = starting_cash
        self.positions_value = positions_value
        self.total_value = starting_cash + inout_cash + positions_value
        
    def position(self, security: str) -> Position:
        return self.positions[security]



# 测试用
# # 创建一个空的Portfolio对象
# portfolio = Portfolio(0.0, 10000.0, 10000.0, 0.0, {}, 0.0, 10000.0, 0.0)

# # 添加一个持仓
# position = Position('AAPL', 120.0, 119.5, 121.0, 122.0, datetime.datetime.now(), datetime.datetime.now(), 
#                      0.0, 100.0, 100.0, 0.0, 12000.0, 'long')
# portfolio.positions['AAPL'] = position

# # 访问属性和方法
# print("累计出入金:{0}".format(portfolio.inout_cash))
# print("可用资金:{0}".format(portfolio.available_cash))
# print("可取资金:{0}".format(portfolio.transferable_cash))
# print("挂单锁住资金:{0}".format(portfolio.locked_cash))

# print("多单的仓位:{0}".format(portfolio.long_positions)) 
# print("空单的仓位:{0}".format(portfolio.short_positions))
# print("总权益:{0}".format(portfolio.total_value))

# print(type(portfolio.long_positions))
# long_positions_dict = portfolio.long_positions
# for position in list(long_positions_dict.values()):  
#     print("标的:{0},总仓位:{1},标的价值:{2}, 建仓时间:{3}".format(position.security, position.total_amount, 
#                                                            position.value, position.init_time))
