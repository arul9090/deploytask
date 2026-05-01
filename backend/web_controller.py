from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import user_model
from services.auth_service import admin_required, login_required

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def index():
    if "user_id" in session:
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("auth.login"))


@web_bp.get("/dashboard")
@login_required
def dashboard():
    if "users:read" in session.get("permissions", []):
        return redirect(url_for("web.admin_dashboard"))
    return redirect(url_for("web.profile"))


@web_bp.get("/admin")
@admin_required
def admin_dashboard():
    print("DEBUG: admin_dashboard called")
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        page, per_page = 1, 10

    pagination = user_model.paginated_users(page, per_page)
    all_users_for_stats = user_model.list_users()
    
    stats = {
        "total": pagination["total"],
        "admins": sum(1 for user in all_users_for_stats if "admin" in user["roles"]),
        "newest": all_users_for_stats[0]["name"] if all_users_for_stats else "-",
    }
    
    return render_template(
        "dashboard_admin.html",
        all_users=pagination.get("users", []),
        pagination=pagination,
        stats=stats,
        admin_name=session.get("name", "Admin")
    )


@web_bp.get("/profile")
@login_required
def profile():
    user = user_model.find_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    return render_template("dashboard_user.html", user=user_model.serialize_user(user))


@web_bp.post("/profile/update")
@login_required
def update_profile():
    user_id = session["user_id"]
    data = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone"),
        "dob": request.form.get("dob"),
        "bio": request.form.get("bio")
    }
    
    updated_user = user_model.update_profile(user_id, data)
    if updated_user:
        session["name"] = updated_user.get("name", session.get("name"))
        flash("Profile updated successfully!", "success")
    else:
        flash("Failed to update profile.", "danger")
        
    return redirect(url_for("web.profile"))


@web_bp.route("/admin/users/<user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_user_role(user_id):
    user = user_model.find_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("web.admin_dashboard"))

    # Don't allow toggling yourself (to prevent locking yourself out)
    if str(user["_id"]) == session["user_id"]:
        flash("You cannot change your own role.", "warning")
        return redirect(url_for("web.admin_dashboard"))

    current_roles = user.get("roles", ["user"])
    if "admin" in current_roles:
        new_roles = ["user"]
        msg = f"User {user.get('email')} demoted to User."
    else:
        new_roles = ["user", "admin"]
        msg = f"User {user.get('email')} promoted to Admin."

    user_model.update_roles(user_id, new_roles)
    flash(msg, "success")
    return redirect(url_for("web.admin_dashboard"))
