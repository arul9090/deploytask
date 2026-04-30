import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.environ.get("MONGO_DB", "skillrank_db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "skillrank-super-secret-change-in-prod")
    JWT_SECRET = os.environ.get("JWT_SECRET", "skillrank-jwt-secret-change-in-prod")

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", SMTP_USERNAME)
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"
