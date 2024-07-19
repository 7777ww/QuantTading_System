from binance_api import BinanceKlinesCollector
from config import uri

class rs_calculate(BinanceKlinesCollector):

    def __init__(self,db_uri,db_name,collection_name):
        """
        初始化RSCalculate類，繼承自BinanceKlinesCollector。

        參數：
        - db_uri (str): MongoDB的URI。
        - db_name (str): 要連接的數據庫名稱。
        - collection_name (str): 要操作的集合名稱。
        - Rs_collection用來存RS_value
        """
        super().__init__(db_uri, db_name, collection_name)
        self.Rs_collection=self.db["RS"]


if __name__ == "__main__":
    # Configuration
    DB_URI = uri
    DB_NAME = "Quant"
    COLLECTION_NAME = 'OHLCV'

    # Example usage
    collector = rs_calculate(DB_URI, DB_NAME, COLLECTION_NAME)
    print(collector.collection.find_one())
