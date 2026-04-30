import datetime
import jwt
from config import Config
from services.role_service import get_user_permissions, get_user_roles


def generate_jwt(user) -> str:
    payload = {
        "sub": str(user["_id"]),
        "roles": get_user_roles(user),
        "permissions": get_user_permissions(user),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
