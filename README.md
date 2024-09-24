# Binance 交易所交易對篩選系統

這個專案是一個基於 Flask 的微服務，用於篩選和分析幣安交易所的交易對。它的主要功能包括：

- 獲取幣安交易所的交易對數據
- 計算交易對的 RS ranking
- 根據成交量和移動平均線進行篩選
- 將篩選結果保存到數據庫
- 通過 Web 界面展示篩選結果

## 使用 MVC 架構
此系統採用了 MVC（Model-View-Controller）架構：



### Model
使用 **MongoEngine** 定義資料模型，負責數據邏輯與數據庫交互部分。

### View (Route)
`route/` 資料夾定義了 Flask 的路由，負責處理來自客戶端的請求，並將數據返回前端或 API 客戶端。  
目前前端完全分離出來，但仍可以使用 Flask 的 `render_template` 呈現資料。

- **`filter.py`**：定義篩選結果的顯示與每日篩選結果的 API 端點。

### Controller (Service)
`service/` 資料夾負責業務邏輯，主要處理來自 Binance API 的數據與 DB 的交互，並根據篩選邏輯對數據進行處理。

## 系統架構
系統架構如下所示：
![系統架構圖](./quant_system_stracture.png)

系統使用 Flask 框架構建，並提供 RESTful API 接口，允許客戶端通過 HTTP 請求與服務器進行交互，實現數據的獲取、處理和展示。該架構具有良好的擴展性與靈活性，便於集成到其他應用中，或供其他服務調用。

## Docker 部署
使用 Docker 可以方便地部署該應用。請確保你已經安裝 Docker，然後按以下步驟運行應用：

1. 構建 Docker 映像：
    ```bash
    docker build -t binance-filter-system .
    ```

2. 運行容器：
    ```bash
    docker run -d -p 5000:5000 binance-filter-system
    ```

這樣，你的 Flask 應用將會在本地的 `5000` 端口上運行。

## 使用說明

### RESTful API 路由

- **`/get_daily_screening`**：此路由會返回當日的篩選結果。使用 Flask 的 `@route` 裝飾器來定義。

### 頁面模板

- **`filter.html`**：顯示每日篩選結果。
- **`get_kline.html`**：用於提交請求以獲取特定交易對的 K 線數據。
- **`kline_data.html`**：顯示特定交易對的 OHLCV 數據。

## 主要功能

1. **Flask RESTful API**：該系統提供了簡單易用的 API，方便其他系統調用篩選結果和 OHLCV 數據。
2. **基於 Binance API 的交易對篩選**：根據自定義的篩選條件（如成交量、移動平均線等）進行篩選。
3. **數據持久化**：篩選結果會存儲到數據庫中，方便後續查詢與分析。
4. **網頁展示**：通過簡單的 Web 界面，使用者可以直接查看篩選結果和 K 線數據。

## 依賴安裝

如未使用 Docker 部署，請確保安裝以下依賴：

```bash
pip install -r requirements.txt
