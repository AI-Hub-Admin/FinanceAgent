# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import FinanceAgent as fa
import json

def test_fetch_global_stock_market():

    ## Hongkong Stock Exchange Tencent: 700, Kuaishou: 1024
    hk_stock_info_json = fa.api(symbol_list=['700', '1024'], market="HK")

    ## Shanghai and Shenzhen Stock Market: SH600519: 贵州茅台(Maotai), SH600036: 招商银行 (China Merchants Bank)
    cn_stock_info_json = fa.api(symbol_list=['SH600519', 'SH600036'], market="CN_MAINLAND")

    ## UK Market: London Stock Exchange Market
    lse_stock_info_json = fa.api(symbol_list=['SHEL', 'ULVR'], market="LSE")

    ## India NSE National Stock Exchange, Tata Motor(TM03), Infosys(IT)
    india_stock_info_json = fa.api(symbol_list=['TM03', 'IT'], market="NSE_INDIA")

    ## US Stock Market
    us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT'], market="US")

    ## output report
    keys = ["symbol", "avg_price", "high", "low", "previous_close", "update_time", "market_capitalization", "pe_ratio", "source_url", "data_source"]    
    print ("#### HK Stock Info")
    for stock_info in hk_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)
    print ("-----------------------------------")

    print ("#### CN MAINLAND Stock Info")
    for stock_info in cn_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)
    print ("-----------------------------------")

    print ("#### London Stock Exchange LSE")
    for stock_info in lse_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)
    print ("-----------------------------------")

    print ("#### US Stock Info")
    for stock_info in us_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)
    print ("-----------------------------------")

    print ("#### India Stock Market Info")
    for stock_info in india_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)
    print ("-----------------------------------")

def test_us_stock_api():

    # us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT', 'GOOG'], market="US")

    keys = ["symbol", "avg_price", "high", "low", "previous_close", "update_time", "market_capitalization", "pe_ratio", "source", "data_source"]    
    
    ## UK Market: London Stock Exchange Market
    us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT'], market="US")
    print ("#### US Stock Exchange LSE")
    for stock_info in us_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)

def test_hk_stock_api():
    # us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT', 'GOOG'], market="US")
    keys = ["symbol", "avg_price", "high", "low", "previous_close", "update_time", "market_capitalization", "pe_ratio", "source_url", "data_source"]    
    
    ## UK Market: London Stock Exchange Market
    hk_stock_info_json = fa.api(symbol_list=['700', '1024'], market="HK")
    print ("#### HongKong Stock Exchange LSE")
    for stock_info in hk_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)

def test_cn_stock_api():

    # us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT', 'GOOG'], market="US")

    keys = ["symbol", "avg_price", "high", "low", "previous_close", "update_time", "market_capitalization", "pe_ratio", "source_url", "data_source"]    
    
    cn_stock_info_json = fa.api(symbol_list=['SH600519', 'SH600036'], market="CN_MAINLAND")
    print ("#### CN Shanghai and Shenzhen Stock Exchange LSE")
    for stock_info in cn_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)

def test_lse_stock_api():

    # us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT', 'GOOG'], market="US")

    keys = ["symbol", "avg_price", "high", "low", "previous_close", "update_time", "market_capitalization", "pe_ratio", "source_url", "data_source"]    
    
    lse_stock_info_json = fa.api(symbol_list=['SHEL', 'ULVR'], market="LSE")
    print ("#### LSE  Stock Exchange LSE")
    for stock_info in lse_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)

def test_india_stock_api():

    # us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT', 'GOOG'], market="US")

    keys = ["symbol", "avg_price", "high", "low", "previous_close", "update_time", "market_capitalization", "pe_ratio", "source_url", "data_source"]    
    
    india_stock_info_json = fa.api(symbol_list=['TM03', 'IT'], market="NSE_INDIA")
    print ("#### India NSE Stock Info")
    for stock_info in india_stock_info_json:
        print ("-----------------------------------")
        for key in keys:
            value = stock_info[key] if key in stock_info else ""
            print (key + "|" + value)

def main():
	test_fetch_global_stock_market()

if __name__ == '__main__':
	main()
