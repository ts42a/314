import os
import tempfile
import pytest

# Import the Flask `app` and the models from backend
from backend.app import app as flask_app
from backend.models import db, User, Event, Booking, Transaction

@pytest.fixture()
def app():
    """
    Create and configure a new Flask app instance for each test.
    """
    # Tell Flask to use an in-memory SQLite database for tests
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "secret-key"
    })

    # Create app context and all tables
    with flask_app.app_context():
        # Don't call db.init_app again - it's already initialized in app.py
        db.create_all()
        yield flask_app
        # Teardown: drop all tables
        db.drop_all()

@pytest.fixture
def client(app):
    """
    A test client for the Flask app, using the in-memory DB.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    A test runner for Click commands (if you ever add any).
    """
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """
    Create and return a sample 'user' (role="user") in the DB.
    """
    from werkzeug.security import generate_password_hash

    with app.app_context():
        user = User(  # Use User, not Organizer
            name="Test User",
            email="test@example.com",
            password=generate_password_hash("testpass"),
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def sample_organizer(app):
    """
    Create and return a sample 'organizer' (role="organizer") in the DB.
    """
    from werkzeug.security import generate_password_hash

    with app.app_context():
        org = User(  
            name="Test Organizer",
            email="org@example.com",
            password=generate_password_hash("testpass"),
            role="organizer"
        )
        db.session.add(org)
        db.session.commit()
        return org.id