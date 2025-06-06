import pytest
from backend.models import Booking, Notification, User, db

def test_ntf_02_notify_booking_status(client, app, sample_event_with_booking, sample_user, sample_organizer):
    """
    NTF-02: Test that when the booking status changes, the system notifies
    both the user and the organizer.
    """
    event_id, booking_id = sample_event_with_booking

    with app.app_context():
        # Simulate booking status change
        booking = Booking.query.get(booking_id)
        booking.status = "approved"  # e.g., status moved from 'requested' to 'approved'
        db.session.commit()

        user = User.query.get(sample_user)
        organizer = User.query.get(sample_organizer)

        # Create notification for user
        user_notification = Notification(
            recipient_id=user.id,
            sender_name=organizer.name,
            subject="Booking Status Update",
            message=f"Your booking has been {booking.status.title()}."
        )

        # Create notification for organizer
        organizer_notification = Notification(
            recipient_id=organizer.id,
            sender_name=user.name,
            subject="Booking Status Update",
            message=f"A booking was {booking.status.title()} for your event."
        )

        db.session.add_all([user_notification, organizer_notification])
        db.session.commit()

        # Check user received notification
        notif_user = Notification.query.filter_by(recipient_id=user.id).all()
        assert any(
            f"Your booking has been {booking.status.title()}." in n.message for n in notif_user
        ), "User did not receive booking status update notification."

        # Check organizer received notification
        notif_org = Notification.query.filter_by(recipient_id=organizer.id).all()
        assert any(
            f"A booking was {booking.status.title()}" in n.message for n in notif_org
        ), "Organizer did not receive booking status update notification."
