from functools import wraps
from flask import flash, jsonify, redirect, request, session, url_for
from extensions import bcrypt
from models import user_model
from services.mail_service import send_welcome_email
from services.role_service import get_user_permissions, get_user_roles, primary_role
from services.token_service import decode_jwt


def start_user_session(user):
    roles = get_user_roles(user)
    session["user_id"] = str(user["_id"])
    session["role"] = primary_role(roles)
    session["roles"] = roles
    session["permissions"] = get_user_permissions(user)
    session["name"] = user.get("name", "")


def login_with_password(email: str, password: str):
    user = user_model.find_by_email(email)
    if not user or not user.get("password_hash"):
        return None
    if not bcrypt.check_password_hash(user["password_hash"], password):
        return None
    return user


def register_local_user(form_data):
    name = form_data.get("name", "").strip()
    email = form_data.get("email", "").strip().lower()
    password = form_data.get("password", "")
    phone = form_data.get("phone", "").strip()
    dob = form_data.get("dob", "").strip()
    bio = form_data.get("bio", "").strip()

    if not all([name, email, password]):
        return None, "Name, email, and password are required."
    if user_model.find_by_email(email):
        return None, "An account with that email already exists."

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = user_model.create_user({
        "name": name,
        "email": email,
        "password_hash": hashed,
        "phone": phone,
        "dob": dob,
        "bio": bio,
    })

    try:
        send_welcome_email(user)
    except Exception as exc:
        print(f"Warning: welcome email failed for {email}: {exc}")

    return user, None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if "users:read" not in session.get("permissions", []):
            flash("Admin access required.", "danger")
            return redirect(url_for("web.profile"))
        return f(*args, **kwargs)
    return decorated


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        payload = decode_jwt(auth_header.split(" ", 1)[1])
        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        request.jwt_payload = payload
        return f(*args, **kwargs)
    return decorated


def jwt_permission_required(permission: str):
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated(*args, **kwargs):
            permissions = request.jwt_payload.get("permissions", [])
            if permission not in permissions:
                return jsonify({"error": f"Permission required: {permission}"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
