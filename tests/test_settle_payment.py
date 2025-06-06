from backend.app import app as flask_app
from backend.models import db, User, Event, Booking, Transaction, Ticket

def test_booking_general_only(client, app, sample_user, sample_organizer):
    with app.app_context():
        user = User.query.get(sample_user)
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
        user_id = user.id

    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)

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
        booking = Booking.query.filter_by(customer_email=user.email).first()
        assert booking is not None
        assert booking.tickets_qty == 3
        assert booking.total_price == 75.0



def test_booking_vip_only(client, app, sample_user, sample_organizer):
    with app.app_context():
        user = User.query.get(sample_user)
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
        user_id = user.id

    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)

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
        booking = Booking.query.filter_by(customer_email=user.email).first()
        assert booking is not None
        assert booking.tickets_qty == 2
        assert booking.total_price == 240.0

