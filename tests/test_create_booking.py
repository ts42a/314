from backend.models import Event, User, Booking, Ticket, db

def test_create_booking(client, app, sample_organizer):
    """
    Test that a customer can successfully create a booking and generate tickets with QR codes.
    """
    with app.app_context():
        user = User(
            name="John Doe",
            email="john@example.com",
            password="hash",
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

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

    with app.app_context():
        user = User.query.get(user_id)

    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)

    response = client.post(f'/book_event/{event_id}', data={
        'general_qty': '1',
        'vip_qty': '1',
        'card_option': 'new',
        'new_card_number': '4111111111111111',
        'new_cardholder_name': 'John Test',
        'new_expiry_month': '12',
        'new_expiry_year': '2030',
        'new_cvv': '123',
        'customer_name': user.name,
        'customer_email': user.email,
        'payment_method': 'New Card ending in 1111'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='john@example.com').first()
        assert booking is not None
        assert booking.tickets_qty == 2
        assert booking.total_price == 150.0


def test_create_booking_general_only(client, app, sample_organizer):
    """
    Test booking with only general tickets.
    """
    with app.app_context():
        user = User(
            name="Jane Smith",
            email="jane@example.com",
            password="hash",
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

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

    with app.app_context():
        user = User.query.get(user_id)

    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)

    response = client.post(f'/book_event/{event_id}', data={
        'general_qty': '3',
        'vip_qty': '0',
        'card_option': 'new',
        'new_card_number': '4111111111111111',
        'new_cardholder_name': 'Jane Smith',
        'new_expiry_month': '12',
        'new_expiry_year': '2030',
        'new_cvv': '123',
        'customer_name': user.name,
        'customer_email': user.email,
        'payment_method': 'New Card ending in 1111'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='jane@example.com').first()
        assert booking is not None
        assert booking.tickets_qty == 3
        assert booking.total_price == 75.0

        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        for ticket in tickets:
            assert ticket.ticket_type == 'General'
            assert 'G-' in ticket.ticket_code


def test_create_booking_vip_only(client, app, sample_organizer):
    """
    Test booking with only VIP tickets.
    """
    with app.app_context():
        user = User(
            name="Rich Customer",
            email="rich@example.com",
            password="hash",
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

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

    with app.app_context():
        user = User.query.get(user_id)

    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)

    response = client.post(f'/book_event/{event_id}', data={
        'general_qty': '0',
        'vip_qty': '2',
        'card_option': 'new',
        'new_card_number': '4111111111111111',
        'new_cardholder_name': 'Rich Customer',
        'new_expiry_month': '12',
        'new_expiry_year': '2030',
        'new_cvv': '123',
        'customer_name': user.name,
        'customer_email': user.email,
        'payment_method': 'New Card ending in 1111'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        booking = Booking.query.filter_by(customer_email='rich@example.com').first()
        assert booking is not None
        assert booking.tickets_qty == 2
        assert booking.total_price == 240.0

        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        for ticket in tickets:
            assert ticket.ticket_type == 'VIP'
            assert 'V-' in ticket.ticket_code


