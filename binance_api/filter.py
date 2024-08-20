from binance_api.rs import RSAnalyzer
from model.daily import DailyScreening
from model import OHLCV
from datetime import datetime, timedelta
import pandas as pd
from binance_api.get_kline import BinanceKlinesCollector
from pymongo.errors import OperationFailure
from mongoengine import NotUniqueError

class SymbolFilter:
    def __init__(self, interval='4h', moving_periods=1):
        from binance_api.get_binanace_contract_pairs import binance_contract_pairs
        self.usdt_pairs = binance_contract_pairs()
        self.rs_analyzer = RSAnalyzer(all_pairs=self.usdt_pairs, interval=interval, moving_periods=moving_periods)
        self.collector = BinanceKlinesCollector()
        self.interval = interval
   

    def filter_symbols(self, top_n=20, moving_avg_period=5):
        # 1. 獲取RS值最高的前N個交易對
        top_rs_pairs = self.rs_analyzer.get_top_rs_pairs(n=top_n)
        # 獲取top_rs_pairs的最近K線數據
        symbols = top_rs_pairs['symbol'].tolist()
        recent_klines = self.collector.get_recent_klines(symbols, n_klines=50, interval=self.interval)

        # 打印獲取的K線數據信息
        print(f"已獲取 {len(recent_klines)} 個交易對的K線數據")

        filtered_results = []

        # 2. 遍歷這些交易對:
        for symbol, klines_df in recent_klines.items():
            if not klines_df.empty:
                # 計算移動平均成交量
                klines_df['volume'] = klines_df['volume'].astype(float)
                klines_df['moving_avg_volume'] = klines_df['volume'].rolling(window=moving_avg_period).mean()
                
                # 獲取最新一天的成交量和移動平均成交量
                latest_volume = klines_df['volume'].iloc[-1]
                latest_moving_avg_volume = klines_df['moving_avg_volume'].iloc[-1]
                
                # 應用篩選條件:
                # 如果最新一天的成交量大於N天移動平均和價格變化都滿足閾值:
                if latest_volume > latest_moving_avg_volume:
                    # 將交易對添加到篩選結果中
                    filtered_results.append({
                        'symbol': symbol,
                        'volume': latest_volume,
                        'moving_avg_volume': latest_moving_avg_volume,
                        'rs_value': top_rs_pairs.loc[top_rs_pairs['symbol'] == symbol, 'rs_value'].values[0]
                    })

        # 將篩選結果轉換為DataFrame
        self.filtered_results = pd.DataFrame(filtered_results)
        return self.save_db()

    def save_db(self):
        
        # 3. 將篩選結果保存到數據庫
        if not self.filtered_results.empty:
            try:
                daily_screening = DailyScreening(
                    date=datetime.now().date(),
                    symbols=self.filtered_results['symbol'].tolist(),
                    volumes=self.filtered_results['volume'].tolist(),
                    moving_avg_volumes=self.filtered_results['moving_avg_volume'].tolist(),
                    rs_values=self.filtered_results['rs_value'].tolist()
                )
                # 檢查數據庫中是否已存在今日的篩選結果

                daily_screening.save()
                print("已保存今日新的篩選結果")
                print(f"已將 {len(self.filtered_results)} 個符合條件的交易對保存到數據庫")
            except NotUniqueError:
                print(f"日期 {datetime.now().date()} 已存在於數據庫中，更新數據")
                existing_screening = DailyScreening.objects(date=datetime.now().date()).first()
                if existing_screening:
                    existing_screening.update(
                        set__symbols=self.filtered_results['symbol'].tolist(),
                        set__volumes=self.filtered_results['volume'].tolist(),
                        set__moving_avg_volumes=self.filtered_results['moving_avg_volume'].tolist(),
                        set__rs_values=self.filtered_results['rs_value'].tolist()
                    )
                    print("已更新今日的篩選結果")
        else:
            print("篩選結果為空，沒有符合條件的交易對")
        
        return self.filtered_results
        # 3. 將篩選結果保存到數據庫
   
        # 2. 遍歷這些交易對:
            # 2.1 獲取每個交易對最近K個kline的OHLCV數據
            
            # 2.2 如果有數據:
                # 計算24小時總成交量
                # 計算價格變化百分比
                
                # 2.3 應用篩選條件:
                    # 如果成交量和價格變化都滿足閾值:
                        # 將交易對添加到篩選結果中

        # 3. 將篩選結果保存到數據庫

        # 4. 返回篩選結果的DataFrame

# 使用示例
if __name__ == "__main__":
    filter = SymbolFilter(interval='1d', moving_periods=1)
    過濾結果 = filter.filter_symbols(top_n=20, moving_avg_period=5)
    
    print(過濾結果)
