from backend.models import db, User, Event, Booking, Transaction

def test_delete_event(app, client, sample_organizer):
    """
    Test the delete_event route functionality.
    """
    with app.app_context():
        # Re-fetch user from DB using the organizer's ID
        user = User.query.get(sample_organizer)

        # Create a sample event owned by the organizer
        event = Event(
            title="Test Event",
            description="A test event",
            date="2025-07-01",
            location="Test Location",
            price=50.0,
            guests_limit=100,
            organizer_id=sample_organizer
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

        # Create associated bookings and transactions
        booking = Booking(
            event_id=event_id,
            customer_name="Test Customer",
            customer_email="customer@example.com",
            tickets_qty=2,
            payment_method="credit_card"
        )
        db.session.add(booking)

        transaction = Transaction(
            event_id=event_id,
            amount=100.0,
            status="completed"
        )
        db.session.add(transaction)
        db.session.commit()

        # Verify event and related data exist before deletion
        assert Event.query.get(event_id) is not None
        assert Booking.query.filter_by(event_id=event_id).count() == 1
        assert Transaction.query.filter_by(event_id=event_id).count() == 1

    # Simulate login using session transaction
    with client.session_transaction() as session:
        session['_user_id'] = str(sample_organizer)

    # Delete the event
    delete_response = client.post(f'/delete_event/{event_id}', follow_redirects=True)
    assert delete_response.status_code == 200

    # Check for success message in response
    assert b"Event deleted successfully!" in delete_response.data

    # Verify deletion using the same pattern as create_event test
    with app.app_context():
        # Verify event is deleted
        deleted_event = Event.query.filter_by(id=event_id).first()
        assert deleted_event is None

        # Verify associated bookings and transactions are deleted
        remaining_bookings = Booking.query.filter_by(event_id=event_id).count()
        remaining_transactions = Transaction.query.filter_by(event_id=event_id).count()

        assert remaining_bookings == 0
        assert remaining_transactions == 0

#
# def test_delete_event_unauthorized_user(app, client, sample_organizer, sample_user):
#     """
#     Test that a user who is not the organizer cannot delete an event.
#     """
#     with app.app_context():
#         # Create a sample event owned by the organizer
#         event = Event(
#             title="Test Event",
#             description="A test event",
#             date="2025-07-01",
#             location="Test Location",
#             price=50.0,
#             guests_limit=100,
#             organizer_id=sample_organizer
#         )
#         db.session.add(event)
#         db.session.commit()
#         event_id = event.id
#
#     # Log in as a different user (not the organizer)
#     login_response = client.post('/login', data={
#         'email': 'test@example.com',
#         'password': 'testpass'
#     }, follow_redirects=True)
#     assert login_response.status_code == 200
#
#     # Try to delete the event - should get 403 Forbidden
#     delete_response = client.post(f'/delete_event/{event_id}')
#     assert delete_response.status_code == 403
#
#     with app.app_context():
#         # Refresh the session to get the current database state
#         db.session.expire_all()
#
#         # Verify event still exists
#         assert Event.query.get(event_id) is not None
#
#
# def test_delete_nonexistent_event(app, client, sample_organizer):
#     """
#     Test that trying to delete a non-existent event returns 404.
#     """
#     # Log in as the organizer
#     login_response = client.post('/login', data={
#         'email': 'org@example.com',
#         'password': 'testpass'
#     }, follow_redirects=True)
#     assert login_response.status_code == 200
#
#     # Try to delete a non-existent event
#     delete_response = client.post('/delete_event/99999')
#     assert delete_response.status_code == 404
#
#
# def test_delete_event_unauthenticated(app, client, sample_organizer):
#     """
#     Test that unauthenticated users cannot delete events.
#     """
#     with app.app_context():
#         # Create a sample event
#         event = Event(
#             title="Test Event",
#             description="A test event",
#             date="2025-07-01",
#             location="Test Location",
#             price=50.0,
#             guests_limit=100,
#             organizer_id=sample_organizer
#         )
#         db.session.add(event)
#         db.session.commit()
#         event_id = event.id
#
#     # Try to delete without logging in
#     delete_response = client.post(f'/delete_event/{event_id}')
#
#     # Should redirect to login page (302) or return 401
#     assert delete_response.status_code in [302, 401]
#
#     with app.app_context():
#         # Refresh the session to get the current database state
#         db.session.expire_all()
#
#         # Verify event still exists
#         assert Event.query.get(event_id) is not None
#
#
# def test_delete_event_with_multiple_bookings(app, client, sample_organizer):
#     """
#     Test deleting an event with multiple bookings and transactions.
#     """
#     with app.app_context():
#         # Create a sample event owned by the organizer
#         event = Event(
#             title="Popular Event",
#             description="An event with multiple bookings",
#             date="2025-07-01",
#             location="Test Location",
#             price=25.0,
#             guests_limit=100,
#             organizer_id=sample_organizer
#         )
#         db.session.add(event)
#         db.session.commit()
#         event_id = event.id
#
#         # Create multiple bookings and transactions
#         for i in range(3):
#             booking = Booking(
#                 event_id=event_id,
#                 customer_name=f"Customer {i + 1}",
#                 customer_email=f"customer{i + 1}@example.com",
#                 tickets_qty=1,
#                 payment_method="credit_card"
#             )
#             transaction = Transaction(
#                 event_id=event_id,
#                 amount=25.0,
#                 status="completed"
#             )
#             db.session.add(booking)
#             db.session.add(transaction)
#
#         db.session.commit()
#
#         # Verify multiple records exist
#         assert Booking.query.filter_by(event_id=event_id).count() == 3
#         assert Transaction.query.filter_by(event_id=event_id).count() == 3
#
#     # Log in and delete the event
#     client.post('/login', data={
#         'email': 'org@example.com',
#         'password': 'testpass'
#     }, follow_redirects=True)
#
#     delete_response = client.post(f'/delete_event/{event_id}', follow_redirects=True)
#     assert delete_response.status_code == 200
#
#     with app.app_context():
#         # Refresh the session to get the current database state
#         db.session.expire_all()
#
#         # Verify all related records are deleted
#         assert Event.query.get(event_id) is None
#         assert Booking.query.filter_by(event_id=event_id).count() == 0
#         assert Transaction.query.filter_by(event_id=event_id).count() == 0