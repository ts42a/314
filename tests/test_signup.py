# tests/test_signup.py
import pytest
from werkzeug.security import check_password_hash

def test_signup_success(client):
    """
    Posting valid signup data should create a new user and log them in.
    """
    resp = client.post("/signup", data={
        "type": "user",
        "name": "New User",
        "email": "new@example.com",
        "password": "secret123",
        "confirm_password": "secret123"
    }, follow_redirects=True)

    # The response should show "Signup successful!"
    assert b"Signup successful!" in resp.data

    # Verify user in database
    from backend.models import User  # Fixed: Use User instead of Organizer
    with client.application.app_context():
        u = User.query.filter_by(email="new@example.com").first()
        assert u is not None
        assert u.role == "user"
        assert check_password_hash(u.password, "secret123")

def test_signup_password_mismatch(client):
    """
    Signup with mismatched passwords should fail.
    """
    resp = client.post("/signup", data={
        "type": "user",
        "name": "New User",
        "email": "new@example.com",
        "password": "secret123",
        "confirm_password": "different123"
    }, follow_redirects=True)

    # Should show error message
    assert b"Passwords do not match" in resp.data

    # Verify user was NOT created in database
    from backend.models import User
    with client.application.app_context():
        u = User.query.filter_by(email="new@example.com").first()
        assert u is None

def test_signup_duplicate_email(client, sample_user):
    """
    Signup with an email that already exists should fail.
    """
    resp = client.post("/signup", data={
        "type": "user",
        "name": "Another User",
        "email": "test@example.com",  # This email already exists from sample_user
        "password": "secret123",
        "confirm_password": "secret123"
    }, follow_redirects=True)

    # Should show error message
    assert b"Email already exists" in resp.data

def test_signup_organizer(client):
    """
    Signing up as an organizer should work correctly.
    """
    resp = client.post("/signup", data={
        "type": "organizer",
        "name": "New Organizer",
        "email": "neworg@example.com",
        "password": "secret123",
        "confirm_password": "secret123",
        "phone": "123-456-7890",
        "address": "123 Main St",
        "abn": "12345678901"  # ABN is only for organizers
    }, follow_redirects=True)

    # The response should show "Signup successful!"
    assert b"Signup successful!" in resp.data

    # Verify organizer in database
    from backend.models import User
    with client.application.app_context():
        u = User.query.filter_by(email="neworg@example.com").first()
        assert u is not None
        assert u.role == "organizer"
        assert u.phone == "123-456-7890"
        assert u.address == "123 Main St"
        assert u.abn == "12345678901"
        assert check_password_hash(u.password, "secret123")