import pytest
from dotenv import load_dotenv

from app import create_app
from extensions import db as _db

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def app():
    """Session-wide test 'Flask' application."""
    app = create_app(database_uri="sqlite:///:memory:", testing=True)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["RATELIMIT_ENABLED"] = False
    with app.app_context():
        _db.create_all()
    yield app
    # No need to drop_all here, will be handled per test


@pytest.fixture(scope="session")
def db():
    """Udostępnia obiekt bazy danych dla testów."""
    from extensions import db as _db

    return _db


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean all tables before each test."""
    with app.app_context():
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
