import pytest
from backend.models import db, User, Event, Booking

@pytest.fixture
def sample_booking(app, sample_organizer):
    with app.app_context():
        event = Event(
            title='Sample Event',
            description='For testing',
            date='2025-06-30',
            location='Sample Location',
            price=20.0,
            organizer_id=sample_organizer,
            guests_limit=50
        )
        db.session.add(event)
        db.session.commit()

        booking = Booking(
            event_id=event.id,
            customer_name='Test User',
            customer_email='testuser@example.com',
            tickets_qty=2,
            payment_method='Credit Card',
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()

        return booking.id, event.id

def test_approve_booking(client, app, sample_organizer, sample_booking):
    booking_id, event_id = sample_booking

    # Simulate organizer login
    with client.session_transaction() as session:
        session['_user_id'] = str(sample_organizer)

    # Approve booking
    response = client.post(f'/approve_booking/{booking_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.get(booking_id)
        event = Event.query.get(event_id)
        assert booking.status == 'approved'
        assert event.guests_limit == 48  # guests_limit reduced

def test_reject_booking(client, app, sample_organizer, sample_booking):
    booking_id, event_id = sample_booking

    # Simulate organizer login
    with client.session_transaction() as session:
        session['_user_id'] = str(sample_organizer)

    # Reject booking
    response = client.post(f'/reject_booking/{booking_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.get(booking_id)
        event = Event.query.get(event_id)
        assert booking.status == 'rejected'
        assert event.guests_limit == 50  # unchanged
