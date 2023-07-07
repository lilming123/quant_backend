import csv
from datetime import datetime

from dateutil.relativedelta import relativedelta
from hs_udata import set_token, index_constituent, get_barra_factor, stock_quote_weekly, stock_quote_yearly
import numpy as np
import pandas as pd
import os

hs_token = "DzVp6WDIPwZJK0jIFUA0DmdV3Sfy8vB1W8AwZJld-bV_TTeJZdohzBkX2vwVZsNb"
set_token(hs_token)
# 沪深300成分股的所有股票
stocks_list = []
# 当前投资组合和仓位
now_stocks = {}
# 策略组合和仓位
strategy_stocks = {}
# 每周收益率
weekly_returns = {}
# 累计收益率
cum_returns = {}
# 沪深300累计收益率
hs_cum_returns = {}


# 初始化策略仓位
def init_stra_wights(now_date):
    while get_barra_factor(stock_code=str(stocks_list), factor_name="cne5_earnings_yield", start_date=str(now_date),
                           end_date=str(now_date)).empty:
        now_date = now_date - relativedelta(days=1)
    df_earning = get_barra_factor(stock_code=str(stocks_list), factor_name="cne5_earnings_yield", start_date=str(now_date),
                          end_date=str(now_date))
    df_earning = df_earning.loc[df_earning['factorvalue'] != 'nan']
    else_stock = df_earning.sort_values(by='factorvalue', ascending=False)[50:]
    wights_stock = df_earning.sort_values(by='factorvalue', ascending=False).head(50)
    else_wights = 0
    for each_stock in stocks_list:
        if each_stock in else_stock['stockcode'].tolist():
            strategy_stocks[each_stock] = 0.001
            else_wights += 0.001
        else:
            strategy_stocks[each_stock] = None
    all_factor = wights_stock['factorvalue'].astype(float).sum()
    for index, row in wights_stock.iterrows():
        if (1 - else_wights) * float(row['factorvalue']) / all_factor > 0.05:
            print("超过5%")
        strategy_stocks[row['stockcode']] = (1 - else_wights) * float(row['factorvalue']) / all_factor


# 初始化实际仓位
def init_now_wights():
    for each_stock in stocks_list:
        if strategy_stocks[each_stock] is not None:
            now_stocks[each_stock] = strategy_stocks[each_stock]
        else:
            now_stocks[each_stock] = 0


# 计算收益率和累计收益率
def cal_return(now_date):
    # 目前累计收益率
    now_cum_returns = 0
    # 下周一开盘
    open_delta = relativedelta(days=3)
    # 本周五收盘
    close_delta = relativedelta(days=4)
    while now_date <= datetime(year=2023, month=4, day=1):

        # 如果是收盘日
        if now_date.isoweekday() == 5:
            init_stra_wights(now_date)
            now_date = now_date + open_delta
        # 如果是开盘日
        elif now_date.isoweekday() == 1:
            now_df = stock_quote_weekly(en_prod_code=','.join(map(str, stocks_list)), trading_date=str(now_date),
                                        adjust_way=2)
            last_df = stock_quote_weekly(en_prod_code=','.join(map(str, stocks_list)),
                                         trading_date=str(now_date - relativedelta(days=7)), adjust_way=2)
            each_stock_returns = {}
            for each_stock in [k for k, v in now_stocks.items() if v != 0]:
                if now_df.loc[now_df['prod_code'] == each_stock].empty or last_df.loc[
                    last_df['prod_code'] == each_stock].empty:
                    continue
                now_row = now_df.loc[now_df['prod_code'] == each_stock]
                last_row = last_df.loc[last_df['prod_code'] == each_stock]
                if now_row.iloc[0]['week_open_price'] == '' or last_row.iloc[0]['week_open_price'] == '':
                    continue
                now_price = float(now_row.iloc[0]['week_open_price'])
                last_price = float(last_row.iloc[0]['week_open_price'])
                each_stock_returns[each_stock] = (now_price - last_price) / last_price
            each_weekly_returns = 0
            for each_stock in each_stock_returns.keys():
                each_weekly_returns += now_stocks[each_stock] * each_stock_returns[each_stock]
            weekly_returns[now_date] = each_weekly_returns
            now_cum_returns += each_weekly_returns
            cum_returns[now_date] = now_cum_returns
            # 调仓
            init_now_wights()
            now_date = now_date + close_delta


def stock_list():
    data = index_constituent(index_stock_code="399300")
    for index, row in data.iterrows():
        hz = '.SH' if row['secu_market'] == '上海证券交易所' else '.SZ'
        each_stock = row['secu_code'] + hz
        stocks_list.append(each_stock)


def get_hs_returns():
    now_hs300_return = 0
    now_date = datetime(year=2015, month=1, day=5)
    week_delta = relativedelta(days=7)
    while now_date <= datetime(year=2023, month=6, day=1):
        weekly_returns = stock_quote_weekly(en_prod_code="000300.SH", trading_date=str(now_date), adjust_way=2)
        hs_returns = weekly_returns.loc[0, 'week_px_change_rate']
        print(str(now_date))
        if hs_returns == '':
            now_hs300_return += 0
        else:
            now_hs300_return += float(hs_returns)
        hs_cum_returns[now_date] = now_hs300_return
        now_date = now_date + week_delta
    hs300_weekly_fields = list(hs_cum_returns.keys())
    with open('./file/hs300_returns.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=hs300_weekly_fields)
        writer.writeheader()
        writer.writerow(hs_cum_returns)

def get_returns():
    with open('app/public/cum_returns.csv', 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 2:  # 因为索引从0开始，所以第三行的索引是2
                return list(row)


if __name__ == '__main__':
    now_date = datetime(year=2015, month=4, day=3)
    # 获取股票池数据
    stock_list()
    # 初始化策略仓位
    init_stra_wights(now_date)
    # 初始化实际仓位
    now_date = now_date + relativedelta(days=3)
    init_now_wights()
    # 计算收益率与累计收益率
    now_date = now_date + relativedelta(days=4)
    cal_return(now_date)
    # get_hs_returns()
    weekly_fields = list(weekly_returns.keys())

    # 写入csv文件
    with open('./file/weekly_returns.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=weekly_fields)
        writer.writeheader()
        writer.writerow(weekly_returns)

    cum_fields = list(cum_returns.keys())
    # 写入csv文件
    with open('./file/cum_returns.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=cum_fields)
        writer.writeheader()
        writer.writerow(cum_returns)
