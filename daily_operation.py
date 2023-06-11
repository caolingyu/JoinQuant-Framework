import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import akshare as ak
import requests

from dotenv import load_dotenv

from src.backtesting_framework import *
from src.strategy_development import *
from src.data_processing import *

# Load environment variables from .env file
load_dotenv()

# Define commission rate and slippage
config = {
    'commission_rate': 2.5 / 10000,  # Commission rate
    'slippage': 0.01  # Slippage
}

# Initialize function, set benchmark, etc.
def initialize(context):
    # Set '159919' as the benchmark
    set_bench_mark('159919')
    g.stock_pool = ['159919', '510500', '159915', '513100']
    g.stock_num = 1  # Buy the top stock_num stocks based on the score
    g.momentum_day = 29  # Latest momentum reference for the last momentum_day days

    # rsrs timing parameters
    g.ref_stock = '159919'  # Basic data for rsrs timing calculation using ref_stock
    g.N = 18  # Calculate the latest slope and R-squared based on the last N days
    g.M = 600  # Calculate the latest z-score based on the last M days
    g.score_threshold = 0.7  # rsrs z-score threshold
    # ma timing parameters
    g.mean_day = 20  # Calculate the closing price based on the last mean_day
    g.mean_diff_day = 3  # Calculate the initial closing price based on (mean_day + mean_diff_day) days ago with a window of mean_diff_day
    g.slope_series = initial_slope_series()[:-1]  # Exclude the slope for the first day of backtesting to avoid duplicate addition during runtime

# Function to send a Bark notification
def send_bark_notification(title, content):
    bark_url = f"https://api.day.app/{os.getenv('BARK_API_KEY')}"  # Replace YOUR_BARK_KEY with your actual Bark API key
    params = {
        'title': title,
        'body': content
    }
    response = requests.get(bark_url, params=params)
    # You can add error handling for the response if needed

def handle_data(context):
    check_out_list = get_rank()
    today_stock = '今日自选股:{}'.format(check_out_list)
    #获取综合择时信号
    timing_signal = get_timing_signal(g.ref_stock)
    today_signal = '今日择时信号:{}'.format(timing_signal)
    return f"{today_stock} {timing_signal}"

# Main framework function
def run():
    init_value = context.portfolio.available_cash
    initialize(context)

    today = datetime.date.today()
    dt = today.strftime('%Y-%m-%d')
    dt = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
    context.dt = dt

    reminder_content = handle_data(context)

    # Example daily operation reminder
    # if dt.weekday() < 5:  # Only execute on weekdays (Monday to Friday)
    reminder_title = '今日策略操作'
    send_bark_notification(reminder_title, reminder_content)

run()
