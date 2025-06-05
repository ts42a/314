from backend.models import User, Booking, Event, db
from datetime import date


def test_generate_ticket(client, app, sample_user):
    """
    Test that a user can trigger ticket generation for their booking.
    """
    with app.app_context():
        user = User.query.get(sample_user)
        user_id = user.id

        organizer = User(
            name="Gen Org",
            email="genorg@example.com",
            password="hash",
            role="organizer"
        )
        db.session.add(organizer)
        db.session.commit()

        event = Event(
            title="Gen Event",
            description="Generate ticket event",
            date=date.today().strftime('%Y-%m-%d'),
            location="Hall A",
            general_price=40.0,  # Changed from 'price' to 'general_price'
            vip_price=80.0,      # Added required vip_price field
            organizer_id=organizer.id,
            guests_limit=60,
            event_type='single'  # Added required event_type field
        )
        db.session.add(event)
        db.session.commit()

        booking = Booking(
            event_id=event.id,
            customer_name=user.name,
            customer_email=user.email,
            tickets_qty=1,
            payment_method="Cash",
            total_price=40.0  # Added required total_price field
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)

    response = client.post(f'/generate_ticket/{booking_id}', follow_redirects=True)
    assert response.status_code == 200
    # assert b'Ticket generated successfully!' in response.data