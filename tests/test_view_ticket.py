from backend.models import User, Booking, Event, db
from datetime import date


def test_display_ticket_view(client, app, sample_user):
    """
    Test that a logged-in user can view their ticket via /ticket/<booking_id>.
    """
    with app.app_context():
        user = User.query.get(sample_user)
        user_id = user.id
        user_email = user.email
        user_name = user.name

        organizer = User(
            name="Ticket Org",
            email="ticketorg@example.com",
            password="hash",
            role="organizer"
        )
        db.session.add(organizer)
        db.session.commit()

        event = Event(
            title="Ticketed Event",
            description="Ticket testing event",
            date=date.today().strftime('%Y-%m-%d'),
            location="Auditorium",
            price=50.0,
            organizer_id=organizer.id,
            guests_limit=100
        )
        db.session.add(event)
        db.session.commit()

        booking = Booking(
            event_id=event.id,
            customer_name=user_name,
            customer_email=user_email,
            tickets_qty=2,
            payment_method="Card"
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)

    response = client.get(f'/ticket/{booking_id}')
    assert response.status_code == 200
    assert user_name.encode() in response.data
    assert b'Ticket' in response.data or b'Event' in response.data
