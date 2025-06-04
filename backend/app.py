from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote
from datetime import datetime, timedelta
import os

try:
    from backend.models import db, User, Event, Booking, Transaction
except ModuleNotFoundError:
    try:
        from models import db, User, Event, Booking, Transaction
    except ModuleNotFoundError as e:
        print("Error: Could not import 'backend.models' or fallback 'models'.")
        raise SystemExit("Fatal: Required models module not found. Exiting.")

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
db.init_app(app) # bind db obj from models.py

login_manager = LoginManager(app)
login_manager.login_view = 'home'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------
# ROUTES
# -----------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/discover')
def discover():
    q = Event.query
    title = request.args.get('title', '').strip()
    loc   = request.args.get('location', '')
    cat   = request.args.get('category', '')
    guests = request.args.get('guests', type=int)

    # filter on Event.title to match your template
    if title:
        q = q.filter(Event.title.ilike(f'%{title}%'))
    if loc:
        q = q.filter_by(location=loc)
    if cat:
        q = q.filter_by(category=cat)
    if guests:
        q = q.filter(Event.capacity >= guests)  # Fixed: changed from max_guests to capacity

    events = q.all()
    return render_template('discover.html', events=events)



@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')


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
    print("=== LOGIN ATTEMPT ===")
    print("Form data:", dict(request.form))

    email = request.form['email']
    pwd = request.form['password']
    role = request.form.get('type', 'user')

    print(f"Email: {email}")
    print(f"Password: {pwd}")
    print(f"Role: {role}")

    user = User.query.filter_by(email=email).first()
    print(f"User found: {user}")

    if user:
        print(f"User role: {user.role}")
        print(f"Password check: {check_password_hash(user.password, pwd)}")

    if not user or user.role != role or not check_password_hash(user.password, pwd):
        print("LOGIN FAILED")
        flash("Invalid credentials or role", "signin")
        return redirect(url_for('home'))

    print("LOGIN SUCCESS")
    login_user(user)
    flash("Logged in successfully!", "signin")
    print("===================")
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
        total_earnings=total_earnings   
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
    # send them back to the right anchor on either dashboard
    anchor = 'profile'
    return redirect(url_for('account') if current_user.role=='organizer'
                    else url_for('profile') + f'#{anchor}')

@app.route('/profile')
@login_required
def profile():
    if current_user.role != 'user':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    # Show the user's own bookings:
    user_bookings = Booking.query.filter_by(customer_email=current_user.email).all()

    return render_template(
        'user-dashboard.html',
        user=current_user,
        bookings=user_bookings
    )

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
            location     = request.form['location'],
            price        = float(request.form['price']),
            organizer_id = current_user.id,
            guests_limit = int(request.form['capacity'])  
            # time         = request.form['time_single'],
           # category     = request.form['category'],
           # image_url    = request.form.get('image_url'),
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created!", "success")
        return redirect(url_for('event_page', event_id=event.id))
    return render_template('launch_event.html')

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

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.organizer_id:
        abort(403)
    
    # Delete associated bookings first
    Booking.query.filter_by(event_id=event_id).delete()
    Transaction.query.filter_by(event_id=event_id).delete()
    
    # Delete the event
    db.session.delete(event)
    db.session.commit()
    
    flash("Event deleted successfully!", "success")
    return redirect(url_for('account'))
    
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
        # event.time        = request.form['time_single']    
        event.location    = request.form['location']
        event.price       = float(request.form['price'])
        event.guests_limit = int(request.form['capacity'])    # capacity -> guests_limit
        db.session.commit()
        flash("Event updated!", "success")
        return redirect(url_for('event_page', event_id=event.id))
    return render_template('edit_event.html', event=event)

def create_test_user(email, role):
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f" User {email} already exists, skipping...")
        return

    # Create new user with explicit password
    password_hash = generate_password_hash("test")
    print(f" Creating user {email} with hash: {password_hash[:20]}...")

    u = User(
        name="Test " + role.title(),
        email=email,
        password=password_hash,
        role=role
    )
    db.session.add(u)
    db.session.commit()

    # Verify the user was created correctly
    created_user = User.query.filter_by(email=email).first()
    if created_user:
        test_check = check_password_hash(created_user.password, "test")
        print(f" User {email} created successfully. Password check: {test_check}")
    else:
        print(f" ERROR: Failed to create user {email}")

@app.route('/debug/form', methods=['POST'])
def debug_form():
    print("=== FORM DEBUG ===")
    print("Form data:", dict(request.form))
    print("Method:", request.method)
    print("==================")
    return f"Form data: {dict(request.form)}"

@app.route('/debug/users')
def debug_users():
    users = User.query.all()
    result = "<h2>All Users in Database:</h2>"
    for user in users:
        result += f"<p>ID: {user.id}, Email: {user.email}, Role: {user.role}, Name: {user.name}</p>"
    return result

@app.route('/debug/routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint} ({rule.methods})")
    return "<br>".join(routes)


# -----------------------
# INIT & RUN 
# -----------------------
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Remove all existing tables
        db.create_all()  # create databases
        create_test_user("test_user@test.com", "user")  
        create_test_user("test_org@test.com", "organizer")
        # Every restart reset all data records
        # List all users
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        for user in users:
            print(f"  - {user.email} ({user.role})")
    app.run(debug=True)
