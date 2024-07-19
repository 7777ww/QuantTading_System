import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from quant.data_transform import convert_columns_to_string,rename_and_reorder_columns,convert_to_timestamp
from config import uri
from typing import Optional, Dict, Any
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBClient:
    def __init__(self, uri: str = uri, database_name: str = "Quant"):
        """
        Initializes the MongoDB client and connects to the specified database.

        Parameters:
        - uri (str): The MongoDB URI.
        - database_name (str): The name of the database to connect to.
        """
        self.uri = uri
        self.database_name = database_name
        self.db = self.connect_to_mongo_db()
    def connect_to_mongo_db(self) -> Optional[Collection]:
        """
        Connects to the MongoDB database.

        Returns:
        - db (Collection): The connected database object, or None if connection fails.
        """
        try:
            client = MongoClient(self.uri)
            db = client[self.database_name]
            logger.info("Successfully connected to MongoDB")
            return db
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return None
        """
        Not_complete
        """

def connect_to_mongo_db(uri=uri,database_name="Quant" ):
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

def get_data_from_mongo_with_time_range(collection:Collection, symbol: str, interval: str,start_time: Optional[str] = None, end_time: Optional[str] = None, projection=None):
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
"""
test_section
"""
if __name__ == "__main__":

    MongoClient()

    # db=connect_to_mongo_db(uri, "Quant")
    # collection=db["OHLCV"]
    # target=get_data_from_mongo_with_time_range(collection,"ETHUSDT","1d","2024-7-7","2024-7-9")
    # print(target)

