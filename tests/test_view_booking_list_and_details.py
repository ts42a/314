from backend.models import Event, User, Booking, Transaction, db

def test_organizer_view_booking_lists(client, sample_event_with_booking, sample_organizer):
    """
    Test that the organizer can view booking lists for their event.
    """
    event_id, booking_id = sample_event_with_booking

    with client.application.app_context():
        organizer = User.query.get(sample_organizer)
        booking = Booking.query.get(booking_id)

    with client.session_transaction() as session:
        session['_user_id'] = str(organizer.id)

    response = client.get('/account')
    assert response.status_code == 200
    assert booking.customer_name.encode() in response.data
    assert booking.customer_email.encode() in response.data


def test_user_view_booking_lists(client, app, sample_event_with_booking, sample_user):
    """
    Test that the user can view their own booking in their profile.
    """
    event_id, booking_id = sample_event_with_booking

    with app.app_context():
        user = User.query.get(sample_user)
        booking = Booking.query.get(booking_id)

    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)

    response = client.get('/profile')
    assert response.status_code == 200
    assert booking.customer_name.encode() in response.data
    assert booking.customer_email.encode() in response.data
