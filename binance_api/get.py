import requests
import time
from datetime import datetime
from pymongo import MongoClient, UpdateOne, ASCENDING
from quant.db import connect_to_mongo_db
from config import uri

class BinanceAPI:
    BASE_URL = 'https://api.binance.com/api/v3/klines'
    
    
    @staticmethod
    def date_to_milliseconds(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return int(dt.timestamp() * 1000)
    
    @classmethod
    def get_klines(cls, symbol, interval, start_time=None, end_time=None, limit=500):
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        if start_time:
            params['startTime'] = cls.date_to_milliseconds(start_time) if isinstance(start_time, str) else start_time
        if end_time:
            params['endTime'] = cls.date_to_milliseconds(end_time) if isinstance(end_time, str) else end_time
        
        response = requests.get(cls.BASE_URL, params=params)
        data = response.json()
        return data

    def get_earliest_timestamp(self, symbol, interval):
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': 0,
            'limit': 1
        }
        response = requests.get(self.BASE_URL, params=params)
        data = response.json()
        return data[0][0] if data else None

class Kline:
    def __init__(self, symbol, interval, kline_data):
        self.symbol = symbol
        self.interval = interval
        self.timestamp = kline_data[0]
        self.open = kline_data[1]
        self.high = kline_data[2]
        self.low = kline_data[3]
        self.close = kline_data[4]
        self.volume = kline_data[5]
        self.close_time = kline_data[6]

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "interval": self.interval,
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "close_time": self.close_time
        }

class KlineDatabase:
    def __init__(self, uri,db_name, collection_name):
        db=connect_to_mongo_db(uri=uri,database_name=db_name)#這邊要輸入自己建的uri
        self.connection=db[collection_name]
 

    def save_klines(self, klines):
        operations = []
        for kline in klines:
            doc = kline.to_dict()
            query = {
                "symbol": doc["symbol"],
                "interval": doc["interval"],
                "timestamp": doc["timestamp"]
            }
            operations.append(
                UpdateOne(
                    query,
                    {"$set": doc},
                    upsert=True
                )
            )
        if operations:
            try:
                result = self.collection.bulk_write(operations)
                print(f"Inserted or updated {result.upserted_count + result.modified_count} documents")
            except Exception as e:
                print(f"Operation failed: {e}")

def download_all_klines(symbol, interval, start_time, db_name='Quant', collection_name='OHLCV'):
    api = BinanceAPI()
    db = KlineDatabase(uri,db_name, collection_name)
    
    while True:
        klines_data = api.get_klines(symbol, interval, start_time)
        if not klines_data:
            break
        
        klines = [Kline(symbol, interval, k) for k in klines_data]
        db.save_klines(klines)
        
        start_time = klines_data[-1][0] + 1  # next starting time
        time.sleep(1)  # avoid hitting rate limit

# Example usage
download_all_klines('BTCUSDT', '4h', '2024-07-17')
