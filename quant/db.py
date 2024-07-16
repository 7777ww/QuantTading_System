from pymongo import MongoClient
from pymongo.collection import Collection
from data_transform import convert_columns_to_string,rename_and_reorder_columns,convert_to_timestamp
from config.config import uri
from typing import Optional, Dict, Any
import pandas as pd



def connect_to_mongo_db(uri, database_name):
    """
    Initializes the MongoDB client and connects to the specified database.

    Parameters:
    - uri (str): The MongoDB URI.
    - database_name (str): The name of the database to connect to.

    Returns:
    - db (Database): The connected database object, or None if connection fails.
    """
    try:
        client = MongoClient(uri)
        db = client[database_name]
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_data_from_mongo_with_time_range(collection:Collection, start_time: Optional[str] = None, end_time: Optional[str] = None, projection=None):
    """
    从 MongoDB 集合中抓取特定时间范围的数据。

    :param collection: MongoDB 集合
    :param start_time: 开始时间（字符串格式）
    :param end_time: 结束时间（字符串格式）
    :param projection: 要包含或排除的字段
    :return: 包含查询数据的 pandas DataFrame
    """
    query = {}
    if start_time and end_time:
        start_time = convert_to_timestamp(start_time)
        end_time = convert_to_timestamp(end_time)
        query = {
            "timestamp": {
                "$gte": start_time,
                "$lt": end_time
            }
        }
    
    cursor = collection.find(query, projection)
    data = pd.DataFrame(list(cursor))
    data = convert_columns_to_string(data, ['timestamp', 'close_time'])
    data = rename_and_reorder_columns(data)



    return pd.DataFrame(data)
"""
test_section
"""
db=connect_to_mongo_db(uri, "Quant")
collection=db["OHLCV"]
target=get_data_from_mongo_with_time_range(collection,"2024-7-7","2024-7-9")
print(target)

