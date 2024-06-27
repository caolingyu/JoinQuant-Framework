from importlib import reload

import notebooks.dynamic_balance_strategy.backtest_0207 as backtest_0207


# ASSET_LIST = ['159934', '159941', '000614', '001911', '002088', '001651']
ASSET_LIST = ['518880', '159941', '001286']
# 001443
# ASSET_LIST = ['159934', '159941', '001314']
# ASSET_LIST = ['000082', '161119', '513500', '518880']
# ASSET_LIST = ['510880', '159941', '518880']
      

# for code in ASSET_LIST:
#     print(all_funds_info_df[all_funds_info_df['基金代码']==code][['基金代码', '基金简称', '成立日期']])


pb = backtest_0207.PortfolioBacktester(ASSET_LIST)
backtest_res_overall, backtest_res = pb.get_backtest_result()
print(backtest_res_overall)
print(pb.get_weight_matrix(pb.data, method='pca', half=True))


