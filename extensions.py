from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
csrf = CSRFProtect()
db = SQLAlchemy()


def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions with the application."""
    limiter.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    db.init_app(app)

    # Configure login manager
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Proszę się zalogować, aby uzyskać dostęp do tej strony."
    )
    login_manager.login_message_category = "info"
