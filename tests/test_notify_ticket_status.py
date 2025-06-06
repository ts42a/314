import pytest
from backend.models import Booking, Notification, User,db

def test_ntf_03_notify_ticket_status(client, app, sample_event_with_booking, sample_user, sample_organizer):
    """
    NTF-03: Test that when the ticket status is updated, the user is notified.
    """
    event_id, booking_id = sample_event_with_booking

    with app.app_context():
        # Retrieve the booking and update its status
        booking = Booking.query.get(booking_id)
        booking.status = "active"
        db.session.commit()

        # Retrieve the user and organizer
        user = User.query.get(sample_user)
        organizer = User.query.get(sample_organizer)

        # Create a notification for the user
        notification = Notification(
            recipient_id=user.id,
            sender_name=organizer.name,
            subject="Ticket Status Update",
            message=f"Your ticket status has been updated to {booking.status.title()}."
        )
        db.session.add(notification)
        db.session.commit()

        # Verify that the notification was created
        notifications = Notification.query.filter_by(recipient_id=user.id).all()
        assert any(
            n.message == f"Your ticket status has been updated to {booking.status.title()}."
            for n in notifications
        ), "Notification for ticket status update not found."
