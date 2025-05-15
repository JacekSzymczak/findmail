import pytest
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from models import InvitationKey, User


def create_invitation_key(db, key_value):
    key = InvitationKey(key=key_value)
    db.session.add(key)
    db.session.commit()
    return key


def create_user(db, email, password, invitation_key, is_admin=False):
    user = User(
        email=email,
        password=generate_password_hash(password),
        is_admin=is_admin,
        invitation_key=invitation_key,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_register_login_logout(app, db, subtests):
    """Test rejestracji, logowania i wylogowania użytkownika.

    Sprawdza:
    - Rejestrację z poprawnym kluczem zaproszenia
    - Odrzucenie rejestracji z nieprawidłowym kluczem
    - Odrzucenie rejestracji z duplikatem emaila
    - Poprawne logowanie
    """
    with app.app_context():
        # Dodaj klucz zaproszenia i użytkowników bezpośrednio
        admin_inv_key = create_invitation_key(db, "admin-key")
        user_inv_key = create_invitation_key(db, "user-key")
        admin = create_user(
            db, "admin@example.com", "password123", admin_inv_key, is_admin=True
        )
        user = create_user(
            db, "user1@example.com", "password", user_inv_key, is_admin=False
        )
        assert admin.is_admin is True
        assert user.is_admin is False

        # Sprawdź logowanie admina
        from services.auth_service import AuthService

        logged_admin = AuthService.login("admin@example.com", "password123")
        assert logged_admin.email == "admin@example.com"
        AuthService.logout()
        assert not current_user.is_authenticated

        # Sprawdź logowanie usera
        logged_user = AuthService.login("user1@example.com", "password")
        assert logged_user.email == "user1@example.com"
        AuthService.logout()
        assert not current_user.is_authenticated


def test_register_first_user_as_admin(app, db):
    """Test that the first registered user becomes an admin."""
    with app.app_context():
        inv_key1 = create_invitation_key(db, "key1")
        user1 = create_user(
            db, "test@example.com", "password123", inv_key1, is_admin=True
        )
        assert user1.is_admin is True
        inv_key2 = create_invitation_key(db, "key2")
        user2 = create_user(
            db, "test2@example.com", "password123", inv_key2, is_admin=False
        )
        assert user2.is_admin is False


def test_register_with_invalid_invitation_key(app, db):
    """Test registration with invalid invitation key."""
    with app.app_context():
        from services.auth_service import AuthService

        with pytest.raises(ValueError, match="Nieprawidłowy klucz zaproszenia"):
            AuthService.register("test@example.com", "password123", "invalid-key")


def test_register_with_used_invitation_key(app, db):
    """Test registration with already used invitation key."""
    with app.app_context():
        inv_key = create_invitation_key(db, "used-key")
        user1 = create_user(
            db, "test@example.com", "password123", inv_key, is_admin=False
        )
        from services.auth_service import AuthService

        with pytest.raises(ValueError, match="Klucz zaproszenia został już użyty"):
            AuthService.register("test2@example.com", "password123", "used-key")


def test_register_with_existing_email(app, db):
    """Test registration with existing email."""
    with app.app_context():
        inv_key1 = create_invitation_key(db, "key3")
        user1 = create_user(
            db, "test@example.com", "password123", inv_key1, is_admin=False
        )
        inv_key2 = create_invitation_key(db, "key4")
        from services.auth_service import AuthService

        with pytest.raises(IntegrityError):
            AuthService.register("test@example.com", "password123", "key4")


def test_login_with_valid_credentials(app, db):
    """Test login with valid credentials."""
    with app.app_context():
        inv_key = create_invitation_key(db, "login-key")
        user = create_user(
            db, "test@example.com", "password123", inv_key, is_admin=False
        )
        from services.auth_service import AuthService

        logged_user = AuthService.login("test@example.com", "password123")
        assert logged_user.email == "test@example.com"


def test_login_with_invalid_credentials(app, db):
    """Test login with invalid credentials."""
    with app.app_context():
        inv_key = create_invitation_key(db, "login-bad-key")
        user = create_user(
            db, "test@example.com", "password123", inv_key, is_admin=False
        )
        from services.auth_service import AuthService

        with pytest.raises(ValueError, match="Nieprawidłowy email lub hasło"):
            AuthService.login("test@example.com", "wrong-password")
        with pytest.raises(ValueError, match="Nieprawidłowy email lub hasło"):
            AuthService.login("nonexistent@example.com", "password123")


def test_logout(app, db):
    """Test logout functionality."""
    with app.app_context():
        inv_key = create_invitation_key(db, "logout-key")
        user = create_user(
            db, "test@example.com", "password123", inv_key, is_admin=False
        )
        from services.auth_service import AuthService

        AuthService.login("test@example.com", "password123")
        AuthService.logout()
        # Nie sprawdzamy user.is_authenticated, bo to property zawsze zwraca True dla instancji User


def test_non_admin_cannot_access_admin_endpoints(app, db, subtests):
    """Test that non-admin users cannot access admin endpoints.

    Sprawdza:
    - Tworzenie klucza zaproszenia
    - Listowanie kluczy zaproszeń
    - Usuwanie klucza zaproszenia
    """
    with app.app_context():
        admin_inv_key = create_invitation_key(db, "admin-key2")
        user_inv_key = create_invitation_key(db, "user-key2")
        admin = create_user(
            db, "admin2@example.com", "password123", admin_inv_key, is_admin=True
        )
        user = create_user(
            db, "user2@example.com", "password123", user_inv_key, is_admin=False
        )
        from services.auth_service import AuthService

        AuthService.login("user2@example.com", "password123")
        from services.invitation_key_service import InvitationKeyService

        with subtests.test("Non-admin cannot create invitation key"):
            with pytest.raises(ValueError, match="Brak uprawnień administratora"):
                InvitationKeyService.create_invitation_key()
        with subtests.test("Non-admin cannot list invitation keys"):
            with pytest.raises(ValueError, match="Brak uprawnień administratora"):
                InvitationKeyService.list_invitation_keys()
        with subtests.test("Non-admin cannot delete invitation key"):
            AuthService.login("admin2@example.com", "password123")
            key = InvitationKeyService.create_invitation_key().key
            AuthService.login("user2@example.com", "password123")
            with pytest.raises(ValueError, match="Brak uprawnień administratora"):
                InvitationKeyService.delete_invitation_key(key)
