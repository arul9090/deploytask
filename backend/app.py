from flask import Flask
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
import sys
import os

# Add the parent directory to sys.path to allow importing from 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from controllers.api_controller import api_bp
from controllers.auth_controller import auth_bp
from controllers.web_controller import web_bp
from database.database import client
from extensions import bcrypt, oauth


def create_app():
    app = Flask(__name__, template_folder='../frontend/templates')
    app.config.from_object(Config)

    bcrypt.init_app(app)
    oauth.init_app(app)

    if Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    return app


app = create_app()


if __name__ == "__main__":
    try:
        client.admin.command("ping")
    except OperationFailure as exc:
        print("Error: MongoDB authentication failed.")
        print(f"Details: {exc}")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        print("Error: Could not connect to MongoDB.")
        print(f"URI in use: {Config.MONGO_URI}")
        print(f"Details: {exc}")
    else:
        print("[OK] Connected to MongoDB.")
        print("     Running at http://localhost:5000 (v2-pagination-fixed)")
        app.run(debug=True, use_reloader=True)
