from backend.models import Event, User

def test_create_event(client, app, sample_organizer):
    """
    Test that an organizer can successfully create an event.
    """
    # Re-fetch user from DB using the organizer's ID
    with app.app_context():
        user = User.query.get(sample_organizer)

    # Simulate login
    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)

    # Submit the event creation form
    response = client.post('/launch_event', data={
        'title': 'Test Event',
        'description': 'This is a test event.',
        'date_single': '2025-06-12',
        'time_single': '14:00',
        'location': 'Online',
        'general_price': '25.50',  
        'vip_price': '50.00',      # Added VIP price
        'offer_vip': 'on',         # Added VIP checkbox
        'capacity': '50',
        'event_type': 'single',    # Added event type
        'category': 'Tech',
        'image_url': ''
    }, follow_redirects=True)

    # Assertions
    assert response.status_code == 200

    with app.app_context():
        event = Event.query.filter_by(title='Test Event').first()
        assert event is not None
        assert event.title == 'Test Event'
        assert event.description == 'This is a test event.'
        assert event.date == '2025-06-12'
        assert event.time == '14:00'
        assert event.location == 'Online'
        assert event.general_price == 25.50
        assert event.vip_price == 50.00
        assert event.guests_limit == 50
        assert event.event_type == 'single'
        assert event.category == 'Tech'
        assert event.organizer_id == user.id
        # Verify multi-day fields are None for single events
        assert event.end_date is None
        assert event.end_time is None