import akshare as ak

etf_real_time_df = ak.stock_zh_a_spot_em()
etf_code_list = etf_real_time_df['代码'].tolist()
etf_name_list = etf_real_time_df['名称'].tolist()

ema30_bullish_etfs = []

for code, name in zip(etf_code_list, etf_name_list):
    df = ak.stock_zh_a_hist(symbol=code, adjust='qfq').rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }
    )
    if len(df) > 0:
        # 计算EMA30、EMA60和EMA120均线
        df['EMA30'] = df['close'].ewm(span=30, adjust=False).mean()
        df['EMA60'] = df['close'].ewm(span=60, adjust=False).mean()
        df['EMA120'] = df['close'].ewm(span=120, adjust=False).mean()

        # 计算MACD指标
        df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']

        # 判断均线是否满足条件
        if (
            df['EMA30'].iloc[-1] > df['EMA60'].iloc[-1]
            and df['EMA60'].iloc[-1] > df['EMA120'].iloc[-1]
        ):
            # 寻找本轮下跌的起点
            current_histogram = df['MACD_histogram'].iloc[-1]
            start_index = df[df['MACD_histogram'] > 0].last_valid_index() + 1

            # 判断是否为第三次下跌趋势的减弱
            if start_index is not None:
                histogram_values = df['MACD_histogram'].iloc[start_index:]
                cnt = 0
                last_valid = True
                for value in histogram_values.diff():
                    if value > 0 and last_valid:
                        cnt += 1
                        last_valid = False
                    elif value > 0:
                        continue
                    elif value < 0 and not last_valid:
                        last_valid = True
                    else:
                        continue
                # if (
                #     len(histogram_values) >= 4
                #     and (histogram_values.diff() > 0).iloc[1:].sum() >= 2
                # ):
                if cnt >= 3:
                    ema30_bullish_etfs.append(name)
                
# print(ema30_bullish_etfs)

etf_real_time_df = ak.stock_zh_a_spot_em()
etf_code_list = etf_real_time_df['代码'].tolist()
etf_name_list = etf_real_time_df['名称'].tolist()

etf_dict = dict(zip(etf_name_list, etf_code_list))
# print(etf_dict)

for item in ema30_bullish_etfs:
    print(item, etf_dict.get(item))
