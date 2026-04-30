ROLE_PERMISSIONS = {
    "user": ["profile:read"],
    "admin": ["profile:read", "users:read", "users:update_roles"],
}


def normalize_roles(raw_roles) -> list[str]:
    if isinstance(raw_roles, list):
        roles = [str(role).strip().lower() for role in raw_roles if str(role).strip()]
    elif isinstance(raw_roles, str) and raw_roles.strip():
        roles = [raw_roles.strip().lower()]
    else:
        roles = ["user"]

    return sorted(set(roles))


def permissions_for_roles(roles: list[str]) -> list[str]:
    permissions = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, []))
    return sorted(permissions)


def get_user_roles(user) -> list[str]:
    return normalize_roles(user.get("roles", user.get("role", "user")))


def get_user_permissions(user) -> list[str]:
    role_permissions = permissions_for_roles(get_user_roles(user))
    direct_permissions = user.get("permissions", [])
    if not isinstance(direct_permissions, list):
        direct_permissions = []
    return sorted(set(role_permissions + direct_permissions))


def primary_role(roles: list[str]) -> str:
    return "admin" if "admin" in roles else roles[0]


def has_permission(user, permission: str) -> bool:
    return permission in get_user_permissions(user)
