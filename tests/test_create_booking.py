from backend.models import Event, User, Booking, Ticket, db

def test_create_booking(client, app, sample_organizer):
    """
    Test that a customer can successfully create a booking and generate tickets with QR codes.
    """
    # Create an event first
    with app.app_context():
        organizer = User.query.get(sample_organizer)
        event = Event(
            title='Test Event for Booking',
            description='Test event description',
            date='2025-06-15',
            location='Test Location',
            price=50.0,
            organizer_id=organizer.id,
            guests_limit=100
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Create a booking
    response = client.post(f'/book_event/{event_id}', data={
        'customer_name': 'John Doe',
        'customer_email': 'john@example.com',
        'ticket_qty': '2',
        'payment_method': 'Credit Card',
        'ticket_type': 'General'
    }, follow_redirects=True)

    # Assertions
    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='john@example.com').first()
        assert booking is not None
        assert booking.customer_name == 'John Doe'
        assert booking.tickets_qty == 2
        assert booking.payment_method == 'Credit Card'
        assert booking.event_id == event_id
        assert booking.ticket_type == 'General'

        # Check tickets generated
        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        assert len(tickets) == 2
        for ticket in tickets:
            assert ticket.ticket_code.startswith(f"{booking.id}-")
            assert ticket.qr_code_path.endswith(".png")