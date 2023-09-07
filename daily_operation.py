import os
import codecs
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import akshare as ak
import requests
import redis

from dotenv import load_dotenv

from src.backtesting_framework import *
# from src.strategy_development import *
from src.strategy_development.strategy_2 import *

from src.data_processing import *


import logging

# 创建日志器
logger = logging.getLogger(__name__)

# 设置日志级别
logger.setLevel(logging.DEBUG) 

# 创建日志处理器并设置级别
file_handler = logging.FileHandler('daily_operation.log')
file_handler.setLevel(logging.DEBUG)

# 创建日志格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter) 

# 将处理器添加到日志器
logger.addHandler(file_handler)


# Load environment variables from .env file
load_dotenv()

# Define commission rate and slippage
config = {
    'commission_rate': 2.5 / 10000,  # Commission rate
    'slippage': 0.01  # Slippage
}

# Function to send a Bark notification
def send_bark_notification(title, content):
    bark_url = f"https://api.day.app/{os.getenv('BARK_API_KEY')}"  # Replace YOUR_BARK_KEY with your actual Bark API key
    params = {
        'title': title,
        'body': content
    }
    response = requests.get(bark_url, params=params)
    # You can add error handling for the response if needed

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Publish message to Redis channel
    r.publish('my-channel', f'{title}: {content}')

def run():
    init_value = context.portfolio.available_cash
    initialize(context)

    today = datetime.date.today()
    dt = today.strftime('%Y-%m-%d')
    dt = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
    context.dt = str(dt)

    reminder_content = handle_data_daily(context)

    reminder_title = '今日策略操作'
    logger.info(f"{reminder_title} {reminder_content}")
    send_bark_notification(reminder_title, reminder_content)

run()
