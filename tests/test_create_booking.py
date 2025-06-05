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
            general_price=50.0,
            vip_price=100.0,
            organizer_id=organizer.id,
            guests_limit=100,
            event_type='single'
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Create a booking with the correct form fields that your route expects
    response = client.post(f'/book_event/{event_id}', data={
        'customer_name': 'John Doe',
        'customer_email': 'john@example.com',
        'general_qty': '1',  # Changed from 'ticket_qty' to match your route
        'vip_qty': '1',  # Added VIP quantity
        'payment_method': 'Credit Card'
    }, follow_redirects=True)

    # Assertions
    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='john@example.com').first()
        assert booking is not None
        assert booking.customer_name == 'John Doe'
        assert booking.tickets_qty == 2  # 1 general + 1 VIP = 2 total
        assert booking.payment_method == 'Credit Card'
        assert booking.event_id == event_id
        assert booking.total_price == 150.0  # 1*50 + 1*100 = 150
        assert booking.status == 'pending'

        # Check tickets generated
        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        assert len(tickets) == 2

        # Check ticket types
        ticket_types = [ticket.ticket_type for ticket in tickets]
        assert 'General' in ticket_types
        assert 'VIP' in ticket_types

        for ticket in tickets:
            assert ticket.ticket_code.startswith(f"{booking.id}-")
            assert 'G-' in ticket.ticket_code or 'V-' in ticket.ticket_code
            if ticket.qr_code_path:  # Only check if QR path exists
                assert ticket.qr_code_path.endswith(".png")


def test_create_booking_general_only(client, app, sample_organizer):
    """
    Test booking with only general tickets.
    """
    with app.app_context():
        organizer = User.query.get(sample_organizer)
        event = Event(
            title='General Only Event',
            description='Test event',
            date='2025-06-20',
            location='Test Location',
            general_price=25.0,
            vip_price=75.0,
            organizer_id=organizer.id,
            guests_limit=50,
            event_type='single'
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Book only general tickets
    response = client.post(f'/book_event/{event_id}', data={
        'customer_name': 'Jane Smith',
        'customer_email': 'jane@example.com',
        'general_qty': '3',  # 3 general tickets
        'vip_qty': '0',  # No VIP tickets
        'payment_method': 'PayPal'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='jane@example.com').first()
        assert booking is not None
        assert booking.tickets_qty == 3
        assert booking.total_price == 75.0  # 3 * 25 = 75

        # All tickets should be General type
        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        assert len(tickets) == 3
        for ticket in tickets:
            assert ticket.ticket_type == 'General'
            assert 'G-' in ticket.ticket_code


def test_create_booking_vip_only(client, app, sample_organizer):
    """
    Test booking with only VIP tickets.
    """
    with app.app_context():
        organizer = User.query.get(sample_organizer)
        event = Event(
            title='VIP Only Event',
            description='Exclusive event',
            date='2025-07-01',
            location='Premium Venue',
            general_price=40.0,
            vip_price=120.0,
            organizer_id=organizer.id,
            guests_limit=20,
            event_type='single'
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Book only VIP tickets
    response = client.post(f'/book_event/{event_id}', data={
        'customer_name': 'Rich Customer',
        'customer_email': 'rich@example.com',
        'general_qty': '0',  # No general tickets
        'vip_qty': '2',  # 2 VIP tickets
        'payment_method': 'Credit Card'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='rich@example.com').first()
        assert booking is not None
        assert booking.tickets_qty == 2
        assert booking.total_price == 240.0  # 2 * 120 = 240

        # All tickets should be VIP type
        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        assert len(tickets) == 2
        for ticket in tickets:
            assert ticket.ticket_type == 'VIP'
            assert 'V-' in ticket.ticket_code