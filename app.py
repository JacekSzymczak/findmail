import os

from dotenv import dotenv_values
from flask import Flask, jsonify

from api.auth import auth_bp
from api.invitation_keys import invitation_keys_bp
from api.mailboxes import mailboxes_bp
from api.messages import messages_bp
from extensions import (
    exempt_blueprints,
    init_extensions,
    login_manager,
)
from services.auth_service import AuthService


def create_app(database_uri=None):
    app = Flask(__name__)

    # Load environment variables ONLY from .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_config = dotenv_values(env_path)

    # Set secret key from environment or generate a secure one
    app.secret_key = env_config.get("SECRET_KEY") or os.urandom(24)

    # Securely load database configuration from .env file
    db_config = {
        "user": env_config.get("DB_USER"),
        "password": env_config.get("DB_PASSWORD"),
        "host": env_config.get("DB_HOST", "localhost"),
        "port": env_config.get("DB_PORT", "3306"),
        "database": env_config.get("DB_NAME"),
    }

    # Validate required database configuration
    required_keys = ["user", "password", "host", "database"]
    missing_keys = [key for key in required_keys if not db_config[key]]

    if missing_keys:
        raise ValueError(
            f"Missing required database configuration: {', '.join(missing_keys)}"
        )

    # Construct database URI
    database_uri = database_uri or env_config.get(
        "DATABASE_URL",
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}",
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Load IMAP configuration
    app.config["IMAP_HOST"] = env_config.get("IMAP_HOST")
    app.config["IMAP_PORT"] = int(env_config.get("IMAP_PORT", "993"))
    app.config["IMAP_USER"] = env_config.get("IMAP_USER")
    app.config["IMAP_PASSWORD"] = env_config.get("IMAP_PASSWORD")
    app.config["IMAP_USE_SSL"] = (
        env_config.get("IMAP_USE_SSL", "true").lower() == "true"
    )

    # Configure logging
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Test database connection
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError, SQLAlchemyError

        # Create SQLAlchemy engine
        engine = create_engine(database_uri)

        # Attempt to connect to the database
        with engine.connect() as connection:
            # Use text() to create a proper executable SQL statement
            result = connection.execute(text("SELECT 1"))
            # Fetch the result to ensure the query works
            result.fetchone()
            logger.info("Successfully connected to database")

    except OperationalError as oe:
        logger.error(f"Database connection error: {oe}")
        raise
    except SQLAlchemyError as se:
        logger.error(f"SQLAlchemy error during database connection: {se}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {e}")
        raise

    # Initialize extensions
    init_extensions(app)

    # Register API blueprints
    app.register_blueprint(invitation_keys_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mailboxes_bp)
    app.register_blueprint(messages_bp)

    # Exempt blueprints from CSRF protection after registration
    exempt_blueprints(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return AuthService.get_user_by_id(int(user_id))

    # Centralized error handler
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return app


# Create application instance for Flask CLI
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
