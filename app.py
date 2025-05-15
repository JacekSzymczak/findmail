import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from api.auth import auth_bp
from api.invitation_keys import invitation_keys_bp
from api.mailboxes import mailboxes_bp
from api.messages import messages_bp
from extensions import csrf, db, limiter, login_manager

# Load environment variables
load_dotenv()


def create_app(database_uri=None):
    app = Flask(__name__)
    # Load configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri or os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/findmail"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    limiter.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    # Redirect unauthorized users to login
    login_manager.login_view = "auth.login"

    # Register API blueprints
    app.register_blueprint(invitation_keys_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mailboxes_bp)
    app.register_blueprint(messages_bp)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from services.auth_service import AuthService

        return AuthService.get_user_by_id(int(user_id))

    # Centralized error handler
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return app


# Create application instance for Flask CLI
app = create_app()
