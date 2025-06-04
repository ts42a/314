from backend.models import Event, User, Booking, Transaction, db


def test_organizer_cancel_booking(client, app, sample_organizer):
    """
    Organizer cancels a booking they own.
    """
    with app.app_context():
        # Get organizer and store ID
        organizer = User.query.get(sample_organizer)
        organizer_id = organizer.id

        # Create event by organizer
        event = Event(
            title='Org Cancel',
            description='Test event',
            date='2025-07-01',
            location='Test Place',
            price=25.0,
            organizer_id=organizer_id,
            guests_limit=100
        )
        db.session.add(event)
        db.session.commit()

        # Create booking under that event
        booking = Booking(
            event_id=event.id,
            customer_name='Bob Test',
            customer_email='bob@example.com',
            tickets_qty=3,
            payment_method='Online'
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    # Simulate organizer login
    with client.session_transaction() as session:
        session['_user_id'] = str(organizer_id)

    # Attempt to cancel booking
    response = client.post(f'/cancel_booking/{booking_id}', follow_redirects=True)
    assert response.status_code == 200

    # Verify booking is deleted
    with app.app_context():
        assert Booking.query.get(booking_id) is None


def test_user_cancel_own_booking(client, app, sample_user):
    """
    User cancels their own booking.
    """
    with app.app_context():
        # Get user and store ID
        user = User.query.get(sample_user)
        user_id = user.id

        # Create organizer for the event
        organizer = User(
            name='Organizer Y',
            email='orgy@example.com',
            password='hashed',
            role='organizer'
        )
        db.session.add(organizer)
        db.session.commit()

        # Create event by that organizer
        event = Event(
            title='User Cancel',
            description='User-side cancel test',
            date='2025-07-10',
            location='CancelLand',
            price=30.0,
            organizer_id=organizer.id,
            guests_limit=80
        )
        db.session.add(event)
        db.session.commit()

        # Create booking by user
        booking = Booking(
            event_id=event.id,
            customer_name=user.name,
            customer_email=user.email,
            tickets_qty=1,
            payment_method='Card'
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

    # Simulate user login
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)

    # Attempt to cancel booking
    response = client.post(f'/cancel_booking/{booking_id}', follow_redirects=True)
    assert response.status_code == 200

    # Verify booking is deleted
    with app.app_context():
        assert Booking.query.get(booking_id) is None
