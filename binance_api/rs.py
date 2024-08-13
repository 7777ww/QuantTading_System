from binance_api.get_binanace_contract_pairs import binance_contract_pairs
from binance_api.get_kline import BinanceKlinesCollector
import pandas as pd
from config import uri

collector = BinanceKlinesCollector()





def calculate_rs(close_prices, shift_period):
    """
    計算相對強度（RS）。
    
    參數:
    close_prices: pandas.Series, 收盤價序列
    shift_period: int, 移動的週期數
    
    返回:
    pandas.Series: RS值
    """
    return close_prices / close_prices.shift(shift_period)

def rs(data, moving_periods, symbol):
    """
    計算給定數據的相對強度（RS）。
    
    參數:
    data: pandas.DataFrame, 包含'close'列和'timestamp'列的數據框
    moving_periods: int, 移動的週期數
    symbol: str, 交易對符號
    
    返回:
    pandas.DataFrame: 包含symbol, 時間和RS值的數據框
    """
    if 'close' not in data.columns or 'timestamp' not in data.columns:
        raise ValueError("數據框中必須包含'close'和'timestamp'列")
    
    rs_values = calculate_rs(data['close'], moving_periods)
    rs_values = rs_values.dropna()
    result_df = pd.DataFrame({
        'symbol': symbol,
        'timestamp': data['timestamp'],
        'rs_value': rs_values
    })
    
    return result_df




from binance_api.get_binanace_contract_pairs import binance_contract_pairs

def create_rs_dataframe(all_pairs=None, interval='4h', moving_periods=1):
    """
    為所有合約交易對創建包含RS值的DataFrame。

    參數:
    interval: str, K線間隔，默認為'4h'
    moving_periods: int, RS計算的移動週期，默認為1

    返回:
    pandas.DataFrame: 包含symbol、moving_periods、interval和data列的DataFrame
    """
    # 獲取所有合約交易對
    if all_pairs is None:
        all_pairs = binance_contract_pairs()

    # 創建一個列表來存儲所有交易對的RS數據
    rs_data_list = []

    for symbol in all_pairs:
        try:
            df = collector.get_recent_klines([symbol], n_klines=10, interval=interval)[symbol]
            rs_result = rs(df, moving_periods, symbol)
            
            # 將RS結果轉換為符合model格式的數據
            rs_data = [
                {
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'rs_value': row['rs_value']
                }
                for _, row in rs_result.iterrows() if not pd.isna(row['rs_value'])
            ]
            
            rs_data_list.append({
                'symbol': symbol,
                'moving_periods': moving_periods,
                'interval': interval,
                'data': rs_data
            })
        except Exception as e:
            print(f"無法獲取或處理 {symbol} 的數據：{str(e)}")

    # 將結果轉換為DataFrame
    # 直接從DataFrame中刪除rs_value為NaN的行
    # 從rs_data_list中刪除每個交易對的前moving_periods筆數據

    result_df = pd.DataFrame(rs_data_list)

    return result_df

def get_top_rs_pairs(result_df=None,n=10, interval='4h', moving_periods=1):
    """
    獲取RS值最大的前n個交易對。

    參數:
    n: int, 要返回的交易對數量，默認為10
    interval: str, K線間隔，默認為'4h'
    moving_periods: int, RS計算的移動週期，默認為1

    返回:
    pandas.DataFrame: 包含前n個RS值最大的交易對數據
    """
    if result_df is None:
        result_df = create_rs_dataframe(interval, moving_periods)

    # 按最後一個RS值降序排序
    result_df['last_rs'] = result_df['data'].apply(lambda data: data[-1]['rs_value'] if data else None)
    top_n_df = result_df.sort_values('last_rs', ascending=False).head(n)
    
    top_n_df = top_n_df.drop('last_rs', axis=1)
    top_rs_data = []
    for _, row in top_n_df.iterrows():
        symbol = row['symbol']
        last_rs_value = row['data'][-1]['rs_value']
        top_rs_data.append({"symbol": symbol, "rs_value": round(last_rs_value, 4)})
    
    return pd.DataFrame(top_rs_data)

    return top_n_df

from model.rs import rs as RSModel
from mongodb import init_db

def save_rs_to_db(result_df):
    """
    將RS數據保存到MongoDB數據庫。

    參數:
    result_df: pandas.DataFrame, 包含RS數據的DataFrame
    """
    # 連接到MongoDB數據庫

    for _, row in result_df.iterrows():
        # 查找現有的RSModel實例
        rs_instance = RSModel.objects(symbol=row['symbol'], moving_periods=row['moving_periods'], interval=row['interval']).first()
        
        if rs_instance:
            # 更新data字段
            rs_instance.update(set__data=[
                {
                    'timestamp': pd.to_datetime(item['timestamp']),
                    'rs_value': item['rs_value']
                }
                for item in row['data']
            ])
            print(f"更新 {row['symbol']} 的RS數據")
        else:
            # 如果記錄不存在，創建新的RSModel實例
            rs_instance = RSModel(
                symbol=row['symbol'],
                moving_periods=int(row['moving_periods']),
                interval=row['interval'],
                data=[
                    {
                        'timestamp': pd.to_datetime(item['timestamp']),
                        'rs_value': item['rs_value']
                    }
                    for item in row['data']
                ]
            )
            rs_instance.save()
            print(f"儲存 {row['symbol']} 的RS數據")

    print("RS數據已成功保存到數據庫")

# 在get_top_rs_pairs函數的末尾添加以下代碼

#1.目前待修改：shfit後2的nan2.沒有全寫入
# 使用示例
if __name__ == "__main__":
    rs_df=create_rs_dataframe()
    top_rs_pairs=get_top_rs_pairs(rs_df)

    # # 選擇一個symbol來查看其DataFrame
    # sample_symbol = rs_df['symbol'].iloc[0]
    # sample_df = rs_df[rs_df['symbol'] == sample_symbol]
    
    # print(f"查看 {sample_symbol} 的DataFrame：")
    # print(sample_df)
    
    # # 顯示該symbol的數據詳情
    # print(f"\n{sample_symbol} 的數據詳情：")
    # print(sample_df['data'].iloc[0])
    
    # # 將數據寫入數據庫
    save_rs_to_db(rs_df)
    print("數據已成功寫入數據庫")

