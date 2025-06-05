import os
import tempfile
import pytest

# Import the Flask app and the models from backend
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
        return user.id

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

@pytest.fixture
def sample_event_with_booking(app, sample_user, sample_organizer):
    """
    Create an event by the organizer and a booking by the user.
    Returns (event_id, booking_id) instead of objects to avoid detachment issues.
    """
    with app.app_context():
        organizer = User.query.get(sample_organizer)
        user = User.query.get(sample_user)

        # Create event
        event = Event(
            title="Sample Event",
            description="Test event with booking",
            date="2025-06-25",
            location="Sample Location",
            general_price=25.0,
            vip_price=30.0,
            organizer_id=organizer.id,
            guests_limit=50
        )
        db.session.add(event)
        db.session.commit()

        # Create booking by user - ADD total_price field
        booking = Booking(
            event_id=event.id,
            customer_name=user.name,
            customer_email=user.email,
            tickets_qty=2,
            payment_method="Credit Card",
            total_price=2 * event.general_price,  # ADD THIS LINE: 2 * 25.0 = 50.0
            status='confirmed'  # Also add status if needed
        )
        db.session.add(booking)
        db.session.commit()

        # Return IDs instead of objects to avoid detachment
        return event.id, booking.id