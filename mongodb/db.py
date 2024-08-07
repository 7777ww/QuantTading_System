import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from quant.data_transform import convert_columns_to_string,rename_and_reorder_columns,convert_to_timestamp
from config import uri
from typing import Optional, Dict, Any
import pandas as pd
import os
from config import Config
from mongoengine import connect,register_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATABASE_CONFIG_FILE = os.path.join(CONFIG_DIR, 'database.json')


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




"""

test_section
"""
class MongoConnector(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path=DATABASE_CONFIG_FILE):
        if self._instance is not None:  # Avoid redundant initialization
            super().__init__()
            config = Config(config_path).load_config()
            uri = config['mongodb']['uri']
            local = config['mongodb']['local']
            db_name = config['mongodb']['name']

            register_connection(
                alias=db_name,  # 设置连接的别名为 'default'
                host=uri,         # 使用 MongoDB Atlas 的 URI
                db=db_name        # 指定数据库名称
            )

            self.db_name=config['mongodb']['name']
            try:
                # self.cloud=connect(db=self.db_name, host=uri, alias='cloud')
                # print("Connected to cloud database")

                self.cloud = MongoClient(uri)
                
            except Exception as e:
                # Handle exceptions
                pass
            try:
                self.local = MongoClient(local)
                # connect(db=self.db_name, host=local, alias='local')

            except Exception as e:
                # Handle exceptions
                pass
            self._initialized = True

    def get_cloud_conn(self):
        return self.cloud

    def get_local_conn(self):
        return self.local
    
if __name__ == "__main__":
    db=MongoConnector()
    



    # MongoClient()

    # db=connect_to_mongo_db(uri, "Quant")
    # collection=db["OHLCV"]
    # target=get_data_from_mongo_with_time_range(collection,"ETHUSDT","1d","2024-7-7","2024-7-9")
    # print(target)

