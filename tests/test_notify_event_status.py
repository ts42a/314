import pytest
from backend.models import db, Event, Booking, Notification, User


@pytest.fixture
def setup_event_with_booking(app, sample_user, sample_organizer):
    with app.app_context():
        event = Event(
        title='UOW Tech Meetup',
        description='Exciting updates in tech.',
        date='2025-06-30',
        location='Innovation Campus',
        general_price=15.0,
        vip_price=30.0, 
        guests_limit=100,
        event_type='single',
        organizer_id=sample_organizer
)

        db.session.add(event)
        db.session.flush()

        booking = Booking(
            event_id=event.id,
            customer_id=sample_user,
            customer_name='Test User',
            customer_email='user@example.com',
            tickets_qty=1,
            total_price=15.0,
            status='approved',
            payment_method='Card'
        )
        db.session.add(booking)
        db.session.commit()

        return event.id, sample_user


def test_event_update_triggers_notification(app, setup_event_with_booking):
    event_id, user_id = setup_event_with_booking

    with app.app_context():
        event = Event.query.get(event_id)
        user = User.query.get(user_id)

        # Change a valid attribute instead
        event.description = 'Updated details for UOW Tech Meetup.'
        db.session.commit()

        notification = Notification(
            recipient_id=user.id,
            sender_name='System',
            subject=f"Event Update: {event.title}",
            message=f"The event '{event.title}' has been updated. Please check the event page for details."
        )
        db.session.add(notification)
        db.session.commit()

        notifs = Notification.query.filter_by(recipient_id=user.id).all()
        assert len(notifs) > 0

        latest = notifs[-1]
        assert "Event Update" in latest.subject
        assert event.title in latest.subject
