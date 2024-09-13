from flask import Blueprint, jsonify, Response

from binance_api.rs import create_rs_dataframe, save_rs_to_db
import json
import time


rs_blueprint = Blueprint('rs', __name__)

@rs_blueprint.route('/calculate_rs', methods=['GET'])
def calculate_rs():
    try:
        rs_df = create_rs_dataframe()
        save_rs_to_db(rs_df)
        return jsonify({"message": "RS數據已成功計算並保存到數據庫"}), 200
    except Exception as e:
        return jsonify({"error": f"計算RS時發生錯誤: {str(e)}"}), 500

@rs_blueprint.route('/get_top_rs', methods=['GET'])
def get_top_rs():
    try:
        # 創建一個進度條
        progress = 0
        total_pairs = 0
        processed_pairs = 0

        def update_progress():
            nonlocal total_pairs, processed_pairs
            while processed_pairs < total_pairs:
                remaining = total_pairs - processed_pairs
                yield f"data: 還有 {remaining} 個交易對需要下載\n\n"
                time.sleep(0.5)

        # 開始流式響應
        def generate():
            yield "Content-Type: text/event-stream\n\n"
            yield from update_progress()
            
            rs_df = create_rs_dataframe()
            top_rs = get_top_rs_pairs(rs_df)
            
            yield f"data: 100\n\n"
            yield f"data: {json.dumps(top_rs)}\n\n"
            
            # 移除了 to_dict() 方法的調用，因為 top_rs 是一個列表對象
            yield f"data: {json.dumps(top_rs)}\n\n"

        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({"error": f"獲取頂級RS時發生錯誤: {str(e)}"}), 500
