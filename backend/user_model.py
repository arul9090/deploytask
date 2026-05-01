import datetime
from bson import ObjectId
from database import users
from services.role_service import get_user_permissions, get_user_roles, primary_role


def dicebear_url(seed: str) -> str:
    safe = seed.replace("@", "").replace(".", "")
    return f"https://api.dicebear.com/7.x/avataaars/svg?seed={safe}&backgroundColor=b6e3f4,c0aede,d1d4f9"


def serialize_user(user) -> dict:
    roles = get_user_roles(user)
    permissions = get_user_permissions(user)
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "dob": user.get("dob", ""),
        "bio": user.get("bio", ""),
        "role": primary_role(roles),
        "roles": roles,
        "permissions": permissions,
        "avatar_url": user.get("avatar_url") or dicebear_url(user.get("email", user.get("name", "user"))),
        "created_at": user.get("created_at", "").strftime("%d %b %Y")
        if isinstance(user.get("created_at"), datetime.datetime)
        else str(user.get("created_at", "")),
    }


def find_by_email(email: str):
    return users.find_one({"email": email})


def find_by_id(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    return users.find_one({"_id": ObjectId(user_id)})


def create_user(data: dict):
    now = datetime.datetime.utcnow()
    document = {
        "name": data["name"],
        "email": data["email"],
        "password_hash": data.get("password_hash"),
        "phone": data.get("phone", ""),
        "dob": data.get("dob", ""),
        "bio": data.get("bio", ""),
        "role": "user",
        "roles": ["user"],
        "permissions": [],
        "avatar_url": data.get("avatar_url") or dicebear_url(data["email"]),
        "auth_provider": data.get("auth_provider", "local"),
        "google_id": data.get("google_id", ""),
        "created_at": now,
    }
    result = users.insert_one(document)
    document["_id"] = result.inserted_id
    return document


def find_or_create_google_user(profile: dict):
    email = profile.get("email", "").strip().lower()
    if not email:
        return None, False

    user = find_by_email(email)
    if user:
        users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "auth_provider": user.get("auth_provider", "google"),
                    "google_id": profile.get("sub", user.get("google_id", "")),
                    "avatar_url": profile.get("picture", user.get("avatar_url", "")),
                }
            },
        )
        return find_by_email(email), False

    user = create_user({
        "name": profile.get("name") or email.split("@")[0],
        "email": email,
        "avatar_url": profile.get("picture") or dicebear_url(email),
        "auth_provider": "google",
        "google_id": profile.get("sub", ""),
    })
    return user, True


def list_users():
    return [serialize_user(user) for user in users.find().sort("created_at", -1)]


def paginated_users(page: int, per_page: int):
    per_page = min(per_page, 100)
    skip = (page - 1) * per_page
    total = users.count_documents({})
    total_pages = (total + per_page - 1) // per_page
    cursor = users.find().sort("created_at", -1).skip(skip).limit(per_page)
    page_users = [serialize_user(user) for user in cursor]
    return {
        "count": len(page_users),
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "users": page_users,
    }


def update_roles(user_id: str, roles: list[str]):
    if not ObjectId.is_valid(user_id):
        return None

    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "roles": roles,
                "role": primary_role(roles),
                "permissions": [],
            }
        },
    )
    if result.matched_count == 0:
        return None
    return find_by_id(user_id)


def update_profile(user_id: str, data: dict):
    if not ObjectId.is_valid(user_id):
        return None

    update_data = {}
    if "name" in data: update_data["name"] = data["name"].strip()
    if "phone" in data: update_data["phone"] = data["phone"].strip()
    if "dob" in data: update_data["dob"] = data["dob"].strip()
    if "bio" in data: update_data["bio"] = data["bio"].strip()

    if not update_data:
        return find_by_id(user_id)

    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return find_by_id(user_id)
