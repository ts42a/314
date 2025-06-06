import pytest
from backend.models import db, Booking, User
from flask import get_flashed_messages

@pytest.fixture
def sample_paid_booking(app, sample_user):
    with app.app_context():
        booking = Booking(
            event_id=1,
            customer_id=sample_user,
            customer_name="Test User",
            customer_email="user@test.com",
            tickets_qty=2,
            payment_method="Credit Card",
            status="paid",
            total_price=100.0
        )
        db.session.add(booking)
        db.session.commit()
        return booking.id

def test_notify_payment_success(client, app, sample_user, sample_paid_booking):
    booking_id = sample_paid_booking

    # Simulate login
    with client.session_transaction() as session:
        session['_user_id'] = str(sample_user)

    # Simulate accessing ticket page (which reflects booking status)
    response = client.get(f"/ticket/{booking_id}", follow_redirects=True)

    assert response.status_code == 200
    assert b"Test User" in response.data

def test_notify_payment_failure(client, app, sample_user):
    with app.app_context():
        booking = Booking(
            event_id=1,
            customer_id=sample_user,
            customer_name="Test User",
            customer_email="user@test.com",
            tickets_qty=2,
            payment_method="Credit Card",
            status="failed",
            total_price=100.0
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    with client.session_transaction() as session:
        session['_user_id'] = str(sample_user)

    # Try to view ticket for a failed payment
    response = client.get(f"/ticket/{booking_id}", follow_redirects=True)

    assert response.status_code == 200
    assert b"not been approved" in response.data or b"danger" in response.data
