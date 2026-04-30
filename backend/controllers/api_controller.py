from flask import Blueprint, jsonify, request
from models import user_model
from services.auth_service import jwt_permission_required, jwt_required, login_with_password
from services.role_service import ROLE_PERMISSIONS, get_user_permissions, get_user_roles, normalize_roles
from services.token_service import generate_jwt

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/token", methods=["GET", "POST"])
def api_token():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = login_with_password(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({
        "token": generate_jwt(user),
        "roles": get_user_roles(user),
        "permissions": get_user_permissions(user),
    })


@api_bp.get("/users")
@jwt_permission_required("users:read")
def api_users():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"error": "page and per_page must be valid integers"}), 400

    if page < 1:
        return jsonify({"error": "page must be greater than or equal to 1"}), 400
    if per_page < 1:
        return jsonify({"error": "per_page must be greater than or equal to 1"}), 400

    return jsonify(user_model.paginated_users(page, per_page))


@api_bp.patch("/users/<user_id>/roles")
@jwt_permission_required("users:update_roles")
def api_update_user_roles(user_id):
    requested_roles = normalize_roles((request.get_json(silent=True) or {}).get("roles"))
    unknown_roles = [role for role in requested_roles if role not in ROLE_PERMISSIONS]
    if unknown_roles:
        return jsonify({
            "error": "Unknown role provided",
            "allowed_roles": sorted(ROLE_PERMISSIONS.keys()),
            "unknown_roles": unknown_roles,
        }), 400

    updated_user = user_model.update_roles(user_id, requested_roles)
    if not updated_user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "message": "User roles updated",
        "user": user_model.serialize_user(updated_user),
    })


@api_bp.get("/me")
@jwt_required
def api_me():
    user = user_model.find_by_id(request.jwt_payload.get("sub", ""))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_model.serialize_user(user))
