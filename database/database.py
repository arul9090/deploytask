import certifi
from pymongo import MongoClient
try:
    from config import Config
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
    from config import Config


def create_mongo_client():
    options = {"serverSelectionTimeoutMS": 5000}
    if Config.MONGO_URI.startswith("mongodb+srv://"):
        options["tlsCAFile"] = certifi.where()
    return MongoClient(Config.MONGO_URI, **options)


client = create_mongo_client()
db = client[Config.MONGO_DB]
users = db["users"]
