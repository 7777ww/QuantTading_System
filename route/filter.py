from flask import Blueprint, jsonify, render_template
from model.daily import DailyScreening
from datetime import datetime

filter_blueprint = Blueprint('filter', __name__)

@filter_blueprint.route('/get_daily_screening', methods=['GET'])
def get_daily_screening():
    try:
        # 獲取今天的日期
        today = datetime.now().date()
        
        # 從數據庫中檢索今天的篩選結果
        daily_screening = DailyScreening.objects(date=today).first()
        
        if daily_screening:
            # 如果找到了今天的篩選結果，將其轉換為字典格式
            result = {
                "date": daily_screening.date.isoformat(),
                "symbols": daily_screening.symbols,
                "rs_values": daily_screening.rs_values,
                "volumes": daily_screening.volumes,
                "moving_avg_volumes": daily_screening.moving_avg_volumes
            }
            # 將結果轉換為列表格式，以便在模板中使用
            result_list = []
            for i in range(len(daily_screening.symbols)):
                result_list.append({
                    "symbol": daily_screening.symbols[i],
                    "rs_value": daily_screening.rs_values[i],
                    "volume": daily_screening.volumes[i],
                    "moving_avg_volume": daily_screening.moving_avg_volumes[i]
                })
            return render_template('filter.html', result=result_list), 200
        else:
            # 如果沒有找到今天的篩選結果
            # 如果沒有找到今天的篩選結果，調用 filter_symbols 方法
            from binance_api.filter import SymbolFilter
            
            filter = SymbolFilter(interval='1d', moving_periods=1)
            filtered_results = filter.filter_symbols(top_n=20, moving_avg_period=5)
            
            if not filtered_results.empty:
                result_list = []
                for _, row in filtered_results.iterrows():
                    result_list.append({
                        "symbol": row['symbol'],
                        "rs_value": row['rs_value'],
                        "volume": row['volume'],
                        "moving_avg_volume": row['moving_avg_volume']
                    })
                return render_template('filter.html', result=result_list), 200
            else:
                print("今天沒有符合條件的篩選結果")
            return render_template('filter.html', result=None), 200
    except Exception as e:
        # 如果發生錯誤
        return jsonify({"error": f"獲取每日篩選結果時發生錯誤: {str(e)}"}), 500
