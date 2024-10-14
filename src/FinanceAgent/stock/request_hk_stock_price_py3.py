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

from .request_constants import RESPONSE_SOURCE_STOCK_PRICE_HKEX
from .request_constants import *
from .data_util_py3 import *

DEFAULT_HK_MARKET_DATA_SOURCE_LIST = [
    DATA_SOURCE_HKEX
]

def request_hk_quote(symbol_list, kwargs):
    """
        Args:

        Output:
    """

    result_dict_list = []
    data_source_list = DEFAULT_HK_MARKET_DATA_SOURCE_LIST
    if kwargs is not None:
        data_source_list = kwargs[KEY_DATA_SOURCE_LIST] if KEY_DATA_SOURCE_LIST in kwargs else DEFAULT_HK_MARKET_DATA_SOURCE_LIST

    args_list = [[symbol, data_source, kwargs] for symbol in symbol_list for data_source in data_source_list]
    results = []
    try:
        with ThreadPoolExecutor(max_workers=len(args_list)) as executor:
            start_time = time.time()
            tasks = [executor.submit(request_hk_quote_api_wrapper, args) for args in args_list]
            for future in as_completed(tasks):
                if future is not None and future.result() is not None:
                    results.append(future.result())
            end_time = time.time()
            total_time = end_time - start_time
            print ("DEBUG: get_equity_quote_data_from_hkex_wrapper end, total time %d, task cnt %d,future success cnt %d" % (total_time, len(tasks), len(results)))
    except Exception as e:
        print ("DEBUG: get_equity_quote_data_from_hkex_wrapper failed...")
        print (e)
    return results


def request_hk_quote_api_wrapper(args):
    """
        Args:

        return:
            dict of a stock 
    """
    if len(args) >= 3:
        quote = args[0] # args list of parameters
        data_source = args[1]
        kwargs = args[2]
        # fetch token from kwwars
        token = kwargs[KEY_TOKEN] if KEY_TOKEN in kwargs else ""

        if data_source == DATA_SOURCE_HKEX:

            stock_result_list = request_hk_quote_from_hkex(token, [quote], kwargs)
            if len(stock_result_list) > 0:
                return stock_result_list[0]
            else:
                return {}
        else:
            stock_result_list = request_hk_quote_from_hkex(token, [quote], kwargs)
            if len(stock_result_list) > 0:
                return stock_result_list[0]
            else:
                return {}         
    else:    
        print ("DEBUG: get_equity_quote_data_from_hkex_wrapper args quote, data_source, kwargs missing None| %s" % str(args))
        return None

def request_hk_quote_from_hkex(token, symbol_list, kwargs):
    """
        Inputs:
                token: special token
                symbol_list:list, symbol list
                kwargs if not provided, using default may be outdated
        Return:
                data: type dict
                key 'symbol', value 'symbol'
                key 'avg_price', value average price
        Example URL is :
            https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym=700&token=evLtsLsBNAUVTPxtGqVeG28I7PscNOltZKYXOjej8dE1Ce1wZfKeI7%2bNJoEye8jb&lang=eng&qid=1728822094548&callback=jQuery351021232848445743602_1728822090850&_=1728822090851
            
            qid = 1728822094548
            callback = jQuery351021232848445743602_1728822090850
    """
    # assemble other 
    timestamp = int(time.time())
    qid = kwargs["qid"] if "qid" in kwargs else str(timestamp)
    callback = kwargs["callback"] if "callback" in kwargs else (HKEX_JQUERY_PREFIX + str(timestamp))

    equity_data_list = get_equity_quote_data_from_hkex_list_parallel(token, symbol_list, qid=qid, callback=callback)
    result_dict_list = []
    if len(equity_data_list) > 0:
        for equity_data in equity_data_list:
            if type(equity_data) == dict:
                result_dict = row_mapper_hkex(equity_data)
                result_dict_list.append(result_dict)
    else:
        print ("DEBUG: request_hk_quote get_equity_quote_data_from_hkex_list_parallel return empty list...")
    return result_dict_list

# cache 12h=12*60*60s
@cached(cache= TTLCache(maxsize= 33, ttl = 43200))
def fetch_clean_token():
    return fetch_clean_token_by_force()

def fetch_clean_token_by_force():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
    page_max = 100
    res = requests.get(HKEX_TENCENT_STOCK_URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    script_list = soup.select("script")
    special_token_mark = "LabCI.getToken"
    parsed_script_list = []
    for script in script_list:
        if special_token_mark in script.text:
            parsed_script_list.append(script)
    # print("DEBUG: parsed_script_list is: " + str(parsed_script_list))

    final_token = None
    if len(parsed_script_list) == 0:
        final_token = None
    else:
        raw_text = parsed_script_list[0].text
        search_list = re.search(' return ', raw_text)
        num=search_list.span()

        token_len = 68
        start_index = num[1] + 1 if len(num) > 0 else 0
        token = raw_text[start_index:start_index+token_len]
        final_token = token.split('"')[0]
        print ("DEBUG: final token len is %d" % len(final_token))
    return final_token

def get_equity_quote_data_from_hkex(token, symbol, qid, callback):
    """
        BASE64
        jQuery351019444984572939505_1690107383211({"data":{"responsecode":"002","responsemsg":"Invalid Input"},"qid":"1690107390362"})
    """
    equity_data = None
    if token is None or symbol is None or qid is None or callback is None:
        print ("DEBUG: get_equity_quote_data_from_hkex Input token, symbol, qid, callback contains None...")
        return equity_data
    try:
        special_token_list = ["<br/>"]
        url = HKEX_QUOTE_BASE_URL % (symbol, token, qid, callback)
        print ("DEBUG: HKEX Requests symbol is %s, url is %s" % (symbol, url))
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        res = requests.get(url, headers=headers)
        soup1 = BeautifulSoup(res.text, 'html.parser')

        output_json_text = soup1.text
        for special_token in special_token_list:
            output_json_text = output_json_text.replace(special_token, "")
        search_result = re.search("[(]", output_json_text)
        if search_result is None:
            return equity_data
        start_index = search_result.span()[0] + 1
        end_index = len(output_json_text) - 1
        output_json = output_json_text[start_index:end_index]
        stock_quote_json = json.loads(output_json)
        response_code = stock_quote_json["data"]["responsecode"]
        if response_code == "000":
            equity_data=stock_quote_json["data"]["quote"]
        else:
            equity_data= None
    except Exception as e:
        print (e)
        equity_data = None
    return equity_data
    
def get_equity_quote_data_from_hkex_list(token, symbol_list):
    result_dict_list = []
    for symbol in symbol_list:
        entity_data = get_equity_quote_data_from_hkex(token, symbol)
        if entity_data is not None:
            result_dict_list.append(entity_data)
    return result_dict_list

def get_equity_quote_data_from_hkex_wrapper(args):
    """
    """
    try:
        if len(args) >= 4:
            token = args[0]
            symbol = args[1]
            qid = args[2]
            callback = args[3]
            return get_equity_quote_data_from_hkex(token, symbol, qid, callback)
        else:
            print ("DEBUG: Inputs Args missing values, token, symbol, qid, callback are all required...")
            return None
    except Exception as e:
        print ("DEBUG: get_equity_quote_data_from_hkex_wrapper failed...")
        print (e)
        return None

def get_equity_quote_data_from_hkex_list_parallel(token, symbol_list, **kwargs):
    """
        Each Calling takes 3 - 4 seconds
    """
    result_dict_list = []
    qid = kwargs["qid"] if "qid" in kwargs else ""
    callback = kwargs["callback"] if "callback" in kwargs else ""

    ## parallel
    args_list = [(token, symbol, qid, callback) for symbol in symbol_list]
    results = []
    try:
        with ThreadPoolExecutor(max_workers=len(args_list)) as executor:
            start_time = time.time()            
            tasks = [executor.submit(get_equity_quote_data_from_hkex_wrapper, args) for args in args_list]
            # as_completed
            for future in as_completed(tasks):
                if future is not None and future.result() is not None:
                    results.append(future.result())
            end_time = time.time()
            total_time = end_time - start_time
            print ("DEBUG: get_equity_quote_data_from_hkex_list_parallel end, total time %d, task cnt %d,future success cnt %d" % (total_time, len(tasks), len(results)))
    except Exception as e:
        print ("DEBUG: get_equity_quote_data_from_hkex_list_parallel failed...")
        print (e)
    return results

def if_market_close(equity_data):
    """
    """
    if_close = False
    if ((equity_data["as"] is None or equity_data["as"] == "") 
            and (equity_data["hi"] is None or equity_data["hi"] == "") 
            and (equity_data["lo"] is None or equity_data["lo"] == "") 
            and (equity_data["hc"] is not None and equity_data["hc"] != "")
        ):
        if_close = True
    return if_close

def row_mapper_hkex(equity_data):
    """
        @args
            entity_data: dict 
        
        @Return:
            result_dict: dict
    """
    result_dict = {}
    if if_market_close(equity_data):
        display_price = equity_data["hc"] 
        result_dict[KEY_AVG_PRICE] = display_price  ## average price
        result_dict[KEY_HIGH_PRICE] = display_price
        result_dict[KEY_LOW_PRICE] = display_price
        result_dict[KEY_PREVIOUS_CLOSE] = display_price
    else:
        result_dict[KEY_AVG_PRICE] = equity_data["as"]  ## average price
        result_dict[KEY_HIGH_PRICE] = equity_data["hi"]
        result_dict[KEY_LOW_PRICE] = equity_data["lo"]
        result_dict[KEY_PREVIOUS_CLOSE] = equity_data["hc"] 
    result_dict[KEY_SYMBOL] = equity_data["sym"]                # 3690
    result_dict[KEY_SYMBOL_HK] = equity_data["ric"]             # 'ric': u '3690.HK',
    result_dict[KEY_SYMBOL_NAME_HK] = equity_data["nm"]            # Meituan - W 
    update_time_str = equity_data["db_updatetime"] if "db_updatetime" in equity_data else ""     # 'update_time': u '2023-07-22 23:52:08.0'
    update_time_str = update_time_str              # '29 Jul 2023 18:40:00' -> '29 Jul 2023'
    result_dict[KEY_TIMESTAMP] = update_time_str   # 'update_time': u '2023-07-22 23:52:08'
    result_dict[KEY_UPDATE_TIME] = update_time_str

    market_cap = equity_data["mkt_cap"] if "mkt_cap" in equity_data else ""
    market_cap_u = equity_data["mkt_cap_u"] if "mkt_cap_u" in equity_data else ""
    result_dict[KEY_MARKET_CAP] = market_cap + " " + market_cap_u
    result_dict[KEY_PE_RATIO] = equity_data["pe"] if "pe" in equity_data else ""
    result_dict[KEY_CHANGE] = equity_data["nc"] if "nc" in equity_data else "" # change

    data_source = RESPONSE_SOURCE_STOCK_PRICE_HKEX % (equity_data["sym"] if "sym" in equity_data else "")

    ## Append UNIT_HKD
    for key in [KEY_AVG_PRICE, KEY_HIGH_PRICE, KEY_LOW_PRICE, KEY_PREVIOUS_CLOSE, KEY_MARKET_CAP]:
        value = result_dict[key] if key in result_dict else ""
        value_str = str(value)
        if UNIT_HKD not in value_str:
            value_str = value_str + " " + UNIT_HKD
            result_dict[key] = value_str
        else:
            result_dict[key] = value_str
    result_dict[KEY_SOURCE] = data_source
    result_dict[KEY_DATA_SOURCE] = DATA_SOURCE_HKEX
    result_dict[KEY_SOURCE_URL] = RESPONSE_SOURCE_STOCK_PRICE_HKEX_URL % (equity_data["sym"] if "sym" in equity_data else "")
    return result_dict

def test_request_hk_quote():

    token = fetch_clean_token_by_force()
    symbol_list = ["700", "1024"]
    kwargs = {}
    kwargs[KEY_TOKEN] = token
    quote_json = request_hk_quote(symbol_list, kwargs)
    print (quote_json)

def main():
    test_request_hk_quote()

if __name__ == '__main__':
    main()
