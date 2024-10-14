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
import codecs
import cachetools
from cachetools import cached, TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.append("..")
from .request_constants import *
from .data_util_py3 import *


DEFAULT_INDIA_MARKET_DATA_SOURCE_LIST = [
    DATA_SOURCE_MONEY_CONTROL
]

def request_nse_india_quote(symbol_list, sub_market, kwargs):
    """ 
    """
    result_dict_list = []

    data_source_list = DEFAULT_INDIA_MARKET_DATA_SOURCE_LIST
    if kwargs is not None:
        data_source_list = kwargs[KEY_DATA_SOURCE_LIST] if KEY_DATA_SOURCE_LIST in kwargs else DEFAULT_INDIA_MARKET_DATA_SOURCE_LIST

    args_list = [[symbol, sub_market, data_source] for symbol in symbol_list for data_source in data_source_list]
    results = []
    try:
        with ThreadPoolExecutor(max_workers=len(args_list)) as executor:
            start_time = time.time()
            tasks = [executor.submit(get_equity_quote_data_from_india_tse_wrapper, args) for args in args_list]
            for future in as_completed(tasks):
                if future is not None and future.result() is not None:
                    results.append(future.result())
            end_time = time.time()
            total_time = end_time - start_time
            print ("DEBUG: get_equity_quote_data_from_india_tse_wrapper end, total time %d, task cnt %d,future success cnt %d" % (total_time, len(tasks), len(results)))
    except Exception as e:
        print ("DEBUG: get_equity_quote_data_from_india_tse_wrapper failed...")
        print (e)
    return results

def get_equity_quote_data_from_india_tse_wrapper(args):
    """
        Args:

        return:
            dict of a stock 
    """
    if len(args) >= 3:
        quote = args[0] # args list of parameters
        sub_market = args[1]
        data_source = args[2]
        if data_source == DATA_SOURCE_MONEY_CONTROL:
            stock_list = get_india_nifty50_stock_from_money_control([quote])
            if len(stock_list) > 0:
                return stock_list[0]
            else:
                return {}
        else:
            stock_list = get_india_nifty50_stock_from_money_control([quote])
            if len(stock_list) > 0:
                return stock_list[0]
            else:
                return {}            
    else:    
        print ("DEBUG: get_equity_quote_data_from_india_tse_wrapper args %s None...." % str(args))
        return None

def parse_main_company_name(company_name):
    word_list =company_name.lower().split(" ")
    if len(word_list) > 0:
        return word_list[0]
    else :
        return None 

def get_india_nifty50_stock_from_money_control(symbol_list):
    """
        Args:
            symbol_list
        Output:
            List
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
    res = requests.get(INDIA_NSE_STOCK_URL_MONEY_CONTROL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    tr_list = soup.select("tr")
    base_url = INDIA_NSE_STOCK_URL_MONEY_CONTROL_BASE

    symbol_detailed_info_dict = {}
    # key: symbol, value: dict
    if tr_list is not None:
        cnt = 0
        for tr in tr_list:
            td_list = tr.select("td")
            entity_data = {}
            cnt += 1
            if len(td_list) >= 6:
                # print ("Cnt: %d" % cnt + tr.text)
                company_name_td = td_list[0]
                company_name = company_name_td.select("a")[0].text
                company_url = base_url + company_name_td.select("a")[0]["href"]
                if company_name is None:
                    continue

                url_items_list = company_url.split("/")
                symbol = url_items_list[len(url_items_list) - 1]
                symbol_upper = symbol.upper()

                industry = td_list[1].text
                last_price = td_list[2].text
                change = td_list[3].text
                change_percent = td_list[4].text  # 3.8%

                change_info = str(change) + "(" + str(change_percent) + "%" + ")"
                market_cap = td_list[5].text   # unit: Rs cr

                entity_data[KEY_SYMBOL] = symbol_upper
                entity_data[KEY_COMPANY_NAME] = company_name
                entity_data[KEY_INDUSTRY] = industry
                entity_data[KEY_LAST_PRICE] = last_price
                ## default avg, high, low to last price
                entity_data[KEY_AVG_PRICE] = last_price
                entity_data[KEY_HIGH_PRICE] = last_price
                entity_data[KEY_LOW_PRICE] = last_price
                
                entity_data[KEY_CHANGE] = change_info
                entity_data[KEY_MARKET_CAP] = market_cap
                entity_data[KEY_SOURCE] = DATA_SOURCE_MONEY_CONTROL + "," + company_url
                entity_data[KEY_DATA_SOURCE] = DATA_SOURCE_MONEY_CONTROL
                entity_data[KEY_SOURCE_URL] = company_url
                symbol_detailed_info_dict[symbol] = entity_data
                # output to name_symbol_dict 
                # name_to_symbol_list_dict[company_name] = [symbol]
                # company_name_short = parse_main_company_name(company_name)
                # name_to_symbol_list_dict[company_name_short] = [symbol]

    # output_list
    output_data_list = []

    for symbol in symbol_list:
        symbol_upper = symbol.upper()
        if symbol_upper in symbol_detailed_info_dict:
            output_data_list.append(row_mapper_money_control(symbol_detailed_info_dict[symbol_upper]))
        else:
            print ("DEBUG: get_india_nifty50_stock symbol not in list %s" % symbol_upper)
            continue
    return output_data_list

def row_mapper_money_control(entity_data):
    """
                entity_data["symbol"] = symbol
                entity_data["industry"] = industry
                entity_data["last_price"] = last_price
                entity_data["change"] = change_info
                entity_data["market_cap"] = market_cap
                entity_data["source"] = DATA_SOURCE_MONEY_CONTROL    
    """
    if entity_data is None:
        return None
    result_dict = {}
    avg_price = entity_data[KEY_AVG_PRICE] if KEY_AVG_PRICE in entity_data else ""
    previous_close = entity_data[KEY_LAST_PRICE] if KEY_LAST_PRICE in entity_data else ""
    update_time_str = entity_data[KEY_TIMESTAMP] if KEY_TIMESTAMP in entity_data else ""     # 'update_time': u '2023-07-22 23:52:08.0'
    if avg_price == "":
        avg_price = previous_close
    # row mapper
    result_dict[KEY_AVG_PRICE] = avg_price
    result_dict[KEY_HIGH_PRICE] = entity_data[KEY_HIGH_PRICE] if KEY_HIGH_PRICE in entity_data else ""  
    result_dict[KEY_LOW_PRICE] = entity_data[KEY_LOW_PRICE] if KEY_LOW_PRICE in entity_data else ""
    result_dict[KEY_SYMBOL] = entity_data[KEY_SYMBOL]  if KEY_SYMBOL in  entity_data else ""          
    result_dict[KEY_COMPANY_NAME] = entity_data[KEY_COMPANY_NAME]  if KEY_COMPANY_NAME in  entity_data else ""        
    result_dict[KEY_TIMESTAMP] = update_time_str   # 'update_time': u '2023-07-22 23:52:08'
    result_dict[KEY_PREVIOUS_CLOSE] = previous_close
    result_dict[KEY_UPDATE_TIME] = update_time_str
    result_dict[KEY_CHANGE] = entity_data[KEY_CHANGE] if KEY_CHANGE in  entity_data else ""  
    result_dict[KEY_SOURCE] = entity_data[KEY_SOURCE] if KEY_SOURCE in  entity_data else ""      
    result_dict[KEY_MARKET_CAP] = entity_data[KEY_MARKET_CAP] if KEY_MARKET_CAP in  entity_data else ""      
    result_dict[KEY_PE_RATIO] = entity_data["PE Ratio"] if "PE Ratio" in  entity_data else ""      

    for key in [KEY_AVG_PRICE, KEY_HIGH_PRICE, KEY_LOW_PRICE, KEY_PREVIOUS_CLOSE, KEY_MARKET_CAP]:
        value = result_dict[key] if key in result_dict else ""
        value_str = str(value)
        value_str = format_number_str(value_str)

        if UNIT_INR not in value_str:
            value_str = value_str + " " + UNIT_INR
            result_dict[key] = value_str
        else:
            result_dict[key] = value_str
    result_dict[KEY_DATA_SOURCE] = entity_data[KEY_DATA_SOURCE] if KEY_DATA_SOURCE in  entity_data else ""   
    result_dict[KEY_SOURCE_URL] = entity_data[KEY_SOURCE_URL] if KEY_SOURCE_URL in  entity_data else ""   
    return result_dict

def test_request_nse_india_quote():
    """
         infosys: IT 
         india coal: CI11
    """
    symbol_list = ["IT", "CI11"]
    results = request_nse_india_quote(symbol_list, "", {})
    print (results)

def main():
    test_request_nse_india_quote()

if __name__ == '__main__':
    main()
