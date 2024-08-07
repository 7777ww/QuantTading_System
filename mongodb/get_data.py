from pymongo.collection import Collection
from typing import Optional, Dict, Any

def get_kline_with_time_range(collection:Collection, symbol: str, interval: str,start_time: Optional[str] = None, end_time: Optional[str] = None, projection=None):
    """
 從 MongoDB 集合中抓取特定時間範圍的資料。

    :param collection: MongoDB 集合
    :param symbol: 查詢的符號
    :param interval: 查詢的時間間隔
    :param start_time: 開始時間（字符串格式）
    :param end_time: 結束時間（字符串格式）
    :param projection: 要包含或排除的字段
    :return: 包含查詢資料的 pandas DataFrame
    """
    query = {"symbol": symbol, "interval": interval}
    if start_time:
        start_time = convert_to_timestamp(start_time)
        query["timestamp"] = {"$gte": start_time}
    if end_time:
        end_time = convert_to_timestamp(end_time)
        if "timestamp" in query:
            query["timestamp"]["$lt"] = end_time
        else:
            query["timestamp"] = {"$lt": end_time}
    
    
    cursor = collection.find(query, projection)
    data = pd.DataFrame(list(cursor))
    data = convert_columns_to_string(data, ['timestamp', 'close_time'])
    data = rename_and_reorder_columns(data)



    return pd.DataFrame(data)
