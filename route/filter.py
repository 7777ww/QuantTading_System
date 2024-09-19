from flask import Blueprint, jsonify, render_template
from model.daily import DailyScreening
from datetime import datetime
from service import SymbolService

filter_blueprint = Blueprint('filter', __name__)



@filter_blueprint.route('/get_daily_screening/<strategy_name>', methods=['GET'])
def get_daily_screening(strategy_name):
    try:
        # 檢查是否有傳入策略名稱
        if not strategy_name:
            return jsonify({"error": "未提供策略名稱"}), 400

        # 根據策略名稱獲取今天的篩選結果
        daily_screening = SymbolService.get_daily_screening(strategy_name)

        if daily_screening:
            # 如果找到了今天的篩選結果，將其轉換為列表格式
            result_list = []

            # 如果篩選結果為空，直接返回空結果
            if daily_screening.is_empty:
                return render_template('filter.html', result=[]), 200

            # 如果有篩選結果，構建結果列表
            for i in range(len(daily_screening.symbols)):
                result_list.append({
                    "symbol": daily_screening.symbols[i],
                    "rs_value": daily_screening.rs_values[i],
                    "volume": daily_screening.volumes[i],
                    "moving_avg_volume": daily_screening.moving_avg_volumes[i]
                })

            # 返回結果渲染到模板
            return render_template('filter.html', result=result_list), 200

        else:
            # 如果沒有找到今天的篩選結果，調用篩選邏輯
            result_list = SymbolService.run_symbol_filter(top_n=20, moving_avg_period=5)
            
            if result_list:
                # 如果有篩選結果，保存並渲染結果
                SymbolService.save_to_db(result_list, strategy_name)
                return render_template('filter.html', result=result_list), 200
            else:
                # 如果沒有符合條件的篩選結果，顯示空結果
                print("今天沒有符合條件的篩選結果")
                SymbolService.save_to_db([], strategy_name)
                return render_template('filter.html', result=[]), 200

    except Exception as e:
        # 捕捉例外，返回500錯誤
        print(f"獲取每日篩選結果時發生錯誤: {str(e)}")
        return jsonify({"error": f"獲取每日篩選結果時發生錯誤: {str(e)}"}), 500
