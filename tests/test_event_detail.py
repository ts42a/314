from backend.models import db, User, Event, Booking, Transaction


def test_view_event_detail(client, app, sample_organizer):
    """
    Test that users can view event details on the event page.
    """
    # Create an event to view
    with app.app_context():
        test_event = Event(
            title='Test Event Detail',
            description='This is a detailed test event description.',
            date='2025-06-20',
            location='Test Venue',
            price=15.99,
            guests_limit=100,
            organizer_id=sample_organizer
        )
        db.session.add(test_event)
        db.session.commit()
        event_id = test_event.id

    # View the event detail page (no login required for viewing)
    response = client.get(f'/event/{event_id}')

    # Assertions
    assert response.status_code == 200

    # Check that the event details are displayed on the page
    response_data = response.get_data(as_text=True)
    assert 'Test Event Detail' in response_data
    assert 'This is a detailed test event description.' in response_data
    assert '2025-06-20' in response_data
    assert 'Test Venue' in response_data
    assert '15.99' in response_data
    assert '100' in response_data

    # Verify the event still exists in the database
    with app.app_context():
        event = Event.query.get(event_id)
        assert event is not None
        assert event.title == 'Test Event Detail'
        assert event.organizer_id == sample_organizer