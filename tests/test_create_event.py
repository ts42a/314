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
        'price': '25.50',
        'capacity': '50',
       # 'category': 'Tech',
        'image_url': ''
    }, follow_redirects=True)

    # Assertions
    assert response.status_code == 200

    with app.app_context():
        event = Event.query.filter_by(title='Test Event').first()
        assert event is not None
        assert event.organizer_id == user.id
        assert event.guests_limit == 50
        # assert event.category == 'Tech'

