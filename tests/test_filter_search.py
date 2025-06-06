from backend.models import Event, db

def test_filter_by_location(client, app, sample_organizer):
    """
    Test filtering events by location using the /discover endpoint.
    """
    with app.app_context():
        event1 = Event(
            title="Concert in NY",
            description="A cool music event",
            date="2025-07-01",
            location="New York",
            general_price=30.0,
            vip_price=60.0,
            organizer_id=sample_organizer,
            guests_limit=100,
            event_type="single"
        )
        event2 = Event(
            title="Event Elsewhere",
            description="Some other place",
            date="2025-07-02",
            location="Los Angeles",
            general_price=25.0,
            vip_price=55.0,
            organizer_id=sample_organizer,
            guests_limit=50,
            event_type="single"
        )
        db.session.add_all([event1, event2])
        db.session.commit()

    # Act: Perform filter request to /discover
    response = client.get('/discover?title=&location=New+York&category=&guests=')
    assert response.status_code == 200

    data = response.get_data(as_text=True)
    assert "Concert in NY" in data
    assert "Event Elsewhere" not in data


def test_filter_by_title(client, app, sample_organizer):
    """
    Test filtering events by title using the /discover endpoint.
    """
    with app.app_context():
        event = Event(
            title="Comedy Night Special",
            description="Laughs all night!",
            date="2025-07-10",
            location="Chicago",
            general_price=20.0,
            vip_price=45.0,
            organizer_id=sample_organizer,
            guests_limit=80,
            event_type="single"
        )
        db.session.add(event)
        db.session.commit()

    # Act: Filter by title
    response = client.get('/discover?title=Comedy+Night+Special&location=&category=&guests=')
    assert response.status_code == 200

    data = response.get_data(as_text=True)
    assert "Comedy Night Special" in data