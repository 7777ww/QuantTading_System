import requests
import time
from datetime import datetime
from pymongo import MongoClient, UpdateOne, ASCENDING
def date_to_milliseconds(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return int(dt.timestamp() * 1000)
def get_klines(symbol, interval, start_time=None, end_time=None, limit=500):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    if start_time:
        params['startTime'] = date_to_milliseconds(start_time) if isinstance(start_time, str) else start_time
    if end_time:
        params['endTime'] = date_to_milliseconds(end_time) if isinstance(end_time, str) else end_time
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return data

def get_all_klines(symbol, interval, start_time):
    
    while True:
        klines = get_klines(symbol, interval, start_time)
        if not klines:
            break
        operations = []
        for k in klines:
            doc = {
                "symbol": symbol,
                "interval": interval,
                "timestamp": k[0],
                "open": k[1],
                "high": k[2],
                "low": k[3],
                "close": k[4],
                "volume": k[5],
                "close_time": k[6],

            }
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
                result = collection.bulk_write(operations)
                print(f"插入或更新了 {result.upserted_count + result.modified_count} 个文档")
            except Exception as e:
                print(f"操作失败: {e}")
        
        start_time = klines[-1][0] + 1  # 下一個起始時間
        time.sleep(1)  # 避免頻率過高