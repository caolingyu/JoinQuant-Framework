import akshare as ak
etf_real_time_df = ak.fund_etf_spot_em()
# print(etf_real_time_df)
etf_code_list = etf_real_time_df['代码'].to_list()
etf_name_list = etf_real_time_df['名称'].to_list()

etf_dict = dict(zip(etf_name_list, etf_code_list))
# print(etf_dict)

print("沪深300ETF", etf_dict.get('沪深300ETF'))
print("上证50ETF", etf_dict.get('上证50ETF'))
print("创业板ETF", etf_dict.get('创业板ETF'))
print("中证消费ETF", etf_dict.get('中证消费ETF'))

