import pandas as pd
from binance_api import BinanceKlinesCollector
from binance_api import binance_contract_pairs
from datetime import datetime
from model import DailyScreening

class RSAnalyzer:
    def __init__(self, all_pairs=None, interval='1d', moving_periods=1):
        self.all_pairs = all_pairs if all_pairs is not None else binance_contract_pairs()
        self.interval = interval
        self.moving_periods = moving_periods
        self.result_df = None
        self.top_rs=None
        self.collector = BinanceKlinesCollector()

    def create_rs_dataframe(self, moving_periods=None, interval=None):
        """為所有合約交易對創建包含RS值的DataFrame"""
        if moving_periods is not None:
            self.moving_periods = moving_periods
        if interval is not None:
            self.interval = interval

        rs_data_list = []
        for symbol in self.all_pairs:
            try:
                df = self.collector.get_recent_klines([symbol], n_klines=10, interval=self.interval)[symbol]
                rs_result = self.calculate_rs(df)
                
                rs_data = [
                    {'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), 'rs_value': row['rs_value']}
                    for _, row in rs_result.iterrows() if not pd.isna(row['rs_value'])
                ]
                rs_data_list.append({'symbol': symbol, 'moving_periods': self.moving_periods, 'interval': self.interval, 'data': rs_data})
            except Exception as e:
                print(f"無法獲取或處理 {symbol} 的數據：{str(e)}")

        self.result_df = pd.DataFrame(rs_data_list)
        return self.result_df

    def calculate_rs(self, df):
        """計算RS值"""
        close_prices = df['close']
        rs_values = close_prices / close_prices.shift(self.moving_periods)
        return pd.DataFrame({'timestamp': df['timestamp'], 'rs_value': rs_values.dropna()})

    def get_top_rs_pairs(self, n=10):
        """獲取RS值最大的前n個交易對"""
        if self.result_df is None:
            self.create_rs_dataframe()

        self.result_df['last_rs'] = self.result_df['data'].apply(lambda data: data[-1]['rs_value'] if data else None)
        top_n_df = self.result_df.sort_values('last_rs', ascending=False).head(n)
        self.top_rs_data = [
            {'symbol': row['symbol'], 'rs_value': round(row['data'][-1]['rs_value'], 4)} 
            for _, row in top_n_df.iterrows()
        ]
        
        return self.top_rs_data

    def save_rs_pairs_to_db(self,top_rs_pairs,strategy_name="RS_Selection"):
        """
        將篩選出的交易對及其RS值保存到MongoDB資料庫。
        
        參數:
        - symbols: list, 交易對的列表 (如 ['BTCUSDT', 'ETHUSDT'])
        - rs_values: list, 每個交易對對應的RS值
        - strategy_name: str, 使用的策略名稱 (默認為 'RS_Selection')
        """
        
    # 提取 symbols 和 rs_values 列表
        symbols = [pair['symbol'] for pair in top_rs_pairs]
        rs_values = [pair['rs_value'] for pair in top_rs_pairs]

        # 構建 DailyScreening 物件
        daily_screening = DailyScreening(
            date=datetime.today(),
            strategy_name=strategy_name,
            symbols=symbols,  # 交易對列表
            rs_values=rs_values  # 對應的RS值列表
        )
            # 保存到 MongoDB
        try:
            daily_screening.save()
            print(f"已成功將 {len(top_rs_pairs['symbol'])} 個交易對的篩選結果保存到資料庫。")
            return True
        except Exception as e:
            print(f"寫入資料庫時發生錯誤: {str(e)}")
            return False

    def save_rs_to_db(self):
        """將RS數據保存到MongoDB"""
        if self.result_df is None:
            self.create_rs_dataframe()
        save_rs_to_db(self.result_df)

    def get_rs_from_db(self, strategy_name="RS_Selection",date=datetime.today()):
        """
        從數據庫中獲取RS值。
        
        參數:
        - strategy_name: 可選的策略名稱 (默認為 'RS_Selection')
        """
        # 創建 DailyScreening 物件
        daily_screening = DailyScreening.objects(date=date, strategy_name=strategy_name).first()
        
        # 如果有篩選結果，將其轉換成列表
        if daily_screening:
            rs_data = [{'symbol': symbol, 'rs_value': rs_value} 
                    for symbol, rs_value in zip(daily_screening.symbols, daily_screening.rs_values)]
            return rs_data
        else:
            return []



