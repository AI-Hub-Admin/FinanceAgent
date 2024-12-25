# FinanceAgent package

This is the official github repo of pypi package FinanceAgent(https://pypi.org/project/FinanceAgent/). This repo is intended to provide common financial API interface
to help develop Finance related AI Agents workflows. Since getting realtime or near-realtime finance data is crucial for success of AI Agents, 
we are building a common interface of open API to get public available data from glocal Finance Market (US, Europe, Asia) with multiple finance investment choices such as Stock, Index, Option, etc.
Getting Realtime Data maybe blocked by website and this repo is not responsible for proxy or any data correctness related issues.



*** IMPORTANT LEGAL DISCLAIMER ***

FinanceAgent is not affiliated, endorsed, or vetted by Financial Institutions. It's an open-source tool that uses finance APIs to get realtime finance data to help build 
AI Agents and Finance Larget Language Models. Please contact the repo owner email if your API or data source need to be removed from the repo.



|  REGION  | MARKET| INVESTMENT TYPE | API DATA SOURCE   |
|  ----  | ----  | ----  | ----  | 
|  United Status  | US (NASDAQ,NYSE,DOW) | STOCK  | morningstar.com |
|  United Status  | US (NASDAQ,NYSE,DOW)  | STOCK  | zacks.com |
|  United Status  | US (NASDAQ,NYSE,DOW)  | STOCK  | marketbeat.com |
|  Asia  | HK (HKEX) | STOCK  | hkex.com |
|  Asia  | CN_MAINLAND (SHANGHAI SH, SHENZHEN SZ) | STOCK  | xueqiu.com |
|  Asia  | India (NSE) | STOCK  |  moneycontrol.com  |
|  Europe  | London (LSE) | STOCK  | stockanalysis.com |
|  Asia  | Toyko (TSE) | STOCK  | NA |


## Install
```
pip install FinanceAgent
```


## Usage
```
import FinanceAgent as fa

## Hongkong Stock Exchange Tencent: 700, Kuaishou: 1024
hk_stock_info_json = fa.api(symbol_list=['700', '1024'], market="HK")

## Shanghai and Shenzhen Stock Market: SH600519: 贵州茅台(Maotai), SH600036: 招商银行 (China Merchants Bank)
cn_stock_info_json = fa.api(symbol_list=['SH600519', 'SH600036'], market="CN_MAINLAND")

## US Stock Market: Tesla (TSLA), Microsoft(MSFT), Google (GOOG)
us_stock_info_json = fa.api(symbol_list=['TSLA', 'MSFT', 'GOOG'], market="US")

## UK Stock Market: London Stock Exchange Market, Shell (quote: SHEL), Unilever (quote: ULVR)
lse_stock_info_json = fa.api(symbol_list=['SHEL', 'ULVR'], market="LSE")

## India NSE National Stock Exchange, Tata Motor(TM03), Infosys(IT)
india_stock_info_json = fa.api(symbol_list=['TM03', 'IT'], market="NSE_INDIA")


```


## Sample Output
```

#### HK Stock Info
-----------------------------------
symbol|1024
avg_price|49.650 HKD
high|50.950 HKD
low|47.600 HKD
previous_close|50.850 HKD
update_time|14 Oct 2024 18:33
market_capitalization|214.06 B HKD
pe_ratio|31.15
source|HKEX, https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=1024&sc_lang=en
data_source|hkex.com
-----------------------------------
symbol|700
avg_price|436.000 HKD
high|440.800 HKD
low|424.000 HKD
previous_close|438.800 HKD
update_time|14 Oct 2024 18:33
market_capitalization|4,045.91 B HKD
pe_ratio|33.32
source|HKEX, https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=700&sc_lang=en
data_source|hkex.com
-----------------------------------


#### CN MAINLAND Stock Info
-----------------------------------
symbol|SH600036
avg_price|39.265919080336076 CNY
high|39.8 CNY
low|38.69 CNY
previous_close|38.43 CNY
update_time|2024-10-14 15:00:00
market_capitalization|9918.97 亿 CNY
pe_ratio|
source|XUEQIU.COM, https://xueqiu.com/S/SH600036
data_source|xueqiu.com
-----------------------------------

symbol|SH600519
avg_price|1602.5501242724608 CNY
high|1620.63 CNY
low|1581.17 CNY
previous_close|1604.99 CNY
update_time|2024-10-14 15:00:00
market_capitalization|20124.16 亿 CNY
pe_ratio|
source|XUEQIU.COM, https://xueqiu.com/S/SH600519
data_source|xueqiu.com
-----------------------------------

#### London Stock Exchange LSE
-----------------------------------

symbol|SHEL
avg_price|2,592.00 GBP
high|2,599.29 GBP
low|2,577.50 GBP
previous_close|2,592.00 GBP
update_time|
market_capitalization|161.18B GBP
pe_ratio|11.70
source|stockanalysis.com,https://stockanalysis.com/quote/lon/SHEL
data_source|stockanalysis.com
-----------------------------------

symbol|ULVR
avg_price|4,806.00 GBP
high|4,827.00 GBP
low|4,792.00 GBP
previous_close|4,806.00 GBP
update_time|
market_capitalization|119.19B GBP
pe_ratio|21.57
source|stockanalysis.com,https://stockanalysis.com/quote/lon/ULVR
data_source|stockanalysis.com
-----------------------------------

#### US Stock Info
-----------------------------------
symbol|TSLA
avg_price|217.80 USD
high|223.34 USD
low|214.38 USD
previous_close|238.77 USD
update_time|
market_capitalization|695.79 Bil USD
pe_ratio|87.78
source|
data_source|morningstar.com
-----------------------------------

#### India Stock Market Info
-----------------------------------
symbol|IT
avg_price|1,958.70 INR
high|1,958.70 INR
low|1,958.70 INR
previous_close|1,958.70 INR
update_time|
market_capitalization|813,281.00 INR
pe_ratio|
source|moneycontrol.com,https://www.moneycontrol.comhttps://www.moneycontrol.com/india/stockpricequote/computers-software/infosys/IT
data_source|moneycontrol.com
-----------------------------------
symbol|TM03
avg_price|928.05 INR
high|928.05 INR
low|928.05 INR
previous_close|928.05 INR
update_time|
market_capitalization|341,604.45 INR
pe_ratio|
source|moneycontrol.com,https://www.moneycontrol.comhttps://www.moneycontrol.com/india/stockpricequote/auto-lcvs-hcvs/tatamotors/TM03
data_source|moneycontrol.com
-----------------------------------



```


## Introduction to Available API and Data Source 
** note: Stock Data Displayed on Page Might not be stable


|  REGION  | MARKET| DATA SOURCE   |  API Example |  Robots Verification  |
|  ----  | ----  | ----  | ----  | ----  | 
|  United Status  | US | morningstar.com |  https://www.morningstar.com/stocks/xnas/aapl/quote | YES |
|  United Status  | US | zacks.com |  https://www.zacks.com/stock/quote/aapl | YES |
|  United Status  | US | marketbeat.com |  https://www.marketbeat.com/stocks/NASDAQ/AAPL | YES |
|  Asia  | HK (HKEX)  | hkex.com | https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym=700&sc_lang=en | YES |
|  Asia  | CN_MAINLAND(SH and SHENZHEN) | xueqiu.com | https://xueqiu.com/S/SH600519 | YES |
|  Asia  | India (NSE) | https://www.moneycontrol.com | https://www.moneycontrol.com/india/stockpricequote/auto-lcvshcvs/tatamotors/TM03 | YES |
|  Asia  | Japan (TSE) |   xxx |  |  |
|  Europe  | London (LSE) | stockanalysis.com | https://stockanalysis.com/stocks/shel/ | YES |



## Related Blogs
[Introduction to multimodal generative models](http://www.deepnlp.org/blog/introduction-to-multimodal-generative-models) <br>
[Generative AI Search Engine Optimization](http://www.deepnlp.org/blog/generative-ai-search-engine-optimization-how-to-improve-your-content) <br>
[AI Image Generator User Reviews](http://www.deepnlp.org/store/image-generator) <br>
[AI Video Generator User Reviews](http://www.deepnlp.org/store/video-generator) <br>
[AI Chatbot & Assistant Reviews](http://www.deepnlp.org/store/chatbot-assistant) <br>
[AI Store-Best AI Tools User Reviews](http://www.deepnlp.org/store/pub/) <br>
[AI Store Use Cases-Best AI Tools Cases User Reviews](http://www.deepnlp.org/store) <br>
[4 ways to use ChatGPT Stock Chatbot for stock analysis of Global Stock Markets NASDAQ NYSE LSE HKEX TSE NSE SHANGHAI SHENZHEN](http://www.deepnlp.org/blog/chatgpt-stock-global-market) <br>
[How to write a Financial Chatbot First Part 3 steps to crawl Hong Kong Stock Market (HKEX) realtime stock quotes](http://www.deepnlp.org/blog/fin-chatbot-first-spider-hkex) <br>
[3 steps to create Financial Chatbot powered by ChatGPT Part 1](http://www.deepnlp.org/blog/financial-chatbot-chatgpt-1) <br>

## AI Services Reviews and Ratings <br>
##### AI Agent Marketplace and Search
[AI Agent Marketplace and Search](http://www.deepnlp.org/search/agent) <br>
[Robot Search](http://www.deepnlp.org/search/robot) <br>
[Equation and Academic search](http://www.deepnlp.org/search/equation) <br>
[AI & Robot Comprehensive Search](http://www.deepnlp.org/search) <br>
[AI & Robot Question](http://www.deepnlp.org/question) <br>
[AI & Robot Community](http://www.deepnlp.org/community) <br>
[AI Agent Marketplace Blog](http://www.deepnlp.org/blog/ai-agent-marketplace-and-search-portal-reviews-2025) <br>
##### Reasoning
[OpenAI o1 Reviews](http://www.deepnlp.org/store/pub/pub-openai-o1) <br>
[OpenAI o3 Reviews](http://www.deepnlp.org/store/pub/pub-openai-o3) <br>
##### Chatbot
[ChatGPT User Reviews](http://www.deepnlp.org/store/pub/pub-chatgpt-openai) <br>
[Gemini User Reviews](http://www.deepnlp.org/store/pub/pub-gemini-google) <br>
[Perplexity User Reviews](http://www.deepnlp.org/store/pub/pub-perplexity) <br>
[Claude User Reviews](http://www.deepnlp.org/store/pub/pub-claude-anthropic) <br>
[Qwen AI Reviews](http://www.deepnlp.org/store/pub/pub-qwen-alibaba) <br>
[Doubao Reviews](http://www.deepnlp.org/store/pub/pub-doubao-douyin) <br>
[ChatGPT Strawberry](http://www.deepnlp.org/store/pub/pub-chatgpt-strawberry) <br>
[Zhipu AI Reviews](http://www.deepnlp.org/store/pub/pub-zhipu-ai) <br>
##### AI Image Generation
[Midjourney User Reviews](http://www.deepnlp.org/store/pub/pub-midjourney) <br>
[Stable Diffusion User Reviews](http://www.deepnlp.org/store/pub/pub-stable-diffusion) <br>
[Runway User Reviews](http://www.deepnlp.org/store/pub/pub-runway) <br>
[GPT-5 Forecast](http://www.deepnlp.org/store/pub/pub-gpt-5) <br>
[Flux AI Reviews](http://www.deepnlp.org/store/pub/pub-flux-1-black-forest-lab) <br>
[Canva User Reviews](http://www.deepnlp.org/store/pub/pub-canva) <br>
##### AI Video Generation
[Luma AI](http://www.deepnlp.org/store/pub/pub-luma-ai) <br>
[Pika AI Reviews](http://www.deepnlp.org/store/pub/pub-pika) <br>
[Runway AI Reviews](http://www.deepnlp.org/store/pub/pub-runway) <br>
[Kling AI Reviews](http://www.deepnlp.org/store/pub/pub-kling-kwai) <br>
[Dreamina AI Reviews](http://www.deepnlp.org/store/pub/pub-dreamina-douyin) <br>
##### AI Education
[Coursera Reviews](http://www.deepnlp.org/store/pub/pub-coursera) <br>
[Udacity Reviews](http://www.deepnlp.org/store/pub/pub-udacity) <br>
[Grammarly Reviews](http://www.deepnlp.org/store/pub/pub-grammarly) <br>
##### Robotics
[Tesla Cybercab Robotaxi](http://www.deepnlp.org/store/pub/pub-tesla-cybercab) <br>
[Tesla Optimus](http://www.deepnlp.org/store/pub/pub-tesla-optimus) <br>
[Figure AI](http://www.deepnlp.org/store/pub/pub-figure-ai) <br>
[Unitree Robotics Reviews](http://www.deepnlp.org/store/pub/pub-unitree-robotics) <br>
[Waymo User Reviews](http://www.deepnlp.org/store/pub/pub-waymo-google) <br>
[ANYbotics Reviews](http://www.deepnlp.org/store/pub/pub-anybotics) <br>
[Boston Dynamics](http://www.deepnlp.org/store/pub/pub-boston-dynamic) <br>
##### AI Tools
[DeepNLP AI Tools](http://www.deepnlp.org/store/pub/pub-deepnlp-ai) <br>
##### AI Widgets
[Apple Glasses](http://www.deepnlp.org/store/pub/pub-apple-glasses) <br>
[Meta Glasses](http://www.deepnlp.org/store/pub/pub-meta-glasses) <br>
[Apple AR VR Headset](http://www.deepnlp.org/store/pub/pub-apple-ar-vr-headset) <br>
[Google Glass](http://www.deepnlp.org/store/pub/pub-google-glass) <br>
[Meta VR Headset](http://www.deepnlp.org/store/pub/pub-meta-vr-headset) <br>
[Google AR VR Headsets](http://www.deepnlp.org/store/pub/pub-google-ar-vr-headset) <br>
##### Social
[Character AI](http://www.deepnlp.org/store/pub/pub-character-ai) <br>
##### Self-Driving
[BYD Seal](http://www.deepnlp.org/store/pub/pub-byd-seal) <br>
[Tesla Model 3](http://www.deepnlp.org/store/pub/pub-tesla-model-3) <br>
[BMW i4](http://www.deepnlp.org/store/pub/pub-bmw-i4) <br>
[Baidu Apollo Reviews](http://www.deepnlp.org/store/pub/pub-baidu-apollo) <br>
[Hyundai IONIQ 6](http://www.deepnlp.org/store/pub/pub-hyundai-ioniq-6) <br>

