from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'

# -----------------------
# MODELS
# -----------------------
class User(UserMixin, db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(100), unique=True, nullable=False)
    password        = db.Column(db.String(200), nullable=False)
    role            = db.Column(db.String(20), nullable=False)  # 'user' or 'organizer'
    phone           = db.Column(db.String(20))
    address         = db.Column(db.String(200))
    dob             = db.Column(db.String(50))
    abn             = db.Column(db.String(50))
    bank_name       = db.Column(db.String(200))
    account_number  = db.Column(db.String(100))
    routing_number  = db.Column(db.String(100))

class Event(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(100), nullable=False)
    description  = db.Column(db.Text, nullable=False)
    date         = db.Column(db.String(100), nullable=False)  # "YYYY-MM-DD"
    time         = db.Column(db.String(100), nullable=False)  # "HH:MM"
    location     = db.Column(db.String(200), nullable=False)
    price        = db.Column(db.Float, nullable=False)
    capacity     = db.Column(db.Integer, nullable=False)
    category     = db.Column(db.String(50), nullable=False)
    image_url    = db.Column(db.String(300))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    organizer     = db.relationship('User', backref='events')
    bookings      = db.relationship('Booking', back_populates='event', lazy='dynamic')
    transactions  = db.relationship('Transaction', back_populates='event', lazy='dynamic')

    @property
    def tickets_sold(self):
        return sum(b.tickets_qty for b in self.bookings)

class Booking(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    event_id       = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    customer_name  = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    tickets_qty    = db.Column(db.Integer, default=1)
    payment_method = db.Column(db.String(20))
    timestamp      = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', back_populates='bookings')

class Transaction(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    event_id         = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    amount           = db.Column(db.Float, nullable=False, default=0.0)
    date             = db.Column(db.Date, default=datetime.utcnow)
    status           = db.Column(db.String(50), nullable=False)
    cash_out_amount  = db.Column(db.Float, nullable=True)

    event = db.relationship('Event', back_populates='transactions')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------
# ROUTES
# -----------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    name    = request.form['name']
    email   = request.form['email']
    pwd     = request.form['password']
    cpwd    = request.form['confirm_password']
    role    = request.form.get('type', 'user')
    phone   = request.form.get('phone')
    address = request.form.get('address')
    dob     = request.form.get('dob')     if role=='user'      else None
    abn     = request.form.get('abn')     if role=='organizer' else None

    if pwd != cpwd:
        flash("Passwords do not match", "signup")
        return redirect(url_for('home'))
    if User.query.filter_by(email=email).first():
        flash("Email already exists", "signup")
        return redirect(url_for('home'))

    user = User(
        name=name, email=email,
        password=generate_password_hash(pwd),
        role=role, phone=phone,
        address=address, dob=dob, abn=abn
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    flash("Signup successful!", "signup")
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    pwd   = request.form['password']
    role  = request.form.get('type', 'user')

    user = User.query.filter_by(email=email).first()
    if not user or user.role != role or not check_password_hash(user.password, pwd):
        flash("Invalid credentials or role", "login")
        return redirect(url_for('home'))

    login_user(user)
    flash("Logged in successfully!", "login")
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "logout")
    return redirect(url_for('home'))

@app.route('/account')
@app.route('/org-dashboard.html')
@login_required
def account():
    if current_user.role != 'organizer':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    events = Event.query.filter_by(organizer_id=current_user.id).all()
    bookings = Booking.query.join(Event).filter(Event.organizer_id == current_user.id).all()
    transactions = Transaction.query.filter(
        (Transaction.event.has(organizer_id=current_user.id)) |
        (Transaction.event_id == None)
    ).order_by(Transaction.date.desc()).all()
    
    total_earnings = sum(
        b.tickets_qty * b.event.price
        for b in bookings
    )

    return render_template(
        'org-dashboard.html',
        organizer=current_user,
        events=events,
        bookings=bookings,
        transactions=transactions,
        total_earnings=total_earnings    # <<< pass it in
    )


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if current_user.role != 'organizer':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))
    current_user.name    = request.form['name']
    current_user.phone   = request.form.get('phone')
    current_user.address = request.form.get('address')
    db.session.commit()
    flash("Profile updated!", "success")
    return redirect(url_for('account') + '#profile')

@app.route('/update_payment', methods=['POST'])
@login_required
def update_payment():
    if current_user.role != 'organizer':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))
    current_user.bank_name      = request.form.get('bank_name')
    current_user.account_number = request.form.get('account_number')
    current_user.routing_number = request.form.get('routing_number')
    db.session.commit()
    flash("Payment info updated!", "success")
    return redirect(url_for('account') + '#payment')

@app.route('/manual_booking', methods=['POST'])
@login_required
def manual_booking():
    if current_user.role != 'organizer':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))
    b = Booking(
        event_id       = request.form['event_id'],
        customer_name  = request.form['customer_name'],
        customer_email = request.form['customer_email'],
        tickets_qty    = int(request.form['tickets_qty']),
        payment_method = request.form['payment_method']
    )
    db.session.add(b)
    db.session.commit()

    t = Transaction(
        event_id = b.event_id,
        amount   = b.tickets_qty * b.event.price,
        status   = 'Manual'
    )
    db.session.add(t)
    db.session.commit()

    flash("Manual booking added!", "success")
    return redirect(url_for('account') + '#bookings')

@app.route('/edit_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if current_user.role != 'organizer' or booking.event.organizer_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        booking.customer_name  = request.form['customer_name']
        booking.customer_email = request.form['customer_email']
        booking.tickets_qty    = int(request.form['tickets_qty'])
        booking.payment_method = request.form['payment_method']
        db.session.commit()
        flash("Booking updated successfully!", "success")
        return redirect(url_for('account') + '#bookings')

    return render_template('edit_booking.html', booking=booking)

@app.route('/cash_out', methods=['POST'])
@login_required
def cash_out():
    if current_user.role != 'organizer':
        flash("Access denied.", "danger")
        return redirect(url_for('account') + '#payment')

    try:
        amt = float(request.form['cash_out_amount'])
    except (KeyError, ValueError):
        flash("Invalid cash-out amount.", "danger")
        return redirect(url_for('account') + '#payment')

    t = Transaction(
        event_id        = None,
        amount          = 0.0,
        status          = "Paid Out",
        cash_out_amount = amt
    )
    db.session.add(t)
    db.session.commit()

    flash(f"Successfully cashed out ${amt:.2f}!", "success")
    return redirect(url_for('account') + '#payment')

@app.route('/launch_event', methods=['GET','POST'])
@login_required
def launch_event():
    if current_user.role != 'organizer':
        flash("Only organizers can create events.", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        event = Event(
            title        = request.form['title'],
            description  = request.form['description'],
            date         = request.form['date_single'],
            time         = request.form['time_single'],
            location     = request.form['location'],
            price        = float(request.form['price']),
            capacity     = int(request.form['capacity']),
            category     = request.form['category'],
            image_url    = request.form.get('image_url'),
            organizer_id = current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created!", "success")
        return redirect(url_for('event_page', event_id=event.id))
    return render_template('lunch_event.html')

@app.route('/event/<int:event_id>')
def event_page(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', event=event)

@app.route('/book_event/<int:event_id>', methods=['POST'])
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    b = Booking(
        event_id       = event.id,
        customer_name  = request.form['customer_name'],
        customer_email = request.form['customer_email'],
        tickets_qty    = int(request.form['ticket_qty']),
        payment_method = request.form['payment_method']
    )
    db.session.add(b)
    db.session.commit()
    flash("Booking confirmed!", "success")
    return redirect(url_for('event_page', event_id=event.id))

@app.route('/add-to-calendar/<int:event_id>')
def add_to_calendar(event_id):
    event = Event.query.get_or_404(event_id)
    dt_start = datetime.strptime(f"{event.date} {event.time}", "%Y-%m-%d %H:%M")
    dt_end   = dt_start + timedelta(hours=2)
    start    = dt_start.strftime("%Y%m%dT%H%M%SZ")
    end      = dt_end.strftime("%Y%m%dT%H%M%SZ")
    gcal_url = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(event.title)}"
        f"&dates={start}/{end}"
        f"&details={quote(event.description)}"
        f"&location={quote(event.location)}"
    )
    return redirect(gcal_url)

@app.route('/edit_event/<int:event_id>', methods=['GET','POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.organizer_id:
        abort(403)
    if request.method == 'POST':
        event.title       = request.form['title']
        event.description = request.form['description']
        event.date        = request.form['date_single']
        event.time        = request.form['time_single']
        event.location    = request.form['location']
        event.price       = float(request.form['price'])
        event.capacity    = int(request.form['capacity'])
        event.category    = request.form['category']
        event.image_url   = request.form.get('image_url')
        db.session.commit()
        flash("Event updated!", "success")
        return redirect(url_for('event_page', event_id=event.id))
    return render_template('edit_event.html', event=event)


# -----------------------
# INIT & RUN
# -----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
