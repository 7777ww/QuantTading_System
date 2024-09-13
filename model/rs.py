from mongoengine import Document, StringField, FloatField, LongField, IntField, ListField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField
class RSData(EmbeddedDocument):
    timestamp = DateTimeField(required=True)
    rs_value = FloatField(required=True)
# 定义一个文档模型，与 MongoDB 集合结构匹配
class rs(Document):
    symbol = StringField(required=True)
    moving_periods = IntField(required=True)
    interval = StringField(required=True)
    data = ListField(EmbeddedDocumentField('RSData'))

    meta = {
        'collection': 'rs',
        'indexes': [
            {'fields': ['symbol', 'moving_periods', 'interval'], 'unique': True}
        ]
    }



# 解釋：
# 1. 我們將原本的 rs 類別分成了兩個類別：rs 和 RSData
# 2. rs 類別代表一個完整的文檔，包含了 symbol、moving_periods 和 interval
# 3. RSData 類別是一個嵌入文檔，用於存儲每個時間點的 rs_value
# 4. rs 類別中的 data 字段是一個 ListField，包含了多個 RSData 實例
# 5. 這樣的結構允許我們在一個文檔中存儲多個時間點的 rs_value，每個時間點都有自己的 timestamp
# 6. 索引設置確保了 symbol、moving_periods 和 interval 的組合是唯一的
# 7. 這種結構更適合存儲和查詢一個交易對在不同時間點的 rs_value





