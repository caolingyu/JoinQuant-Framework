#!/bin/bash

# 创建目录
mkdir -p data_processing
mkdir -p strategy_development
mkdir -p backtesting_framework
mkdir -p live_trading
mkdir -p visualization_reporting
mkdir -p utils

# 创建文件
touch data_processing/data_fetcher.py
touch data_processing/data_cleaner.py
touch data_processing/data_transformer.py

touch strategy_development/strategy.py
touch strategy_development/signal_generator.py

touch backtesting_framework/portfolio_management.py
touch backtesting_framework/simulation_engine.py
touch backtesting_framework/performance_evaluation.py

touch live_trading/trading_interface.py
touch live_trading/data_subscription.py
touch live_trading/trade_executor.py

touch visualization_reporting/result_visualizer.py
touch visualization_reporting/report_generator.py

touch utils/time_utils.py
touch utils/statistical_analysis.py
touch utils/data_storage.py

touch main.py

echo "目录和文件创建完成。"
