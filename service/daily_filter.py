from binance_api import SymbolFilter
from datetime import datetime
from model import DailyScreening


class SymbolService:
    @staticmethod
    def run_symbol_filter(top_n=20, moving_avg_period=5, interval='1d'):
        """運行 SymbolFilter 進行篩選"""
        symbol_filter = SymbolFilter(interval=interval)
        filtered_results = symbol_filter.filter_symbols(top_n=top_n, moving_avg_period=moving_avg_period)
        return filtered_results

    @staticmethod
    def get_daily_screening(strategy_name):
        """從資料庫根據策略名稱和當前日期獲取篩選結果"""
        today = datetime.now().date()
        return DailyScreening.objects(date=today, strategy_name=strategy_name).first()

    @staticmethod
    def filter_symbols(top_n=20, moving_avg_period=5, interval='1d', strategy_name='default_strategy'):
        """根據傳入的 strategy_name 和其他參數進行篩選"""
        symbol_filter = SymbolFilter(interval=interval, moving_periods=1)
        filtered_results = symbol_filter.filter_symbols(top_n=top_n, moving_avg_period=moving_avg_period)
        result_list = []

        # 如果有篩選結果，將其轉換成列表
        if not filtered_results.empty:
            result_list = [
                {
                    "symbol": row['symbol'],
                    "rs_value": row['rs_value'],
                    "volume": row['volume'],
                    "moving_avg_volume": row['moving_avg_volume']
                }
                for _, row in filtered_results.iterrows()
            ]
        
        
        return result_list

    @staticmethod
    def save_to_db(result_list, strategy_name):
        """將篩選結果保存到資料庫"""
        try:
            daily_screening = DailyScreening(
                date=datetime.now().date(),
                symbols=[result['symbol'] for result in result_list] if result_list else [],
                rs_values=[result['rs_value'] for result in result_list] if result_list else [],
                volumes=[result['volume'] for result in result_list] if result_list else [],
                moving_avg_volumes=[result['moving_avg_volume'] for result in result_list] if result_list else [],
                is_empty=True if not result_list else False,  # 如果結果為空，設為 True
                strategy_name=strategy_name  # 使用傳入的 strategy_name
            )
            daily_screening.save()
            print("結果已保存")

        except Exception as e:
            print(f"儲存到資料庫時發生錯誤: {str(e)}")