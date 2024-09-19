from flask import Blueprint, jsonify, Response,request
from service import RSAnalyzer
from binance_api.rs import create_rs_dataframe, save_rs_to_db
import json
import time


rs_blueprint = Blueprint('rs', __name__)
rs_service = RSAnalyzer()


@rs_blueprint.route('/calculate_rs', methods=['GET'])
def calculate_rs():
    try:
        rs_df = create_rs_dataframe()
        save_rs_to_db(rs_df)
        return jsonify({"message": "RS數據已成功計算並保存到數據庫"}), 200
    except Exception as e:
        return jsonify({"error": f"計算RS時發生錯誤: {str(e)}"}), 500

@rs_blueprint.route('/top', methods=['GET'])
def get_top_rs():
    """
    獲取RS值最高的交易對。
    參數:
    - n: 要篩選的交易對數量 (默認為 10)
    - strategy_name: 可選的策略名稱 (默認為 'RS_Selection')
    """
    try:
        # 從查詢參數中提取 n 和 strategy_name
        n = int(request.args.get('n', 10))  # 默認返回10個交易對
        strategy_name = request.args.get('strategy_name', 'RS_Selection')  # 默認策略名稱

        # 使用已經創建的 RSAnalyzer 實例進行篩選
        top_rs_pairs = rs_service.get_top_rs_pairs(n=n)
        rs_service.save_rs_pairs_to_db(top_rs_pairs,strategy_name=strategy_name)


        return jsonify({
            'message': f'成功從幣安獲取前 {n} 個RS值最高的交易對並寫入資料庫',
            'strategy_name': strategy_name,
            'result': json.dumps(top_rs_pairs)  # 以 JSON 格式返回結果
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rs_blueprint.route('/get_rs_from_db', methods=['GET'])
def get_rs_from_db():
    """
    從數據庫中獲取RS值。
    參數:
    - strategy_name: 可選的策略名稱 (默認為 'RS_Selection')
    """
    try:
        # 從查詢參數中提取 strategy_name
        strategy_name = request.args.get('strategy_name', 'RS_Selection')  # 默認策略名稱
        date = request.args.get('date', None)  # 默認為 None，如果提供，將使用此日期
        # 檢查是否提供了 date
        if date:
            # 在這裡你可以添加日期格式驗證
            # rs_service 可以根據 date 來查詢相關的 RS 值
            rs_data = rs_service.get_rs_from_db(strategy_name=strategy_name, date=date)
            return jsonify({
            'message': f'成功從資料庫中獲取{date}的RS值前10',
            'strategy_name': strategy_name,
            'result': json.dumps(rs_data)  # 以 JSON 格式返回結果
        }), 200

        else:
            # 如果沒有提供 date，則不進行日期篩選
            rs_data = rs_service.get_rs_from_db(strategy_name=strategy_name)
            return jsonify({
            'message': f'成功從資料庫中獲取今天RS值前10',
            'strategy_name': strategy_name,
            'result': json.dumps(rs_data)  # 以 JSON 格式返回結果
        }), 200


        # 創建 RSAnalyzer 實例並從數據庫中獲取RS值


        

    except Exception as e:
        return jsonify({'error': str(e)}), 500
