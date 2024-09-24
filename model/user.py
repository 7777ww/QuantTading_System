from mongoengine import Document, StringField, IntField

class UserModel(Document):
    # 定義 MongoDB 集合名稱
    meta = {'collection': 'users'}

    # 定義字段
    username = StringField(required=True)
    password = StringField(required=True, max_length=255)  # 設置足夠大的 max_length
