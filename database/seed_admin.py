"""
Run this once to create a default admin account in MongoDB.
Usage:  python seed_admin.py
Then login with  admin@skillrank.com / admin123
"""
import os, datetime, certifi
from pymongo import MongoClient
from flask_bcrypt import generate_password_hash
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
load_dotenv(dotenv_path=dotenv_path)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.environ.get("MONGO_DB", "skillrank_db")

options = {"serverSelectionTimeoutMS": 5000}
if MONGO_URI.startswith("mongodb+srv://"):
    options["tlsCAFile"] = certifi.where()

client = MongoClient(MONGO_URI, **options)
db     = client[DB_NAME]
users  = db["users"]

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@skillrank.com")
ADMIN_PASS  = os.environ.get("ADMIN_PASS", "admin123")

if users.find_one({"email": ADMIN_EMAIL}):
    users.update_one(
        {"email": ADMIN_EMAIL},
        {
            "$set": {
                "role": "admin",
                "roles": ["admin"],
                "permissions": [],
            }
        }
    )
    print(f"[OK] Admin account already exists and roles were refreshed: {ADMIN_EMAIL}")
else:
    hashed = generate_password_hash(ADMIN_PASS).decode("utf-8")
    users.insert_one({
        "name":          "Admin",
        "email":         ADMIN_EMAIL,
        "password_hash": hashed,
        "phone":         "+91 9000000000",
        "dob":           "1990-01-01",
        "bio":           "SkillRank platform administrator.",
        "role":          "admin",
        "roles":         ["admin"],
        "permissions":   [],
        "avatar_url":    "https://api.dicebear.com/7.x/avataaars/svg?seed=adminskillrank&backgroundColor=b6e3f4",
        "created_at":    datetime.datetime.utcnow(),
    })
    print(f"[OK] Admin created -> email: {ADMIN_EMAIL}  password: {ADMIN_PASS}")
