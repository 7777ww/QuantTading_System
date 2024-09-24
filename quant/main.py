from flask import Flask, jsonify, request, Response,render_template
import threading
import time
import pandas as pd
import sys
from flask_jwt_extended import JWTManager



from route.rs import rs_blueprint
from route.kline import kline_blueprint
from route.filter import filter_blueprint

# 註冊RS藍圖
from flask import Flask
from route.rs import rs_blueprint
from route.kline import kline_blueprint
from route.filter import filter_blueprint
from route.user import blp as User_blueprint

def create_app():
    app = Flask(__name__, template_folder='templates')

    # 設定 JWT 的秘密金鑰
    app.config["JWT_SECRET_KEY"] = "jose"  # 先初始化 app 再進行配置

    # 註冊 Blueprint
    app.register_blueprint(rs_blueprint, url_prefix='/rs')
    app.register_blueprint(kline_blueprint, url_prefix='/kline')
    app.register_blueprint(filter_blueprint, url_prefix='/filter')
    app.register_blueprint(User_blueprint) 

    # 主頁面路由
    @app.route('/')
    def main():
        return render_template("homepage.html")

    # 初始化 JWTManager
    jwt = JWTManager(app)

    return app

app = create_app()
app.run(debug=True)
