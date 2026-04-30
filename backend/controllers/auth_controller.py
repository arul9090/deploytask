from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from config import Config
from extensions import oauth
from models import user_model
from services.auth_service import login_with_password, register_local_user, start_user_session
from services.mail_service import send_welcome_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = login_with_password(email, password)
        if user:
            start_user_session(user)
            return redirect(url_for("web.dashboard"))
        flash("Invalid email or password.", "danger")

    return render_template("login.html", google_enabled=google_is_configured())


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        user, error = register_local_user(request.form)
        if error:
            flash(error, "danger")
            return redirect(url_for("auth.login"))
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.get("/auth/google")
def google_login():
    if not google_is_configured():
        flash("Google Sign-In is not configured yet.", "warning")
        return redirect(url_for("auth.login"))
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.get("/auth/google/callback")
def google_callback():
    if not google_is_configured():
        flash("Google Sign-In is not configured yet.", "warning")
        return redirect(url_for("auth.login"))

    token = oauth.google.authorize_access_token()
    profile = token.get("userinfo")
    if profile is None:
        profile = oauth.google.userinfo()

    user, created = user_model.find_or_create_google_user(profile)
    if not user:
        flash("Google did not return a valid email address.", "danger")
        return redirect(url_for("auth.login"))

    if created:
        try:
            send_welcome_email(user)
        except Exception as exc:
            print(f"Warning: welcome email failed for {user.get('email')}: {exc}")

    start_user_session(user)
    return redirect(url_for("web.dashboard"))


def google_is_configured() -> bool:
    return bool(Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET)
