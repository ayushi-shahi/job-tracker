from flask import Flask
from app.config import config_map
from app.extensions import db, migrate, jwt
import os
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    env = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_map[env])

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register models so Flask-Migrate can detect them
    from app.models import User, JobApplication, StatusHistory  # noqa: F401

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.applications import applications_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(applications_bp, url_prefix="/applications")

    return app