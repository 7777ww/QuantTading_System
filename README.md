# binance交易所交易對篩選系統

這個專案是一個基於Flask的微服務，用於篩選和分析幣安交易所的交易對。它主要功能包括:

1. 獲取幣安交易所的交易對數據
2. 計算交易對的RS ranking
3. 根據成交量和移動平均線進行篩選
4. 將篩選結果保存到數據庫
5. 通過Web界面展示篩選結果
系統架構：
![系統架構](/Users/caibinghong/quant_trading_system_diagram/quant_system_stracture.png)


系統使用Flask框架構建，提供RESTful API接口。它允許客戶端通過HTTP請求與服務器進行交互，實現數據的獲取、處理和展示。這種架構使得系統具有良好的可擴展性和靈活性，能夠方便地集成到其他應用中或者被其他服務調用。

## route資料夾
這個資料夾包含了所有使用@route裝飾器的Flask路由。目前已實現功能：

1. filter.py：包含了/get_daily_screening路由，用於獲取每日篩選結果。


## templates資料夾
存放HTML模板文件，主要文件有：

1. filter.html：顯示每日篩選結果的頁面模板。
2. get_kline.html：用於獲取K線數據的表單頁面。
3. kline_data.html：顯示OHLCV數據的頁面模板。

## binance_api資料夾
包含與幣安API交互的代碼，如filter.py中的SymbolFilter類。

## model資料夾
定義了數據模型，如DailyScreening模型。

## main.py
這是整個Flask應用的入口點，負責初始化和啟動服務。

## requirements.txt
列出了項目所需的所有Python依賴包。


