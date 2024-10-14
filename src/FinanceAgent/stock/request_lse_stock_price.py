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

DEFAULT_LONDON_MARKET_DATA_SOURCE_LIST = [
    DATA_SOURCE_STOCK_ANALYSIS
]

def request_lse_quote(symbol_list, sub_market, kwargs):
    """ 
        Args:
            symbol_list: list of str, required
            sub_market: str, optional
            kwargs: dict, optional
        Output:
            dict
    """
    result_dict_list = []
    ## parallel, args = (symbol)
    ## Data_Source_List, which data source to fetch realtime financial data
    data_source_list = DEFAULT_LONDON_MARKET_DATA_SOURCE_LIST
    if kwargs is not None:
        data_source_list = kwargs[KEY_DATA_SOURCE_LIST] if KEY_DATA_SOURCE_LIST in kwargs else DEFAULT_LONDON_MARKET_DATA_SOURCE_LIST

    args_list = []
    args_list = [[symbol, sub_market, data_source] for symbol in symbol_list for data_source in data_source_list]
    # [("AAPL", "NASDAQ"), ("TESLA", "NYSE")]
    results = []
    try:
        with ThreadPoolExecutor(max_workers=len(args_list)) as executor:
            start_time = time.time()            
            tasks = [executor.submit(get_equity_quote_data_from_lse_wrapper, args) for args in args_list]
            for future in as_completed(tasks):
                if future is not None and future.result() is not None:
                    results.append(future.result())
            end_time = time.time()
            total_time = end_time - start_time
            print ("DEBUG: request_lse_quote end, total time %d, task cnt %d,future success cnt %d" % (total_time, len(tasks), len(results)))
    except Exception as e:
        print ("DEBUG: request_lse_quote failed...")
        print (e)
    return results

def parse_main_company_name(company_name):
    word_list =company_name.lower().split(" ")
    if len(word_list) > 0:
        return word_list[0]
    else :
        return None 

def get_equity_quote_data_from_lse_wrapper(args):
    if len(args) >= 3:
        quote = args[0] # args list of parameters
        sub_market = args[1]
        data_source = args[2]
        if data_source == DATA_SOURCE_LSE:
            json_data = {}
            quote_url = ""
            return get_quote_from_lse(quote, quote_url)
        elif data_source == DATA_SOURCE_STOCK_ANALYSIS:
            quote = quote
            quote_url = DATA_SOURCE_STOCK_ANALYSIS_LSE_URL + quote.upper()
            return get_quote_from_stock_analysis(quote, quote_url)
        else:
            json_data = {}
            quote_url = ""            
            # return get_quote_from_morningstar(quote)
            return get_quote_from_lse(quote, quote_url)
    else:
        print ("DEBUG: get_equity_quote_data_from_us_wrapper args %s None...." % str(args))
        return None

def get_quote_from_stock_analysis(quote, quote_url):
    """
        quote_url = "https://stockanalysis.com/quote/lon/SHEL/"
        {'Market Cap': '161.18B',
         'Revenue (ttm)': '238.98B',
         'Net Income (ttm)': '14.55B',
         'Shares Out': '6.22B',
         'EPS (ttm)': '2.22',
         'PE Ratio': '11.70',
         'Forward PE': '8.49',
         'Dividend': '1.05 (4.06%)',
         'Ex-Dividend Date': 'Aug 15, 2024',
         'Volume': '9,881,890',
         'Open': '2,592.50',
         'Previous Close': '2,593.00',
         "Day's Range": '2,579.50 - 2,606.00',
         '52-Week Range': '2,345.00 - 2,961.00',
         'Beta': '0.51',
         'Analysts': 'n/a',
         'Price Target': 'n/a',
         'Earnings Date': 'Oct 7, 2024'}
    """
    entity_data = {}
    entity_data["symbol"] = quote
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(quote_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        div_summary_table_list =soup.select('div[class="order-1 flex flex-row space-x-2 tiny:space-x-3 xs:space-x-4"]')
        div_summary_table = div_summary_table_list[0] if len(div_summary_table_list) > 0 else None
        table_list = div_summary_table.select('table')

        # table_info = table_list[0]
        for table_info in table_list:
            tr_list =table_info.select("tr")
            for tr in tr_list:
                td_list = tr.select("td")
                if len(td_list) >= 2:
                    key = td_list[0].text
                    value = td_list[1].text
                    entity_data[key] = value

        ## main 
        div_main_list = soup.select('div[class="mx-auto mb-2"]')
        if len(div_main_list) > 0:
            div_main = div_main_list[0] if len(div_main_list) >= 1 else None 
            if div_main is not None :
                div_main_sub_list = div_main.select('div')
                div_summary = div_main_sub_list[3] if len(div_main_sub_list) >= 4 else None 
                if div_summary is not None :
                    div_summary_list =div_summary.select("div")
                    if len(div_summary_list) > 0:
                        price_list = div_summary_list[0].select("div")
                        if len(price_list) >= 3:
                            avg_price = price_list[0].text 
                            change_price = price_list[1].text 
                            timestamp =price_list[2].text
                            entity_data["avg_price"] = avg_price
                            entity_data["change"] = change_price
                            entity_data["timestamp"] = timestamp

        ## ext info 
        entity_data[KEY_SOURCE] = DATA_SOURCE_STOCK_ANALYSIS + "," + quote_url
        entity_data[KEY_DATA_SOURCE] =  DATA_SOURCE_STOCK_ANALYSIS
        entity_data[KEY_SOURCE_URL] =  quote_url
    except Exception as e:
        print (e)
    return row_mapper_stock_analysis(entity_data)

def row_mapper_stock_analysis(entity_data):
    if entity_data is None:
        return None
    result_dict = {}
    avg_price = entity_data["avg_price"] if "avg_price" in entity_data else ""
    previous_close = entity_data["Previous Close"] if "Previous Close" in entity_data else ""
    update_time_str = entity_data["timestamp"] if "timestamp" in entity_data else ""     # 'update_time': u '2023-07-22 23:52:08.0'

    ## When market is close and not returning, use previous close set as avg_pirce
    if avg_price == "":
        avg_price = previous_close

    high_price = ""
    low_price = ""
    if "Day's Range" in entity_data:
        values = entity_data["Day's Range"]
        numbers =values.split(" - ")
        if len(numbers) >= 2:
            low_price = numbers[0]
            high_price = numbers[1]

    # row mapper
    result_dict[KEY_AVG_PRICE] = avg_price
    result_dict[KEY_HIGH_PRICE] = high_price
    result_dict[KEY_LOW_PRICE] = low_price
    result_dict[KEY_SYMBOL] = entity_data["symbol"]  if "symbol" in  entity_data else ""          # AAPL
    result_dict[KEY_TIMESTAMP] = update_time_str   # 'update_time': u '2023-07-22 23:52:08'
    result_dict[KEY_PREVIOUS_CLOSE] = previous_close
    result_dict[KEY_UPDATE_TIME] = update_time_str
    result_dict[KEY_CHANGE] = entity_data["change"] if "change" in  entity_data else ""  
    result_dict[KEY_SOURCE] = entity_data["source"] if "source" in  entity_data else ""      
    result_dict[KEY_MARKET_CAP] = entity_data["Market Cap"] if "Market Cap" in  entity_data else ""      
    result_dict[KEY_PE_RATIO] = entity_data["PE Ratio"] if "PE Ratio" in  entity_data else ""   
    for key in [KEY_AVG_PRICE, KEY_HIGH_PRICE, KEY_LOW_PRICE, KEY_PREVIOUS_CLOSE, KEY_MARKET_CAP]:
        value = result_dict[key] if key in result_dict else ""
        value_str = str(value)
        value_str = format_number_str(value_str)

        if UNIT_GBP not in value_str:
            value_str = value_str + " " + UNIT_GBP
            result_dict[key] = value_str
        else:
            result_dict[key] = value_str       
    result_dict[KEY_DATA_SOURCE] = entity_data[KEY_DATA_SOURCE] if KEY_DATA_SOURCE in entity_data else ""   
    result_dict[KEY_SOURCE_URL] = entity_data[KEY_SOURCE_URL] if KEY_SOURCE_URL in entity_data else ""   
    return result_dict

def row_mapper_lse(entity_data):
    if entity_data is None:
        return None
    result_dict = {}
    avg_price = entity_data["avg_price"] if "avg_price" in entity_data else ""
    previous_close = entity_data["previous_close"] if "previous_close" in entity_data else ""
    update_time_str = entity_data["timestamp"] if "timestamp" in entity_data else ""     # 'update_time': u '2023-07-22 23:52:08.0'
    if avg_price == "":
        avg_price = previous_close

    # row mapper
    result_dict[KEY_AVG_PRICE] = avg_price
    result_dict[KEY_HIGH_PRICE] = entity_data["Day High"] if "Day High" in entity_data else ""
    result_dict[KEY_LOW_PRICE] = entity_data["Day Low"] if "Day Low" in entity_data else ""
    result_dict[KEY_SYMBOL] = entity_data["symbol"]  if "symbol" in  entity_data else ""         
    result_dict[KEY_TIMESTAMP] = update_time_str   # 'update_time': u '2023-07-22 23:52:08'
    result_dict[KEY_PREVIOUS_CLOSE] = previous_close
    result_dict[KEY_UPDATE_TIME] = update_time_str
    result_dict[KEY_CHANGE] = entity_data["change"] if "change" in  entity_data else ""  
    result_dict[KEY_SOURCE] = entity_data["source"] if "source" in  entity_data else ""      
    result_dict[KEY_MARKET_CAP] = entity_data["Market Cap"] if "Market Cap" in  entity_data else ""      
    result_dict[KEY_PE_RATIO] = entity_data["Forward PE"] if "Forward PE" in  entity_data else ""      
    result_dict[KEY_DATA_SOURCE] = entity_data[KEY_DATA_SOURCE] if KEY_DATA_SOURCE in  entity_data else ""   
    result_dict[KEY_SOURCE_URL] = entity_data[KEY_SOURCE_URL] if KEY_SOURCE_URL in  entity_data else ""   
    return result_dict

def test_get_quote_from_stock_analysis():
    url = "https://stockanalysis.com/quote/lon/SHEL/"
    quote = "SHEL"
    info = get_quote_from_stock_analysis(quote, url)
    print (info)

def test_request_lse():
    symbol_list = ["SHEL", "ULVR"]
    results_dict = request_lse_quote(symbol_list, None, None)
    print (results_dict)

def main():
    # get_london_stock_exchange_listing()
    # test_get_quote_from_stock_analysis()
    test_request_lse()

if __name__ == '__main__':
    main()
