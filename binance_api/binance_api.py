import requests
import time
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from config import uri
def get_binance_contract_pairs():
    """
    Get all contract trading pairs from Binance.
    
    :return: A list of contract trading pairs
    """
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()
    
    usdt_pairs = [symbol['symbol'] for symbol in data['symbols'] if 'USDT' in symbol['symbol']]
    return usdt_pairs

class BinanceKlinesCollector:
    def __init__(self, db_uri, db_name, collection_name):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
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
        
        while True:
            klines = self.get_klines(symbol, interval, end_time=current_time)
            if not klines:
                break
            operations = []
            for k in klines:
                doc = {
                    "symbol": symbol,
                    "interval": interval,
                    "timestamp": k[0],
                    "close_time": k[6],
                    "open": k[1],
                    "high": k[2],
                    "low": k[3],
                    "close": k[4],
                    "volume": k[5],
                    
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
                    result = self.collection.bulk_write(operations)
                    print(f"Inserted or updated {result.upserted_count + result.modified_count} documents")
                    if result.upserted_count + result.modified_count == 0:
                        print("No records were inserted or updated. Stopping further fetch.")
                        break
                except Exception as e:
                    print(f"Operation failed: {e}")
            
            current_time = klines[0][0] - 1  # Next starting time
            time.sleep(1)  # Avoid hitting the rate limit

if __name__ == "__main__":
    # Configuration
    DB_URI = uri
    DB_NAME = "Quant"
    COLLECTION_NAME = 'OHLCV'

    # Example usage
    collector = BinanceKlinesCollector(DB_URI, DB_NAME, COLLECTION_NAME)
    collector.get_all_klines('ETHUSDT', '1d')
