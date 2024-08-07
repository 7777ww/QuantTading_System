from mongoengine import register_connection, Document, StringField, FloatField, DateTimeField, LongField
import json
import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATABASE_CONFIG_FILE = os.path.join(CONFIG_DIR, 'database.json')
# 从配置文件中加载 MongoDB 连接信息
def load_config(config_path):
    with open(DATABASE_CONFIG_FILE, 'r') as file:
        config = json.load(file)
    return config

# 假设配置文件路径为 'config.json'
config_path = 'config.json'
config = load_config(config_path)

# 从配置中提取URI和数据库名称
uri = config['mongodb']['uri']
db_name = config['mongodb']['name']

# 使用 mongoengine 注册 MongoDB 连接

def register_db_connection(config):
    """
    注册 MongoDB 连接
    :param config: 配置文件中的 MongoDB 连接信息
    """
    uri = config['mongodb']['uri']
    db_name = config['mongodb']['name']
    
    register_connection(
        alias=db_name,  # 设置连接的别名为 'default'
        host=uri,         # 使用 MongoDB Atlas 的 URI
        db=db_name        # 指定数据库名称
    )

# 定义一个文档模型
class OHLCV(Document):
    symbol = StringField(required=True, max_length=10)  # 交易对符号
    interval = StringField(required=True, max_length=10)  # 时间周期
    open = FloatField(required=True)  # 开盘价
    high = FloatField(required=True)  # 最高价
    low = FloatField(required=True)  # 最低价
    close = FloatField(required=True)  # 收盘价
    volume = FloatField(required=True)  # 成交量
    timestamp = LongField(required=True)  # 时间戳
    close_time = LongField(required=True)  # 结束时间

    meta = {'collection': 'OHLCV', 'db_alias': 'default'}  # 指定集合和使用的别名

# 测试连接：查询数据
def test_connection():
    try:
        # 连接 MongoDB 并查询集合中的所有文档
        documents = OHLCV.objects()
        print(f"共找到 {documents.count()} 条数据。")
        
        # 打印前几条数据
        for doc in documents[:5]:
            print(f"交易对: {doc.symbol}, 开盘价: {doc.open}, 收盘价: {doc.close}, 时间戳: {doc.timestamp}")

    except Exception as e:
        print("查询数据时发生错误：", e)

# 主程序入口
if __name__ == "__main__":
    test_connection()  # 测试连接并打印数据
