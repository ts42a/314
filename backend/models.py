from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

# ─── The ONE global SQLAlchemy() instance ────────────────────────────────────
db = SQLAlchemy()

# ─── The single User model (used for both regular users and organizers) ───────
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(100), unique=True, nullable=False)
    password        = db.Column(db.String(200), nullable=False)
    role            = db.Column(db.String(20),  nullable=False)   # either "user" or "organizer"
    phone           = db.Column(db.String(20))
    address         = db.Column(db.String(200))
    dob             = db.Column(db.String(50))
    abn             = db.Column(db.String(50))
    bank_name       = db.Column(db.String(200))
    account_number  = db.Column(db.String(100))
    routing_number  = db.Column(db.String(100))

    # If this User is an organizer, this relationship points at their events.
    events = db.relationship("Event", backref="organizer", lazy=True)

# ─── The single Event model (linked to User via organizer_id) ───────────────
class Event(db.Model):
    __tablename__ = "event"
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(120), nullable=False)
    description   = db.Column(db.Text, nullable=False)
    location      = db.Column(db.String(100), nullable=False)
    date          = db.Column(db.String(50),  nullable=False)
    end_date      = db.Column(db.String(50),  nullable=True)
    time          = db.Column(db.String(20), nullable=True)  
    end_time      = db.Column(db.String(20), nullable=True)
    event_type    = db.Column(db.String(20), nullable=False, default='single')  # 'single' or 'multi'
    guests_limit  = db.Column(db.Integer,     nullable=False) 
    organizer_id  = db.Column(db.Integer,     db.ForeignKey("user.id"), nullable=False)
    general_price = db.Column(db.Float, nullable=False)
    vip_price = db.Column(db.Float, nullable=False)
    category      = db.Column(db.String(50), nullable=True)
    image_url     = db.Column(db.String(255), nullable=True)
    @property
    def capacity(self):
        return self.guests_limit
    
    @property
    def tickets_sold(self):
        return sum(b.tickets_qty for b in self.bookings)
    
    bookings      = db.relationship("Booking",    backref="event",      lazy="dynamic")
    transactions  = db.relationship("Transaction", backref="event",      lazy="dynamic")

# ─── Booking ties a customer into an Event ────────────────────────────────────
class Booking(db.Model):
    __tablename__ = "booking"
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'))  # Organizer ID
    customer_id    = db.Column(db.Integer, db.ForeignKey('user.id'))  # Customer ID 
    event_id       = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    customer_name  = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    tickets_qty    = db.Column(db.Integer, default=1)
    payment_method = db.Column(db.String(20))
    timestamp      = db.Column(db.DateTime, default=datetime.utcnow)
    status         = db.Column(db.String(20), default='pending')  
    total_price    = db.Column(db.Float, nullable=False)
    
    # Relationships
    tickets = db.relationship("Ticket", backref="booking", lazy=True, cascade="all, delete-orphan")
    organizer = db.relationship('User', foreign_keys=[user_id], backref='organized_bookings', lazy=True)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_bookings', lazy=True)

# ─── Transaction (for payments, cash‐outs, etc.) ─────────────────────────────
class Transaction(db.Model):
    __tablename__ = "transaction"

    id               = db.Column(db.Integer, primary_key=True)
    event_id         = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=True)
    amount           = db.Column(db.Float, nullable=False, default=0.0)
    date             = db.Column(db.Date,  default=datetime.utcnow)
    status           = db.Column(db.String(50), nullable=False)
    cash_out_amount  = db.Column(db.Float, nullable=True)
    
    # ─── Booking ties a customer into an Event ────────────────────────────────────
class Ticket(db.Model):
    __tablename__ = 'ticket'
    id             = db.Column(db.Integer, primary_key=True)
    booking_id     = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    ticket_code    = db.Column(db.String(64), unique=True, nullable=False)
    ticket_type    = db.Column(db.String(50), nullable=False)
    qr_code_path   = db.Column(db.String(255))


