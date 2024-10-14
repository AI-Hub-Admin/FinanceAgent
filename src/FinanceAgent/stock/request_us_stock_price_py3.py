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
from .request_constants import *
from .data_util_py3 import *

DEFAULT_US_MARKET_DATA_SOURCE_LIST = [
    # DATA_SOURCE_MARKET_BEATS, 
    # DATA_SOURCE_STOCK_ANALYSIS，
    # DATA_SOURCE_ZACKS,
    DATA_SOURCE_MORNING_STAR
]

def request_us_quote(symbol_list, sub_market, kwargs):
    """
        Inputs:
                symbol_list:list, symbol list
                sub_market: NASDAQ/NYSE
                kwargs: dict
        Return:
                data: type dict
                key 'symbol', value 'symbol'
                key 'avg_price', value average price
    """
    equity_data_list = get_equity_quote_data_from_us_list_parallel(symbol_list, sub_market, kwargs)
    return equity_data_list

def get_equity_quote_data_from_us_list_parallel(symbol_list, sub_market, kwargs):
    """
    """
    result_dict_list = []
    ## parallel, args = (symbol)
    args_list = []
    ## Data_Source_List, which data source to fetch realtime financial data
    data_source_list = DEFAULT_US_MARKET_DATA_SOURCE_LIST
    if kwargs is not None:
        data_source_list = kwargs[KEY_DATA_SOURCE_LIST] if KEY_DATA_SOURCE_LIST in kwargs else DEFAULT_US_MARKET_DATA_SOURCE_LIST
    ## DATA_SOURCE_MARKET_BEATS
    args_list = [[symbol, sub_market, data_source] for symbol in symbol_list for data_source in data_source_list]
    results = []
    try:
        with ThreadPoolExecutor(max_workers=len(args_list)) as executor:
            start_time = time.time()
            tasks = [executor.submit(get_equity_quote_data_from_us_wrapper, args) for args in args_list]
            for future in as_completed(tasks):
                if future is not None and future.result() is not None:
                    results.append(future.result())
            end_time = time.time()
            total_time = end_time - start_time
            print ("DEBUG: get_equity_quote_data_from_us_list_parallel end, total time %d, task cnt %d,future success cnt %d" % (total_time, len(tasks), len(results)))
    except Exception as e:
        print ("DEBUG: get_equity_quote_data_from_us_list_parallel failed...")
        print (e)
    return results

def get_equity_quote_data_from_us_wrapper(args):
    if len(args) >= 3:
        quote = args[0]            
        sub_market = args[1]
        data_source = args[2]
        if data_source == DATA_SOURCE_ZACKS:
            return get_quote_from_zacks(quote)
        elif data_source == DATA_SOURCE_MARKET_BEATS:
            return get_quote_from_market_beats(sub_market, quote)
        elif data_source == DATA_SOURCE_MORNING_STAR:
            return get_quote_from_morningstar(quote)
        else:
            return get_quote_from_morningstar(quote)
    else:
        print ("DEBUG: get_equity_quote_data_from_us_wrapper args %s None...." % str(args))
        return None


#### API to GET Stock Data From Market Beats
def get_stock_list_from_market_beats():

    market_stock_quote_name_dict = {}

    # NYSE
    nyse_stock_list_url = "https://www.marketbeat.com/stocks/NYSE/"
    nyse_market = "NYSE"
    market_stock_quote_name_dict[nyse_market] = get_stock_list_from_market_beats_url(nyse_stock_list_url)

    nasdaq_stock_list_url = "https://www.marketbeat.com/stocks/NASDAQ/"
    nasdaq_market = "NASDAQ"
    market_stock_quote_name_dict[nasdaq_market] = get_stock_list_from_market_beats_url(nasdaq_stock_list_url)

    json_str = json.dumps(market_stock_quote_name_dict, ensure_ascii=False)
    print ("DEBUG: READ stock json_str size %d" % len(json_str))
    output_file = "./stock_market_symbol_name_dict_us.json"
    file = codecs.open(output_file, "w", "utf-8")
    file.write(json_str + "\n")
    file.close()

def get_stock_list_from_market_beats_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
    # house = 'https://www.hkex.com.hk/?sc_lang=EN'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    tr_list = soup.select('tr')

    # k1: quote, e.g. v1: market, e.g. NYSE, NASDAQ
    stock_quote_name_dict = {} 
    for tr in tr_list:
        title = tr.select('div[class="title-area"]')[0].text if len(tr.select('div[class="title-area"]')) > 0 else None
        ticker = tr.select('div[class="ticker-area"]')[0].text if len(tr.select('div[class="ticker-area"]')) > 0 else None
        img = tr.select('div[class="company-thumbnail"]')[0].select("img")[0] if len(tr.select('div[class="company-thumbnail"]')) > 0 else None
        img_source = img["src"] if img is not None else ""
        stock_quote_name_dict[ticker] = title
    return stock_quote_name_dict



#### API to GET Stock Data From Morningstar morningstar.com
def get_quote_from_morningstar(quote):
    """
       quote: AAPL 
       return: equity_data dict{}
       {u'Day Range': u'194.14 196.63  ',
         u'Forward Div Yield': u'0.51%',
         u'Industry': u'Consumer Electronics',
         u'Investment Style': u' Large Growth',
         u'Last Close': u'195.83',
         u'Market Cap': u'3.0802 Tril',
         u'Price / Book': u'49.85',
         u'Price / Sales': u'8.16',
         u'Sector': u'Technology',
         u'Trailing Div Yield': u'0.47%',
         u'Volume / Avg': u'48.3 Mil 56.9 Mil',
         u'Year Range': u'124.17  198.23  ',
         'high_price': u'196.63',
         'low_price': u'194.14'}
    """
    url = "https://www.morningstar.com/stocks/xnas/%s/quote" % quote.lower()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
    # house = 'https://www.hkex.com.hk/?sc_lang=EN'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    equity_data = {}
    equity_data["quote"] = quote
    list_items =soup.select('div[class="mdc-description-list-item__mdc"]')
    if len(list_items) > 0:
        for item in list_items:
            # dt tag
            dt_tag_list = item.select('dt')
            li_label = dt_tag_list[0].text if len(dt_tag_list) > 0 else ""

            # dd tag
            dd_tag_list = item.select('dd')
            li_value = dd_tag_list[0].text if len(dd_tag_list) > 0 else ""
            equity_data[li_label] = li_value
    else:
        equity_data = {}

    # average price
    div_summary = soup.select('div[class="mdc-price-summary__last-price__mdc"]')
    if len(div_summary) > 0:
        span_list = div_summary[0].select("span")
        if len(span_list) >= 4:
            average_price = span_list[0].text
            # span_list[1]
            change = span_list[2].text
            # convert unicode from slash to minus sign
            change = format_number_str(change)
            change_percent = span_list[3].text
            # correct change percent minus sign
            if MINUS_SIGN in change:
                change_percent = MINUS_SIGN + change_percent

            equity_data[KEY_AVG_PRICE] = average_price
            equity_data[KEY_CHANGE] = change
            equity_data[KEY_CHANGE_PERCENT] = change_percent

    equity_data[KEY_DATA_SOURCE] = DATA_SOURCE_MORNING_STAR
    equity_data[KEY_SOURCE_URL] = url

    return row_mapper_morningstar(equity_data)

def row_mapper_morningstar(entity_data):
    """
        entity_data of morningstar
    """
    if entity_data is None:
        return None
    result_dict = {}

    update_time_str = entity_data["timestamp"] if "timestamp" in entity_data else "" 
    
    high_price = ""
    low_price = ""
    previous_close = ""
    if "Day Range" in entity_data:
        values = entity_data["Day Range"]
        values = values.replace("$", "")
        values = values.replace(" ", "")
        # to types of hypens
        values = values.replace("–", "-")
        number_list = values.split("-")
        if len(number_list) >= 2:
            low_price = number_list[0] 
            high_price = number_list[1] 
    if "Previous Close Price" in entity_data:
        previous_close = entity_data["Previous Close Price"]

    # row mapper
    result_dict[KEY_AVG_PRICE] = entity_data[KEY_AVG_PRICE] if KEY_AVG_PRICE in  entity_data else ""
    result_dict[KEY_HIGH_PRICE] = high_price
    result_dict[KEY_LOW_PRICE] = low_price
    result_dict[KEY_SYMBOL] = entity_data["quote"]  if "quote" in  entity_data else ""         
    result_dict[KEY_UPDATE_TIME] = update_time_str
    result_dict[KEY_PREVIOUS_CLOSE] = previous_close
    result_dict[KEY_CHANGE] = entity_data[KEY_CHANGE] if KEY_CHANGE in  entity_data else ""  
    result_dict[KEY_MARKET_CAP] = entity_data["Market Cap"] if "Market Cap" in  entity_data else ""      
    result_dict[KEY_PE_RATIO] = entity_data["Price/Earnings (Normalized)"] if "Price/Earnings (Normalized)" in  entity_data else ""
    result_dict[KEY_DATA_SOURCE] = entity_data[KEY_DATA_SOURCE] if KEY_DATA_SOURCE in  entity_data else ""   
    result_dict[KEY_SOURCE_URL] = entity_data[KEY_SOURCE_URL] if KEY_SOURCE_URL in  entity_data else ""   

    # append unit including USD, CNY, etc.
    # format: number + " " + unit
    for key in [KEY_AVG_PRICE, KEY_HIGH_PRICE, KEY_LOW_PRICE, KEY_PREVIOUS_CLOSE, KEY_MARKET_CAP]:
        value = result_dict[key] if key in result_dict else ""
        value_str = str(value)
        # remove prevailing dollar sign
        value_str = value_str.replace("$", "")
        if UNIT_USD not in value_str:
            value_str = value_str + " " + UNIT_USD
            result_dict[key] = value_str
        else:
            result_dict[key] = value_str

    return result_dict


#### API to GET Stock Data From NASDAQ nasdaq.com
def get_quote_from_nasdaq(quote):
    """
       quote: tsla
    """
    equity_data = {}
    equity_data["quote"] = quote
    try:
        url = "https://www.nasdaq.com/market-activity/stocks/%s" % quote.lower()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Todo


    except Exception as e:
        print ("DEBUG: get_quote_from_nasdaq get quote failed...")
        print (e)
    return equity_data

def get_quote_from_market_beats(market, quote):
    """
       quote: AAPL 
       return: equity_data dict{}
            {'': u'198.23',
             u'52 Wk Low': u'124.17',
             u'Avg. Volume': u'47,877,228',
             u'Beta': u'1.28',
             u'Day High': u'196.63',
             u'Day Low': u'194.14',
             u'Dividend': u'0.96 ( 0.49%)',
             u'Market Cap': u'3,080.15 B',
             u'Open': u'194.67',
             'change': u'+2.61 (1.35%)',
             'previous_close': u'$195.83 USD',
             'quote': 'AAPL',
             'timestamp': u'Jul 28, 2023 04:00 PM'} 
    """
    equity_data = {}
    equity_data["quote"] = quote
    try:
        if market is None or quote is None:
            return equity_data
        # url = "https://www.zacks.com/stock/quote/%s" % quote.lower()
        url = "https://www.marketbeat.com/stocks/%s/%s" % (market.upper(), quote.upper())
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        quote_summary_list = soup.select('div[class="row price-info"]')
        if len(quote_summary_list) > 0:
            quote_summary = quote_summary_list[0]

            avg_price = quote_summary.select('strong')[0].text if len(quote_summary.select('strong')) > 0 else ""
            last_price = avg_price
            # previous close
            equity_data["avg_price"] = avg_price
            equity_data["previous_close"] = last_price
            # change
            change_div_list = quote_summary.select('div[class="d-inline-block"]')[0] if len(quote_summary.select('div[class="d-inline-block"]')) > 0 else None
            if change_div_list is not None:
                span_price_change = change_div_list.select("span")[0].text if len(change_div_list.select("span")) > 0 else ""
                span_price_change = span_price_change.replace('\xa0', "")
                span_price_change = span_price_change.strip()
                equity_data["change"] = span_price_change
                timestamp = change_div_list.select('div[class="price-updated"]')[0].text if len(change_div_list.select('div[class="price-updated"]')) > 0 else ""
                equity_data["timestamp"] = timestamp

        # Stock Activity
        stock_activity_section_list = soup.select('div[id="price-data-lower"]')
        stock_activity_section = stock_activity_section_list[0] if len(stock_activity_section_list) > 0 else None
        if stock_activity_section is not None:
            dl_list = stock_activity_section.select('div[class="price-data w-range"]')
            dl_list_2 = stock_activity_section.select('div[class="price-data"]')
            dl_list += dl_list_2
            for data_line in dl_list:
                dt_alpha = data_line.select('dt')[0] if len(data_line.select('dt')) > 0 else None
                dd_value = data_line.select('dd')[0] if len(data_line.select('dd')[0]) > 0 else None
                tag_extract = [tag.extract() for tag in dd_value.select('div[class="range"]')]
                key = dt_alpha.text if dt_alpha is not None else ""
                value = dd_value.text if dd_value is not None else ""
                # 150.0 -> $ 150.0
                equity_data[key] = value
                if key in ["Today's Range"]:
                    value_list = value.split("$")
                    if len(value_list) == 3:
                        day_low = value_list[1]
                        day_high = value_list[2]
                        equity_data["Day High"] = day_high
                        equity_data["Day Low"] = day_low
        ## Add returning source 
        equity_data["source"] = RESPONSE_SOURCE_STOCK_PRICE_US_MARKET_BEATS % url
        equity_data[KEY_DATA_SOURCE] = DATA_SOURCE_MARKET_BEATS
        equity_data[KEY_SOURCE_URL] = url
    except Exception as e:
        print ("DEBUG: get_quote_from_market_beats get quote failed...")
        print (e)
    if len(equity_data) <= 1:
        return None
    return row_mapper_market_beats(equity_data)


### API to get Quote From Zacks.com (Depreciated)
def get_quote_from_zacks(quote):
    """
       quote: AAPL 
       return: equity_data dict{}
            {'': u'198.23',
             u'52 Wk Low': u'124.17',
             u'Avg. Volume': u'47,877,228',
             u'Beta': u'1.28',
             u'Day High': u'196.63',
             u'Day Low': u'194.14',
             u'Dividend': u'0.96 ( 0.49%)',
             u'Market Cap': u'3,080.15 B',
             u'Open': u'194.67',
             'change': u'+2.61 (1.35%)',
             'previous_close': u'$195.83 USD',
             'quote': 'AAPL',
             'timestamp': u'Jul 28, 2023 04:00 PM'} 
    """
    equity_data = {}
    equity_data["quote"] = quote
    try:
        url = "https://www.zacks.com/stock/quote/%s" % quote.lower()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        quote_summary_list = soup.select('div[class="quote_summary"]')
        if len(quote_summary_list) > 0:
            quote_summary = quote_summary_list[0]
            last_price_p = quote_summary.select('p[class="last_price"]')
            last_price = last_price_p[0].text if len(last_price_p) > 0 else ""
            # previous close
            equity_data["previous_close"] = last_price
            # change
            change_div_list = quote_summary.select('div[class="change"]')
            change_value = change_div_list[0].text.strip() if len(change_div_list) > 0 else ""
            equity_data["change"] = ("$" + change_value) if "$" not in change_value else change_value
            # timestamp
            timestamp_list = quote_summary.select('span[id="timestamp"]')
            timestamp = timestamp_list[0].text if len(timestamp_list) > 0 else ""
            equity_data["timestamp"] = timestamp
        # Stock Activity
        stock_activity_section_list = soup.select('section[id="stock_activity"]')
        stock_activity_section = stock_activity_section_list[0] if len(stock_activity_section_list) > 0 else None
        if stock_activity_section is not None:
            dl_list = stock_activity_section.select('dl[class="abut_bottom"]')
            for data_line in dl_list:
                dt_alpha = data_line.select('dt[class="alpha"]')[0] if len(data_line.select('dt[class="alpha"]')) > 0 else None
                dd_value = data_line.select('dd')[0] if len(data_line.select('dd')[0]) > 0 else None
                key = dt_alpha.text if dt_alpha is not None else ""
                value = dd_value.text if dd_value is not None else ""
                # 150.0 -> $ 150.0
                if key in ["Day High", "Day Low", "change", "Market Cap"]:
                    if "$" not in value:
                        value = "$" + value
                equity_data[key] = value
        # Stock Activity
        stock_earning_section_list = soup.select('section[id="stock_key_earnings"]')
        stock_earning_section = stock_earning_section_list[0] if len(stock_earning_section_list) > 0 else None
        if stock_earning_section is not None:
            dl_list = stock_earning_section.select('dl[class="abut_bottom"]')
            for data_line in dl_list:
                dt_alpha = data_line.select('dt[class="alpha"]')[0] if len(data_line.select('dt[class="alpha"]')) > 0 else None
                dd_value = data_line.select('dd')[0] if len(data_line.select('dd')[0]) > 0 else None
                key = dt_alpha.text if dt_alpha is not None else ""
                value = dd_value.text if dd_value is not None else ""
                # 150.0 -> $ 150.0
                if key in ["Forward PE"]:
                        value = value
                equity_data[key] = value
        ## Add returning source 
        equity_data["source"] = RESPONSE_SOURCE_STOCK_PRICE_US_ZACKS % quote.lower()
        equity_data[KEY_DATA_SOURCE] = DATA_SOURCE_ZACKS
        equity_data[KEY_SOURCE_URL] = RESPONSE_SOURCE_STOCK_PRICE_US_ZACKS_URL % quote.lower()

    except Exception as e:
        print ("DEBUG: get_quote_from_zacks get quote failed...")
        print (e)
    if len(equity_data) <= 1:
        return None
    return row_mapper_zacks(equity_data)


### API to Get Stock Advice of Target Price
def request_stock_advice_parrallel_base(args):
    """ 
        args list of tuples
        1. source: "market_beats"
        2. symbol: "AAPL"

        Return: list of json
    """
    try:
        if len(args) >= 4:
            # source = args[0]
            # symbol = args[1]
            print ("DEBUG: request_stock_advice_parrallel_base input args|%s" % str(args))
            source, symbol, market, sub_market = args
            if source == DATA_SOURCE_MARKET_BEATS:
                return [get_stock_recommendation_from_market_beats(symbol, sub_market)]
            elif source == DATA_SOURCE_ZACKS:
                return [get_stock_recommendation_from_zacks(symbol, sub_market)]
            elif source == DATA_SOURCE_STOCK_ANALYSIS:
                return [get_stock_recommendation_from_stock_analysis(symbol, sub_market)]
            else:
                print ("DEBUG: DATA_SOURCE not Supported %s..." % source)
                return []
        else:
            return []
    except Exception as e:
        print ("DEBUG: DATA_SOURCE error, args %s ..." % str(args))        
        print (e)
        return []

def get_stock_recommendation_from_market_beats(quote, sub_market):

    quote_upper = quote.upper()
    sub_market_upper = sub_market.upper()
    try:
        url = "https://www.marketbeat.com/stocks/%s/%s/price-target/" % (sub_market_upper, quote_upper)
        print ("DEBUG: get_stock_recommendation_from_market_beats url|%s" % url)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')


        quote_forecast_table_list = soup.select('table[id="consensus-table"]')
        quote_forecast_table = quote_forecast_table_list[0] if len(quote_forecast_table_list) > 0 else None 
        if quote_forecast_table is None:
            return {}
        th_list = quote_forecast_table.select('th')
        tr_list = quote_forecast_table.select('tr')
        header_values = []
        for (i, th) in enumerate(th_list):
            header_values.append(th.text)

        table_values = []
        for tr in tr_list:
            td_list =tr.select('td')
            td_value_list = []
            for td in td_list:
                value =td.text
                td_value_list.append(value)
            ## row
            table_values.append(td_value_list)
        # print (table_values)
        ncol = len(header_values)

        output_values = []
        header_value = header_values[1] if len(header_values) > 1 else ""
        output_values.append(header_value)
        for values in table_values:
            value = values[0] + ": " + values[1] if len(values) > 2 else ""
            if value != "":
                output_values.append(value)

        ## table_json
        output_json = {}
        output_value_line = SEPARATOR_COMMA_SPACE.join(output_values)
        output_json[KEY_ADVICE] = output_value_line
        output_json[KEY_DATA_SOURCE] = DATA_SOURCE_MARKET_BEATS
        output_json[KEY_SYMBOL] = quote
        output_json[KEY_SOURCE_URL] = url
        # print ("DEBUG: get_stock_recommendation_from_market_beats output_json|%s" % str(output_json))

        return output_json
    except Exception as e:
        print ("DEBUG: get_stock_recommendation_from_market_beats error...")
        print (e)
        return {}


def get_stock_recommendation_from_zacks(quote, sub_market):

    quote_upper = quote.upper()
    sub_market_upper = sub_market.upper()
    try:
        url = "https://www.zacks.com/stock/research/%s/price-target-stock-forecast" % (quote_upper)
        print ("DEBUG: get_stock_recommendation_from_zacks url|%s" % url)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        target_forecast = soup.select("div[class='target-text-box']")[0].select("p")[0].text if len(soup.select("div[class='target-text-box']")) > 0 else ""
        broker_rating = soup.select("div[class='broker-text-box']")[0].select("p")[0].text if len(soup.select("div[class='broker-text-box']")) > 0 else ""

        output_value_line = target_forecast + "\n" + broker_rating

        output_json = {}
        output_json[KEY_ADVICE] = output_value_line
        output_json[KEY_DATA_SOURCE] = DATA_SOURCE_ZACKS
        output_json[KEY_SYMBOL] = quote
        output_json[KEY_SOURCE_URL] = url
        return output_json
    except Exception as e:
        print ("DEBUG: get_stock_recommendation_from_zacks error...")
        print (e)
        return {}


def get_stock_recommendation_from_stock_analysis(quote, sub_market):

    quote_lower = quote.lower()
    try:
        url = "https://stockanalysis.com/stocks/%s/forecast/" % (quote_lower)
        print ("DEBUG: get_stock_recommendation_from_stock_analysis url|%s" % url)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
        # house = 'https://www.hkex.com.hk/?sc_lang=EN'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        target_forecast = soup.select("div[data-test='forecast-snippet']")[0].select("p")[0].text if len(soup.select("div[data-test='forecast-snippet']")) > 0 else ""
        broker_rating = soup.select("p[data-test='forecast-ratings-snippet']")[0].text if len(soup.select("p[data-test='forecast-ratings-snippet']")) > 0 else ""

        output_value_line = target_forecast + "\n" + broker_rating

        output_json = {}
        output_json[KEY_ADVICE] = output_value_line
        output_json[KEY_DATA_SOURCE] = DATA_SOURCE_STOCK_ANALYSIS
        output_json[KEY_SYMBOL] = quote
        output_json[KEY_SOURCE_URL] = url
        return output_json
    except Exception as e:
        print ("DEBUG: get_stock_recommendation_from_stock_analysis error...")
        print (e)
        return {}

def row_mapper_zacks(entity_data):
    if entity_data is None:
        return None
    result_dict = {}
    avg_price = entity_data["avg_price"] if "avg_price" in entity_data else ""
    previous_close = entity_data["previous_close"] if "previous_close" in entity_data else ""
    update_time_str = entity_data["timestamp"] if "timestamp" in entity_data else ""     # 'update_time': u '2023-07-22 23:52:08.0'

    # When market is close, use previous_close price and set to average price
    if avg_price == "":
        avg_price = previous_close

    # row mapper
    result_dict["avg_price"] = avg_price
    result_dict["high"] = entity_data["Day High"] if "Day High" in entity_data else ""
    result_dict["low"] = entity_data["Day Low"] if "Day Low" in entity_data else ""
    result_dict["symbol"] = entity_data["quote"]  if "quote" in  entity_data else ""         
    result_dict["timestamp"] = update_time_str   # 'update_time': u '2023-07-22 23:52:08'
    result_dict["previous_close"] = previous_close
    result_dict["update_time"] = update_time_str
    result_dict["change"] = entity_data["change"] if "change" in  entity_data else ""  
    result_dict["source"] = entity_data["source"] if "change" in  entity_data else ""      
    result_dict["market_capitalization"] = entity_data["Market Cap"] if "Market Cap" in  entity_data else ""      
    result_dict["pe_ratio"] = entity_data["Forward PE"] if "Forward PE" in  entity_data else ""
    for key in ["avg_price", "high", "low", "previous_close", "market_capitalization"]:
        value = result_dict[key] if key in result_dict else ""
        value_str = str(value)
        if UNIT_USD not in value_str:
            value_str = value_str + " " + UNIT_USD
            result_dict[key] = value_str
        else:
            result_dict[key] = value_str                 
    result_dict[KEY_DATA_SOURCE] = entity_data[KEY_DATA_SOURCE] if KEY_DATA_SOURCE in  entity_data else ""   
    result_dict[KEY_SOURCE_URL] = entity_data[KEY_SOURCE_URL] if KEY_SOURCE_URL in  entity_data else ""   
    return result_dict

def row_mapper_market_beats(entity_data):
    if entity_data is None:
        return None
    result_dict = {}
    avg_price = entity_data["avg_price"] if "avg_price" in entity_data else ""
    previous_close = entity_data["previous_close"] if "previous_close" in entity_data else ""
    update_time_str = entity_data["timestamp"] if "timestamp" in entity_data else ""     # 'update_time': u '2023-07-22 23:52:08.0'
    
    if avg_price == "":
        avg_price = previous_close
    # row mapper
    result_dict["avg_price"] = avg_price
    result_dict["high"] = entity_data["Day High"] if "Day High" in entity_data else ""
    result_dict["low"] = entity_data["Day Low"] if "Day Low" in entity_data else ""
    result_dict["symbol"] = entity_data["quote"]  if "quote" in  entity_data else ""          # AAPL
    result_dict["timestamp"] = update_time_str   # 'update_time': u '2023-07-22 23:52:08'
    result_dict["previous_close"] = previous_close
    result_dict["update_time"] = update_time_str
    result_dict["change"] = entity_data["change"] if "change" in  entity_data else ""  
    result_dict["source"] = entity_data["source"] if "change" in  entity_data else ""      
    result_dict["market_capitalization"] = entity_data["Market Capitalization"] if "Market Capitalization" in  entity_data else ""      
    result_dict["pe_ratio"] = entity_data["P/E Ratio"] if "P/E Ratio" in  entity_data else ""      

    for key in ["avg_price", "high", "low", "previous_close", "market_capitalization"]:
        value = result_dict[key] if key in result_dict else ""
        value_str = str(value)
        if UNIT_USD not in value_str:
            value_str = value_str + " " + UNIT_USD
            result_dict[key] = value_str
        else:
            result_dict[key] = value_str 
    result_dict[KEY_DATA_SOURCE] = entity_data[KEY_DATA_SOURCE] if KEY_DATA_SOURCE in  entity_data else ""   
    result_dict[KEY_SOURCE_URL] = entity_data[KEY_SOURCE_URL] if KEY_SOURCE_URL in  entity_data else ""   
    return result_dict

def test_request_us_quote():
    symbol_list = ['BILI', 'AAPL', 'BABA', 'KAKAB']
    results = request_us_quote(symbol_list, None, None)
    print (results)

def main():

    results_dict = get_quote_from_morningstar("MSFT")
    print ("DEBUG: Apple stock price from Morningstar.com is %s" % str(results_dict))

    results_dict = get_quote_from_zacks("AAPL")
    print ("DEBUG: Apple stock price from Zacks is %s" % str(results_dict))

    result_dict = get_quote_from_market_beats("NASDAQ", "AAPL")
    print ("DEBUG: Apple stock price from market beats is %s" % str(result_dict))

if __name__ == '__main__':
    main()
