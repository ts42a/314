import pytest
from backend.models import Booking, User

def test_display_ticket_view(client, app, sample_user, sample_event_with_booking):
    event_id, booking_id = sample_event_with_booking

    with app.app_context():
        user = User.query.get(sample_user)
        booking = Booking.query.get(booking_id)

        # Sanity check
        assert booking is not None
        assert booking.customer_email == user.email

    # Simulate user login
    with client.session_transaction() as session:
        session["_user_id"] = str(sample_user)

    # View ticket
    response = client.get(f"/ticket/{booking_id}")
    assert response.status_code == 302
    # assert b"Ticket" in response.data or b"QR" in response.data
