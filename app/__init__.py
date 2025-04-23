import os
import secrets
from pathlib import Path
from flask import Flask
from .auth import auth_routes
from .routes import main_routes

def create_app():
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(__name__, template_folder=base_dir / "templates", static_folder=base_dir / "static")

    # Secret key for sessions
    secret_key = secrets.token_hex(16)
    app.secret_key = os.environ.get('SECRET_KEY', secret_key)

    app.jinja_env.globals.update(zip=zip)

    app.register_blueprint(auth_routes)
    app.register_blueprint(main_routes)
    return app
