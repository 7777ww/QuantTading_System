import requests
import time
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from config import uri
import pandas as pd

class BinanceKlinesCollector:
    def __init__(self):
        from mongodb import init_db
        from model import OHLCV as OHLCVModel
        init_db()
        self.OHLCV = OHLCVModel 
        self.session = requests.Session()
        self.klines_data = {}

    def date_to_milliseconds(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return int(dt.timestamp() * 1000)
    
    def get_klines(self, symbol, interval, start_time=None, end_time=None, limit=500):
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit

        }
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return data
    def get_recent_klines(self, symbols, n_klines=10, interval='4h'):
        """
        獲取所有合約交易對的最近N條K線數據。

        參數:
        symbols: list, 要獲取K線數據的交易對列表
        n_klines: int, 要獲取的K線數量
        interval: str, K線間隔，默認為'4h'

        返回:
        dict: 以交易對為鍵，K線數據為值的字典
        """
        self.klines_data = {}

        for symbol in symbols:
            print(f"正在獲取 {symbol} 的最近 {n_klines} 條 {interval} K線數據...")
            klines = self.get_klines(symbol, interval, limit=n_klines)
            if klines:
                # 將K線數據轉換為DataFrame
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                # 將時間戳轉換為datetime格式
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                # 將收盤價轉換為浮點數
                df['close'] = df['close'].astype(float)
                self.klines_data[symbol] = df
            else:
                print(f"無法獲取 {symbol} 的K線數據")

        return self.klines_data

    def get_earliest_timestamp(self, symbol, interval):
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': 0,
            'limit': 1
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data[0][0] if data else None
    
    
    def get_all_klines(self, symbol, interval, start_time=None):
        if not start_time:
            start_time = self.get_earliest_timestamp(symbol, interval)
            if not start_time:
                print(f"Failed to fetch earliest timestamp for symbol {symbol}")
                return
        
        current_time = int(time.time() * 1000)  # Current time in milliseconds
        
        # 先檢查資料庫中是否已存在數據
        existing_data = self.OHLCV.objects(symbol=symbol, interval=interval).order_by('-timestamp').first()
        if existing_data:
            print(f"資料庫中{symbol} 的 {interval} 間隔數據最新時間戳為 {existing_data.timestamp}。")
            print(f"最新的時間戳為 {current_time}。")
            def interval_to_milliseconds(interval):
                """將時間間隔轉換為毫秒"""
                unit = interval[-1]
                number = int(interval[:-1])
                if unit == 'm':
                    return number * 60 * 1000
                elif unit == 'h':
                    return number * 60 * 60 * 1000
                elif unit == 'd':
                    return number * 24 * 60 * 60 * 1000
                elif unit == 'w':
                    return number * 7 * 24 * 60 * 60 * 1000
                else:
                    raise ValueError(f"不支持的時間間隔: {interval}")

            需要寫入的筆數 = (current_time - existing_data.timestamp) // interval_to_milliseconds(interval)
            print(f"需要寫入 {需要寫入的筆數} 筆新數據。")
            start_time = existing_data.timestamp + 1
        else:
            start_time = self.get_earliest_timestamp(symbol, interval)

        while True:
            klines = self.get_klines(symbol, interval, start_time=start_time, end_time=current_time)
            if not klines:
                break
            
            new_klines = []
            for k in klines:
                timestamp = int(k[0])
                if not self.OHLCV.objects(symbol=symbol, interval=interval, timestamp=timestamp).first():
                    new_klines.append(k)
            
            if new_klines:
                ohlcv_list = []
                for k in new_klines:
                    ohlcv = self.OHLCV(
                        symbol=symbol,
                        interval=interval,
                        timestamp=int(k[0]),
                        close_time=int(k[6]),
                        open=float(k[1]),
                        high=float(k[2]),
                        low=float(k[3]),
                        close=float(k[4]),
                        volume=float(k[5])
                    )
                    ohlcv_list.append(ohlcv)
                
                try:
                    self.OHLCV.objects.insert(ohlcv_list)
                    print(f"成功插入 {symbol} 的 {len(ohlcv_list)} 條新 OHLCV 數據")
                except Exception as e:
                    print(f"批量操作失敗: {e}")
            
            start_time = klines[-1][0] + 1  # 下一個開始時間
            time.sleep(1)  # 避免達到速率限制


if __name__ == "__main__":
    # Configuration

    collector = BinanceKlinesCollector()
    # collector.get_all_klines('BTCUSDT', '4h')
    collector.get_recent_klines(['BTCUSDT'], n_klines=10, interval='4h')
