from flask import Blueprint, jsonify, request
from mongodb.get_data import get_ohlcv_data_as_df
from flask import render_template


kline_blueprint = Blueprint('kline', __name__, template_folder='templates')

@kline_blueprint.route('/get_kline', methods=['GET'])
def get_kline():
    try:
        from dateutil.parser import parse
        from datetime import datetime, timedelta

        symbol = request.args.get('symbol')
        interval = request.args.get('interval')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if not all([symbol, interval]):
            return jsonify({"error": "缺少必要的參數 symbol 或 interval"}), 400

        # 解析 start_time 和 end_time


  

        df = get_ohlcv_data_as_df(symbol, interval, start_time, end_time)
        
        if df.empty:
            return jsonify({"error": "未找到符合條件的數據"}), 404

        kline_data = df.reset_index().to_dict(orient='records')
        return jsonify({"data": kline_data}), 200

    except Exception as e:
        return jsonify({"error": f"獲取K線數據時發生錯誤: {str(e)}"}), 500

@kline_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        interval = request.form.get('interval')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        return redirect(url_for('kline.get_kline', symbol=symbol, interval=interval, start_time=start_time, end_time=end_time))
    return render_template('get_kline.html')