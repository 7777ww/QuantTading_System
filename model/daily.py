from mongoengine import Document, StringField, ListField, FloatField, DateField

class DailyScreening(Document):
    #改用date+name
    date = DateField(required=True)  # 篩選日期，作為主鍵
    strategy_name = StringField(required=True,default="none")  # 策略名稱
    symbols = ListField(StringField(), required=True)  # 篩選出的標的列表
    rs_values = ListField(FloatField())  # 對應的RS值列表
    volumes = ListField(FloatField())  # 對應的成交量列表
    moving_avg_volumes = ListField(FloatField())  # 對應的移動平均成交量列表
    price_changes = ListField(FloatField())  # 對應的價格變化百分比列表
    meta = {
        'collection': 'daily_screening',
        'indexes': [
            {'fields': ['date', 'strategy_name'], 'unique': True, 'name': 'unique_date_strategy_index'}  # 指定索引名稱
        ]
    }
    def test_save_db(self):
        """
        測試保存到數據庫的功能
        """
        from datetime import datetime
        import random

        # 創建測試數據
        test_date = datetime.now().date()
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        test_rs_values = [random.uniform(0, 1) for _ in range(3)]
        test_volumes = [random.uniform(1000, 10000) for _ in range(3)]
        test_moving_avg_volumes = [random.uniform(800, 9000) for _ in range(3)]
        test_price_changes = [random.uniform(-5, 5) for _ in range(3)]

        # 創建 DailyScreening 實例
        test_screening = DailyScreening(
            date=test_date,
            symbols=test_symbols,
            rs_values=test_rs_values,
            volumes=test_volumes,
            moving_avg_volumes=test_moving_avg_volumes,
            price_changes=test_price_changes
        )

        try:
            # 先檢查日期是否已存在
            existing_screening = DailyScreening.objects(date=test_date).first()
            
            if existing_screening:
                # 如果已存在，則更新數據
                existing_screening.update(
                    set__symbols=test_symbols,
                    set__rs_values=test_rs_values,
                    set__volumes=test_volumes,
                    set__moving_avg_volumes=test_moving_avg_volumes,
                    set__price_changes=test_price_changes
                )
                print("已存在的數據已更新")
            else:
                # 如果不存在，則保存新數據
                test_screening.save()
                print("新的測試數據已保存到數據庫")

            # 從數據庫中檢索保存的數據
            retrieved_screening = DailyScreening.objects(date=test_date).first()
            
            if retrieved_screening:
                print("成功從數據庫檢索到保存的數據")
                print(f"檢索到的日期: {retrieved_screening.date}")
                print(f"檢索到的標的: {retrieved_screening.symbols}")
            else:
                print("無法從數據庫檢索到保存的數據")

        except Exception as e:
            print(f"保存或檢索數據時發生錯誤: {str(e)}")

        finally:
            # 清理測試數據
            DailyScreening.objects(date=test_date).delete()
            print("測試數據已從數據庫中刪除")
if __name__ == "__main__":
    from mongodb import init_db
    init_db()
    d=DailyScreening()
    d.test_save_db()