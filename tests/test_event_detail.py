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
            time='19:00',                # Added time field
            location='Test Venue',
            general_price=15.99,         # Changed from 'price' to 'general_price'
            vip_price=29.99,            # Added required vip_price field
            guests_limit=100,
            organizer_id=sample_organizer,
            event_type='single',        # Added required event_type field
            category='Entertainment'    # Added optional category field
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
    assert '19:00' in response_data      # Check time is displayed
    assert 'Test Venue' in response_data
    assert '15.99' in response_data      # General price
    assert '29.99' in response_data      # VIP price
    assert '100' in response_data        # Capacity/guests_limit
    assert 'Entertainment' in response_data  # Category

    # Verify the event still exists in the database
    with app.app_context():
        event = Event.query.get(event_id)
        assert event is not None
        assert event.title == 'Test Event Detail'
        assert event.description == 'This is a detailed test event description.'
        assert event.date == '2025-06-20'
        assert event.time == '19:00'
        assert event.location == 'Test Venue'
        assert event.general_price == 15.99
        assert event.vip_price == 29.99
        assert event.guests_limit == 100
        assert event.event_type == 'single'
        assert event.category == 'Entertainment'
        assert event.organizer_id == sample_organizer
        # Verify multi-day fields are None for single events
        assert event.end_date is None
        assert event.end_time is None