from flask import Flask, jsonify, request, Response
import threading
import time
import pandas as pd
import sys
print(sys.path) 
app = Flask(__name__)
from model import OHLCV


from route.rs import rs_blueprint
from route.kline import kline_blueprint
from route.filter import filter_blueprint

# 註冊RS藍圖
app.register_blueprint(rs_blueprint, url_prefix='/rs')
app.register_blueprint(kline_blueprint, url_prefix='/kline')
app.register_blueprint(filter_blueprint, url_prefix='/filter')
@app.route('/')
def main():
    return jsonify({
        "message": "歡迎使用量化交易系統",
        "available_endpoints": [
            {
                "path": "/rs/calculate_rs",
                "method": "GET",
                "description": "計算相對強度（RS）並保存到數據庫"
            },
            {
                "path": "/rs/get_top_rs",
                "method": "GET",
                "description": "獲取頂級相對強度（RS）交易對"
            },
            {
                "path": "/kline/get_kline",
                "method": "GET",
                "description": "獲取K線數據"
            }
        ]
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
    # def start_background_tasks():
    #     # 在這裡添加需要在背景執行的任務
    #     pass

    # # 創建並啟動背景任務線程
    # background_thread = threading.Thread(target=start_background_tasks)
    # background_thread.daemon = True
    # background_thread.start()

    # # 啟動Flask應用
    # app.run(debug=True)




