from backend.models import User, Booking, Event, db
from datetime import date


def test_user_view_profile(client, app, sample_user):
    """
    Test that a user can access their profile and see booking data.
    """
    with app.app_context():
        user = User.query.get(sample_user)
        user_id = user.id
        user_name = user.name
        user_email = user.email

        # Create dummy organizer for event
        organizer = User(
            name='OrgZ',
            email='orgz@example.com',
            password='hash',
            role='organizer'
        )
        db.session.add(organizer)
        db.session.commit()

        event = Event(
            title='View Test Event',
            description='Test description',
            date=date.today().strftime('%Y-%m-%d'),
            location='Testville',
            general_price=20.0,
            vip_price=40.0,
            organizer_id=organizer.id,
            guests_limit=100,
            event_type='single'
        )
        db.session.add(event)
        db.session.commit()

        # Create booking for the user
        booking = Booking(
            event_id=event.id,
            customer_name=user_name,
            customer_email=user_email,
            tickets_qty=1,
            payment_method='Card',
            total_price=20.0 
        )
        db.session.add(booking)
        db.session.commit()

    # Simulate user login
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)

    response = client.get('/profile')
    assert response.status_code == 200
    assert user_name.encode() in response.data
    assert user_email.encode() in response.data
    assert b'Card' in response.data