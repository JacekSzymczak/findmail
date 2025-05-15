import pytest

from models import InvitationKey
from services.auth_service import AuthService
from services.invitation_key_service import InvitationKeyService


def create_invitation_key_in_db(db, key_value):
    key = InvitationKey(key=key_value)
    db.session.add(key)
    db.session.commit()
    return key_value


def test_create_list_delete_invitation_key(app, db, subtests):
    """Test tworzenia, listowania i usuwania kluczy zaproszeń.

    Sprawdza:
    - Tworzenie nowego klucza
    - Poprawne listowanie kluczy
    - Usuwanie klucza
    """
    with app.app_context():
        # Ręcznie dodajemy pierwszy klucz zaproszenia do bazy
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")

        with subtests.test("Tworzenie nowego klucza"):
            invitation = InvitationKeyService.create_invitation_key()
            key = invitation.key
            assert key in InvitationKeyService.list_unused()

        with subtests.test("Usuwanie klucza"):
            deleted = InvitationKeyService.delete_invitation_key(key)
            assert deleted is True

        with subtests.test("Usuwanie nieistniejącego klucza zwraca False"):
            deleted = InvitationKeyService.delete_invitation_key("nonexistent")
            assert deleted is False


def test_create_invitation_key_as_admin(app, db):
    """Test creating invitation key as admin."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")

        # Create invitation key
        new_invitation = InvitationKeyService.create_invitation_key()
        assert new_invitation.key in InvitationKeyService.list_unused()


def test_create_invitation_key_as_non_admin(app, db):
    """Test creating invitation key as non-admin."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")
        user_key = InvitationKeyService.create_invitation_key().key
        AuthService.register("user@example.com", "password123", user_key)
        AuthService.login("user@example.com", "password123")

        # Try to create invitation key
        with pytest.raises(ValueError) as exc_info:
            InvitationKeyService.create_invitation_key()
        assert str(exc_info.value) == "Brak uprawnień administratora"


def test_list_invitation_keys_as_admin(app, db):
    """Test listing invitation keys as admin."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")
        invitation = InvitationKeyService.create_invitation_key()
        key = invitation.key

        # List invitation keys
        keys = InvitationKeyService.list_unused()
        assert key in keys


def test_list_invitation_keys_as_non_admin(app, db):
    """Test listing invitation keys as non-admin."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")
        user_key = InvitationKeyService.create_invitation_key().key
        AuthService.register("user@example.com", "password123", user_key)
        AuthService.login("user@example.com", "password123")

        # Try to list invitation keys
        with pytest.raises(ValueError) as exc_info:
            InvitationKeyService.list_unused()
        assert str(exc_info.value) == "Brak uprawnień administratora"


def test_delete_invitation_key_as_admin(app, db):
    """Test deleting invitation key as admin."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")
        invitation = InvitationKeyService.create_invitation_key()
        key = invitation.key

        # Delete invitation key
        deleted = InvitationKeyService.delete_invitation_key(key)
        assert deleted is True


def test_delete_invitation_key_as_non_admin(app, db):
    """Test deleting invitation key as non-admin."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")
        user_key = InvitationKeyService.create_invitation_key().key
        AuthService.register("user@example.com", "password123", user_key)
        AuthService.login("user@example.com", "password123")
        AuthService.login("admin@example.com", "password123")
        to_delete = InvitationKeyService.create_invitation_key()
        AuthService.login("user@example.com", "password123")

        # Try to delete invitation key
        with pytest.raises(ValueError) as exc_info:
            InvitationKeyService.delete_invitation_key(to_delete.key)
        assert str(exc_info.value) == "Brak uprawnień administratora"


def test_delete_nonexistent_invitation_key(app, db):
    """Test deleting non-existent invitation key."""
    with app.app_context():
        admin_key = create_invitation_key_in_db(db, "admin-key")
        admin = AuthService.register("admin@example.com", "password123", admin_key)
        admin.is_admin = True
        db.session.commit()
        AuthService.login("admin@example.com", "password123")

        # Try to delete non-existent key
        deleted = InvitationKeyService.delete_invitation_key("nonexistent")
        assert deleted is False
