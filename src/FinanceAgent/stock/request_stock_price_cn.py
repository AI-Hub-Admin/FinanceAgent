#coding=utf-8
#!/usr/bin/python

import requests
import os
import re
import bs4
from bs4 import BeautifulSoup
import sys

import json
import time
import datetime
import numpy as np
import codecs
import cachetools
from cachetools import cached, TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.append("..")
from .request_constants import *
from .data_util_py3 import *

def request_sh_sz_quote(symbol_list, kwargs):
    """
        API for query symbols from Shenzhen and Shanghai Stock Market
        
        Args:
            symbol_list: list of str
            kwargs: dict
        Output:
            dict
    """
    matched_symbol_json_list = []
    for symbol in symbol_list:
        request_json = {}
        request_json["code"] = symbol
        matched_symbol_json_list.append(request_json)
    xueqiu_result = xueqiu_api(matched_symbol_json_list)
    xueqiu_stock_price_dict = xueqiu_data_row_mapper(xueqiu_result)
    return xueqiu_stock_price_dict

def add_exchange(shares):
    shares_str = str(shares)
    if (shares_str[:2] == "00") or (shares_str[:3] == "200") or (shares_str[:3] == "300"):
        r_data = "sz"+shares_str
    elif (shares_str[:2] == "60") or (shares_str[:2] == "51") or (shares_str[:3] == "900") or (shares_str[:2] == "68"):
        r_data = "sh"+shares_str
    else:
        r_data = ""
    return r_data

def xueqiu_data_row_mapper(dat):
    """
        Input:
            dat: json str
                symbol: Symbol of Stock
                current: Current Price
                percent: Stock Price Moving Percentage
                chg: Change Amount
                high: Hight Price
                low: Low Price
                avg_price: Average Price
                timestamp: timestamp
                open: open price
                last_close: last clost price
        Return:
                data: type dict
                key 'symbol', value 'symbol'
                key 'symbol_name', value 'symbol_name'  : quote -> symbol
                key 'avg_price', value average price

        # Data Sample
        {
            "data": [{
                "symbol": "SZ002299",
                "current": 13.41,
                "percent": 1.36,
                "chg": 0.18,
                "timestamp": 1728889497000,
                "volume": 9926603,
                "amount": 1.32019052E8,
                "market_capital": 1.6673997956E10,
                "float_market_capital": 1.6673078379E10,
                "turnover_rate": 0.8,
                "amplitude": 3.33,
                "open": 13.24,
                "last_close": 13.23,
                "high": 13.48,
                "low": 13.04,
                "avg_price": 13.3,
                "trade_volume": 0,
                "side": 1,
                "is_trade": false,
                "level": 1,
                "trade_session": null,
                "trade_type": null,
                "current_year_percent": -20.41,
                "trade_unique_id": "9926603",
                "type": 11,
                "bid_appl_seq_num": null,
                "offer_appl_seq_num": null,
                "volume_ext": null,
                "traded_amount_ext": null,
                "trade_type_v2": null,
                "yield_to_maturity": null
            }],
            "error_code": 0,
            "error_description": null
        }
    """
    jdat = json.loads(dat)
    rdat = []
    for n in jdat['data']:
        ndic = {}

        key_list = ['symbol', 'current', 'percent', 'chg', 'high', 'low', 'avg_price', 'timestamp', 'open', 'last_close', 'market_capital']
        for key in key_list:
            ndic[key] = n[key] if (key in n and n[key] is not None) else ""

        ## Format to Display Fields: change
        change_str = n['chg'] if 'chg' in n else "-"
        change_percent_str = n['percent'] if 'percent' in n else "-"
        final_change_str = "%s(%s" % (change_str, change_percent_str) + "%)"  # -41.0(-2.19%)
        if final_change_str is None:
            final_change_str = "-"
        ndic['change'] = final_change_str
    
        previous_close = n['last_close'] if 'last_close' in n else ""
        ndic['previous_close'] = previous_close 

        ## Change market cap to format
        market_capitalization = str("%.2f" % (float(n['market_capital'])/100000000.0)) + " " + UNIT_ONE_IN_TEN_B_CNY
        ndic['market_capitalization'] = market_capitalization
        ndic['pe_ratio'] = n['pe'] if 'pe' in n else ""

        timestamp = int(n['timestamp']) if 'timestamp' in n else 0
        timestamp_int = int(timestamp/1000.0)
        update_datetime = datetime.datetime.fromtimestamp(timestamp_int)
        update_time = update_datetime.strftime('%Y-%m-%d %H:%M:%S')
        ndic['update_time'] = update_time 
        ## Update unit to UNIT_CNY
        for key in ["avg_price", "high", "low", "previous_close", "market_capitalization"]:
            value = ndic[key] if key in ndic else ""
            value_str = str(value)
            if UNIT_CNY not in value_str:
                value_str = value_str + " " + UNIT_CNY
                ndic[key] = value_str
            else:
                ndic[key] = value
        ndic['source'] = RESPONSE_SOURCE_STOCK_PRICE_XUEQIU % (ndic['symbol'] if 'symbol' in ndic else "")
        ndic[KEY_DATA_SOURCE] = DATA_SOURCE_XUEQIU 
        ndic[KEY_SOURCE_URL] = RESPONSE_SOURCE_STOCK_PRICE_XUEQIU_URL % (ndic['symbol'] if 'symbol' in ndic else "")

        rdat.append(ndic)
    
    return rdat


def xueqiu_api(shares_list):
    """
        Args:
            shares_list, list of json [{ code, price, quantity}]
            # https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=SH601231,SZ002299&_=1541640828575

        Return:
            r_data: str json str
    """
    he = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62"}
    url_parameter = ""
    for shares in shares_list:
        exchange_shares = shares["code"].upper()
        if exchange_shares != "":
            url_parameter = url_parameter + exchange_shares + ","
    
    url = CN_STOCK_URL_XUEQIU + url_parameter[:-1]
    r = requests.get(url,headers=he)
    r_data = r.text
    return r_data

def test_requet_stock_price():
    shares_list = [
        {'code': 'SZ002299'},
        {'code': 'SH513050'},
        {'code': 'SH601231'},
        {'code': 'SZ002273'},
        {'code': 'SZ002461'}
    ]

    for n in xueqiu_analysis_return(xueqiu_api(shares_list)):
        print(n)

def main():
    test_requet_stock_price()

if __name__ == '__main__':
    main()
