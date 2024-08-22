from pymongo.collection import Collection
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime
from model import OHLCV
import pandas as pd




def get_ohlcv_data_as_df(symbol: str, interval: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> pd.DataFrame:
    """
    從MongoDB獲取OHLCV數據並轉換為pandas DataFrame，以timestamp為索引。
    如果資料庫中缺少部分數據，則從Binance API下載缺失的部分並寫入資料庫。

    :param symbol: 交易對符號
    :param interval: 時間間隔
    :param start_time: 開始時間（可選），支持多種日期格式，如 '2024' 或 '2024-08'
    :param end_time: 結束時間（可選），支持多種日期格式，如 '2024' 或 '2024-08'
    :return: 包含OHLCV數據的pandas DataFrame
    :raises ValueError: 如果日期解析失敗
    """
    from dateutil.parser import parse
    from dateutil.relativedelta import relativedelta

    try:
        def parse_date(date_str, is_start=True):
            if not date_str:
                return None
            date = parse(date_str)
            if len(str(date.year)) == 4:
                if not is_start:
                    # 對於結束日期,如果不是月底,則保持原樣
                    if date.day != (date + relativedelta(months=1, days=-1)).day:
                        return date.strftime('%Y-%m-%d')
                    date = date + relativedelta(months=1, days=-1)
            return date.strftime('%Y-%m-%d')

        start_time = parse_date(start_time)
        end_time = parse_date(end_time, False)
    except ValueError as e:
        raise ValueError(f"無法解析日期: {str(e)}")
    """
    從MongoDB獲取OHLCV數據並轉換為pandas DataFrame，以timestamp為索引。
    如果資料庫中缺少部分數據，則從Binance API下載缺失的部分並寫入資料庫。

    :param symbol: 交易對符號
    :param interval: 時間間隔
    :param start_time: 開始時間（可選）
    :param end_time: 結束時間（可選）
    :return: 包含OHLCV數據的pandas DataFrame
    """
    from mongodb.db_set_up import init_db
    init_db()
    query = {"symbol": symbol, "interval": interval}
    if start_time:
        query["timestamp"] = {"$gte": convert_to_timestamp(start_time)}
    if end_time:
        if "timestamp" in query:
            query["timestamp"]["$lt"] = convert_to_timestamp(end_time)
        else:
            query["timestamp"] = {"$lt": convert_to_timestamp(end_time)}

    data = OHLCV.objects(__raw__=query).exclude('id')
    df = pd.DataFrame(list(data.as_pymongo()))
    
    if df.empty or (start_time and end_time and len(df) < expected_data_points(start_time, end_time, interval)):
        # 如果資料庫中沒有數據或數據不完整，從Binance API下載
        from binance_api.get_kline import BinanceKlinesCollector
        collector = BinanceKlinesCollector()
        collector.get_all_klines(symbol, interval, start_time=start_time)
        print("downloaded_new_data_from_binance")
        # 重新從資料庫獲取數據
        data = OHLCV.objects(__raw__=query)
        df = pd.DataFrame(list(data.as_pymongo()))

    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        print("get_data_from_db")
    return df

def expected_data_points(start_time: str, end_time: str, interval: str) -> int:
    """
    計算給定時間範圍和間隔應該有的數據點數量

    :param start_time: 開始時間
    :param end_time: 結束時間
    :param interval: 時間間隔
    :return: 預期的數據點數量
    """
    start = pd.to_datetime(start_time)
    end = pd.to_datetime(end_time)
    duration = end - start
    
    interval_map = {'m': 'T', 'h': 'H', 'd': 'D'}
    interval_pd = interval.replace(interval[-1], interval_map[interval[-1]])
    
    return len(pd.date_range(start, end, freq=interval_pd)) - 1



def convert_to_timestamp(date_string: str) -> int:
    """
    將日期字串轉換為時間戳。

    :param date_string: 日期字串，格式為 'YYYY-MM-DD'
    :return: 對應的時間戳（毫秒）
    """
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    return int(dt.timestamp() * 1000)
def convert_columns_to_string(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    將指定的列轉換為字符串類型。

    :param df: 輸入的 DataFrame
    :param columns: 需要轉換的列名列表
    :return: 轉換後的 DataFrame
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df





def get_top_rs():
    pass


if __name__ == "__main__":
    df=get_ohlcv_data_as_df("BTCUSDT", "1d", "2024-08-11", "2024-08-13")
    print(df)