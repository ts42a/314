# tests/test_login.py
import pytest

def test_login_success(client, sample_user):
    """
    Logging in with correct credentials for a 'user' should succeed.
    """
    resp = client.post("/login", data={
        "type": "user",
        "email": "test@example.com",  # Use the actual email from fixture
        "password": "testpass"
    }, follow_redirects=True)

    assert b"Logged in successfully!" in resp.data

def test_login_wrong_password(client, sample_user):
    """
    Login with incorrect password should fail.
    """
    resp = client.post("/login", data={
        "type": "user",
        "email": "test@example.com",
        "password": "wrongpass"
    }, follow_redirects=True)

    assert b"Invalid credentials or role" in resp.data

def test_login_wrong_role(client, sample_user):
    """
    Login as 'organizer' when account is actually role='user' should fail.
    """
    resp = client.post("/login", data={
        "type": "organizer",
        "email": "test@example.com",
        "password": "testpass"
    }, follow_redirects=True)

    assert b"Invalid credentials or role" in resp.data

def test_organizer_login_success(client, sample_organizer):
    """
    Logging in with correct credentials for an 'organizer' should succeed.
    """
    resp = client.post("/login", data={
        "type": "organizer",
        "email": "org@example.com",
        "password": "testpass"
    }, follow_redirects=True)

    assert b"Logged in successfully!" in resp.data

def test_login_nonexistent_user(client):
    """
    Login with email that doesn't exist should fail.
    """
    resp = client.post("/login", data={
        "type": "user",
        "email": "nonexistent@example.com",
        "password": "testpass"
    }, follow_redirects=True)

    assert b"Invalid credentials or role" in resp.data