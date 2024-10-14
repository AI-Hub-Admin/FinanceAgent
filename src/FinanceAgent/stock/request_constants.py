#coding=utf-8
#!/usr/bin/python

## Stock Market
STOCK_MARKET_US = "US"
STOCK_MARKET_CN = "CN_MAINLAND"
STOCK_MARKET_HK = "HK"
STOCK_MARKET_LSE = "LSE"
STOCK_MARKET_NSE_INDIA = "NSE_INDIA"

STOCK_SUB_MARKET_NYSE = "NYSE"
STOCK_SUB_MARKET_NASDAQ = "NASDAQ"
STOCK_SUB_MARKET_DOW = "DOW"

## API NAME LIST
API_NAME_FINANCE_DATA_PARALLEL = "finance_data_parallel"

## API Input Dict Keys
KEY_TOKEN = "token"
KEY_SYMBOL_LIST = "symbol_list"
KEY_MARKET = "market"
KEY_SUB_MARKET = "sub_market"
KEY_DATA_SOURCE_LIST = "data_source_list"

## API Output Dict Keys
KEY_SYMBOL = "symbol"
KEY_TIMESTAMP = "timestamp"
KEY_UPDATE_TIME = "update_time"
KEY_PE_RATIO = "pe_ratio"
KEY_AVG_PRICE = "avg_price"
KEY_CHANGE = "change"
KEY_CHANGE_PERCENT = "change_percent"
KEY_HIGH_PRICE = "high"
KEY_LOW_PRICE = "low"
KEY_PREVIOUS_CLOSE= "previous_close"
KEY_LAST_PRICE = "last_price"
KEY_ADVICE = "advice"
KEY_DATA_SOURCE = "data_source"
KEY_SOURCE_URL = "source_url"
KEY_SOURCE = "source"
KEY_SYMBOL_AND_NAME = "symbol_and_name"
KEY_SYMBOL_NAME_DISPLAY = "symbol_name_display"
KEY_MARKET_CAP = "market_capitalization"
KEY_SYMBOL_HK = "symbol_hk"
KEY_SYMBOL_NAME_HK = "symbol_name_hk"
KEY_COMPANY_NAME = "company_name"
KEY_INDUSTRY = "industry"

## DATA SOURCE
DATA_SOURCE_MARKET_BEATS = "Market Beats"
DATA_SOURCE_ZACKS = "zacks.com"
DATA_SOURCE_STOCK_ANALYSIS = "stockanalysis.com"
DATA_SOURCE_HKEX = "hkex.com"
DATA_SOURCE_XUEQIU = "xueqiu.com"
DATA_SOURCE_MORNING_STAR = "morningstar.com"
DATA_SOURCE_LSE = "londonstockexchange.com"
DATA_SOURCE_MONEY_CONTROL = "moneycontrol.com"

## DATA SOURCE RESPONSE
RESPONSE_SOURCE_STOCK_PRICE_HKEX = "HKEX, https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=%s&sc_lang=en"
RESPONSE_SOURCE_STOCK_PRICE_XUEQIU = "XUEQIU.COM, https://xueqiu.com/S/%s"
RESPONSE_SOURCE_STOCK_PRICE_US_ZACKS = "ZACKS.COM, https://www.zacks.com/stock/quote/%s"
RESPONSE_SOURCE_STOCK_PRICE_US_MARKET_BEATS = "marketbeat.com, %s"

RESPONSE_SOURCE_STOCK_PRICE_HKEX_URL = "https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=%s&sc_lang=en"
RESPONSE_SOURCE_STOCK_PRICE_XUEQIU_URL = "https://xueqiu.com/S/%s"
RESPONSE_SOURCE_STOCK_PRICE_US_ZACKS_URL = "https://www.zacks.com/stock/quote/%s"
RESPONSE_SOURCE_STOCK_PRICE_US_MARKET_BEATS_URL = "%s"

## URL
DATA_SOURCE_STOCK_ANALYSIS_LSE_URL = "https://stockanalysis.com/quote/lon/"
DATA_SOURCE_MORNING_STAR_URL = "https://www.morningstar.com/markets"

## Currency
UNIT_HKD = "HKD"
UNIT_CNY = "CNY"
UNIT_GBP = "GBP"
UNIT_INR = "INR"
UNIT_USD = "USD"
UNIT_INR = "INR"
UNIT_CNY_ZH = "元"

UNIT_BILLION = "billion"
UNIT_MILLION = "million"

UNIT_BILLION_SHORT = "b"
UNIT_MILLION_SHORT = "m"
UNIT_ONE_IN_TEN_B_CNY = "亿"
UNIT_TEN_THOUSAND_CNY = "万"
UNIT_INR_CR = "Cr."

### HKEX Constants
HKEX_TENCENT_STOCK_URL = "https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=700&sc_lang=en"
HKEX_QUOTE_BASE_URL = "https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym=%s&token=%s&lang=eng&qid=%s&callback=%s"
HKEX_JQUERY_PREFIX = "jQuery35103797027038824472_"


### India Stock Market 

INDIA_NSE_STOCK_URL_MONEY_CONTROL = "https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=9"
INDIA_NSE_STOCK_URL_MONEY_CONTROL_BASE = "https://www.moneycontrol.com"


### CN

CN_STOCK_URL_XUEQIU = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol="


### US Stock

MINUS_SIGN = "-"
