from backend.models import db, User, Event, Booking, Transaction

def test_edit_event(client, app, sample_organizer):
    """
    Test that an organizer can successfully edit an existing event.
    """
    # Create an event to edit
    with app.app_context():
        # First, create an event to edit
        original_event = Event(
            title='Original Event',
            description='Original description',
            date='2025-06-10',
            location='Original Location',
            general_price=20.00,
            vip_price=40.00,
            guests_limit=30,
            organizer_id=sample_organizer,
            event_type='single'  # Added required field
        )
        db.session.add(original_event)
        db.session.commit()
        event_id = original_event.id

    # Simulate login
    with client.session_transaction() as session:
        session['_user_id'] = str(sample_organizer)

    # Submit the event edit form
    response = client.post(f'/edit_event/{event_id}', data={
        'title': 'Updated Event Title',
        'description': 'Updated event description.',
        'date_single': '2025-06-15',
        'time_single': '19:00',
        'location': 'Updated Location',
        'general_price': '35.75',
        'vip_price': '55.00',
        'offer_vip': 'on',
        'capacity': '75',
        'event_type': 'single',
        'category': 'Entertainment',  # optional category
        'image_url': 'http://example.com/image.jpg'
    }, follow_redirects=True)

    # Assertions
    assert response.status_code == 200

    with app.app_context():
        # Re-fetch the event to check if it was updated
        updated_event = Event.query.get(event_id)
        assert updated_event is not None
        assert updated_event.title == 'Updated Event Title'
        assert updated_event.description == 'Updated event description.'
        assert updated_event.date == '2025-06-15'
        assert updated_event.time == '19:00'
        assert updated_event.location == 'Updated Location'
        assert updated_event.general_price == 35.75
        assert updated_event.vip_price == 55.00
        assert updated_event.guests_limit == 75
        assert updated_event.event_type == 'single'
        assert updated_event.category == 'Entertainment'
        assert updated_event.image_url == 'http://example.com/image.jpg'
        assert updated_event.organizer_id == sample_organizer
        # Verify multi-day fields are cleared for single events
        assert updated_event.end_date is None
        assert updated_event.end_time is None