from mongoengine import Document, StringField, FloatField, LongField

# 定义一个文档模型，与 MongoDB 集合结构匹配
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
    # 設置不返回 _id 字段
    meta = {
        'collection': 'OHLCV',
        'db_alias': 'default',
        'exclude_fields': ['_id']
    }
