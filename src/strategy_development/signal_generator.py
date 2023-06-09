


def get_real_time_signal():

    signal_dict = {}
    for stock in g.stock_pool:
        today_data = ak.stock_zh_a_daily(stock, start_date=now.strftime("%Y%m%d"), end_date=now.strftime("%Y%m%d"))
        # 停牌
        if len(today_data) == 0:
            continue

        p = today_data['open'].values[0]
        # 计算下一步信号
        next_signal = generate_signal(stock, p)
        if next_signal != 'hold':
            signal_dict[stock] = next_signal

    print(f"{dt.strftime('%Y-%m-%d')} 14:55, 下一步信号为 {signal_dict}")
    return signal_dict


# # 获取当前日期时间
# now = datetime.datetime.now()
# dt = now.date()

# # 如果是每个交易日14:55，则计算最新价格并根据策略规则生成下一步信号
# if dt.weekday() < 5 and datetime.time(14, 55) == now.time():
#     pass


