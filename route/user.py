from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
import mongodb
from model import UserModel
from schemas import UserSchema
from bson import ObjectId  # 需要引入 ObjectId 來處理 MongoDB 的 _id
from flask_jwt_extended import create_access_token


blp = Blueprint(
    "Users",  # 這是 Blueprint 的名稱，會顯示在 API 文件中（如 Swagger UI）
    "users",  # 這是 URL 前綴，所有屬於這個 Blueprint 的路由都會以 /users 開頭
    description="Operations on users"  # 這是 Blueprint 的描述，會出現在自動生成的 API 文件中
)

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        existing_user = UserModel.objects(username=user_data['name']).first()
        if existing_user:
            abort(409, message="User already registered.")
        user = UserModel(username=user_data['name'], password=pbkdf2_sha256.hash(user_data['password']))
        user.save()


        return {"message": "User created successfully."}, 201

        
@blp.route("/user/<string:user_id>")
class User(MethodView):
    def get(self, user_id):
        try:
            # 將 user_id 轉換為 ObjectId
            user = UserModel.objects(id=ObjectId(user_id)).first()
        except:
            abort(400, message="Invalid user ID format.")
        
        if not user:
            abort(404, message="User not found.")
        
        # 返回用戶信息
        return {
            "id": str(user.id),
            "username": user.username,
        }, 200

    def delete(self, user_id):
        try:
            # 將 user_id 轉換為 ObjectId
            user = UserModel.objects(id=ObjectId(user_id)).first()
        except:
            abort(400, message="Invalid user ID format.")
        
        if not user:
            abort(404, message="User not found.")
        
        user.delete()
        return {"message": "User deleted successfully."}, 200


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.objects(username=user_data['name']).first()
        if not user or not pbkdf2_sha256.verify(user_data['password'], user.password):
            abort(401, message="Invalid username or password.")
        access_token = create_access_token(identity=str(user.id))
        return {"message": "Login successful.", "access_token": access_token}, 200
 