from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
import mongodb
from model import UserModel
from schemas import UserSchema

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

