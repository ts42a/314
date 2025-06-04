from backend.models import User, db

def test_organizer_edit_profile(client, app, sample_organizer):
    """
    Test that an organizer can successfully update their profile.
    """
    with app.app_context():
        organizer = User.query.get(sample_organizer)
        organizer_id = organizer.id

    # Simulate login
    with client.session_transaction() as session:
        session['_user_id'] = str(organizer_id)

    # Submit update form
    response = client.post('/update_profile', data={
        'name': 'Updated Organizer',
        'phone': '1234567890',
        'address': 'New Address'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Confirm updated in DB
    with app.app_context():
        updated = User.query.get(organizer_id)
        assert updated.name == 'Updated Organizer'
        assert updated.phone == '1234567890'
        assert updated.address == 'New Address'
