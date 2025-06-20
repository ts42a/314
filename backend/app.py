from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote
from datetime import datetime, timedelta, date

import os
import qrcode
import uuid

try:
    from backend.models import db, User, Event, Booking, Transaction, Ticket, Notification, Card
except ModuleNotFoundError:
    try:
        from models import db, User, Event, Booking, Transaction, Ticket, Notification, Card
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

@app.route("/")
def index():
    return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper Functions
def generate_qr(data, folder="/qr"):
    os.makedirs(folder, exist_ok=True)
    relative_path = f"qr/{data}.png"
    full_path = os.path.join(folder, f"{data}.png")
    img = qrcode.make(data)
    img.save(full_path)
    return relative_path  
    
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

@app.route('/org-dashboard.html')
@login_required
def navigate_organizer_dashboard():
    if current_user.role != 'organizer':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))
    
    db.session.refresh(current_user)
    events = Event.query.filter_by(organizer_id=current_user.id).all()
    
    # Query bookings for this organizer's events with customer relationship
    bookings = Booking.query.join(Event).filter(
        Event.organizer_id == current_user.id
    ).outerjoin(User, Booking.customer_id == User.id).options(
        db.contains_eager(Booking.customer)
    ).all()
    
    transactions = Transaction.query.filter(
        (Transaction.event.has(organizer_id=current_user.id)) |
        (Transaction.event_id == None)
    ).order_by(Transaction.date.desc()).all()
    
    total_earnings = sum(
        (b.event.vip_price if t.ticket_type == "VIP" else b.event.general_price)
        for b in bookings
        for t in b.tickets
    )
    
    return render_template(
        'org-dashboard.html',
        organizer=current_user,
        events=events,
        bookings=bookings,
        transactions=transactions,
        total_earnings=total_earnings
    )
    
@app.route('/profile')
@login_required
def view_profile():
    return render_template('profile.html', user=current_user)
    
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():

    old_name = current_user.name  # Store old name
    
    current_user.name = request.form['name']
    current_user.phone = request.form.get('phone')

    current_user.address = request.form.get('address')
    
    if current_user.role == 'organizer':
        current_user.abn = request.form.get('abn')
        current_user.bank_name = request.form.get('bank_name')
        current_user.account_number = request.form.get('account_number')
        current_user.routing_number = request.form.get('routing_number')
    
    # Update all existing bookings with the new name
    if old_name != current_user.name:
        user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
        for booking in user_bookings:
            booking.customer_name = current_user.name
    
    db.session.commit()
    db.session.refresh(current_user)
    
    flash("Profile updated!", "success")
    anchor = 'profile'
    return redirect(url_for('navigate_organizer_dashboard') + f'#{anchor}' if current_user.role == 'organizer'
                    else url_for('navigate_user_dashboard') + f'#{anchor}')

@app.route('/user-dashboard.html')
@login_required
def navigate_user_dashboard():
    if current_user.role != 'user':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    db.session.refresh(current_user)

    user_bookings = Booking.query.filter_by(customer_email=current_user.email).all()
    today = date.today()
    total_spent = sum(b.total_price for b in user_bookings if b.status == 'approved')

    for b in user_bookings:
        if isinstance(b.event.date, str):
            b.event._parsed_date = datetime.strptime(b.event.date, '%Y-%m-%d').date()
        else:
            b.event._parsed_date = b.event.date

    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.timestamp.desc()).all()

    transactions = Transaction.query.join(Booking, Transaction.event_id == Booking.event_id)\
                    .filter(Booking.customer_email == current_user.email).all()

    return render_template(
        'user-dashboard.html',
        user=current_user,
        bookings=user_bookings,
        today=today,
        total_spent=total_spent,
        messages=notifications,
        transactions=transactions
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

    return redirect(url_for('navigate_organizer_dashboard') + '#payment')


#@app.route('/manual_booking', methods=['POST'])
#@login_required
#def manual_booking():
 #   if current_user.role != 'organizer':
#        flash("Access denied.", "danger")
 #       return redirect(url_for('home'))
#    b = Booking(
#        event_id       = request.form['event_id'],
 #       customer_name  = request.form['customer_name'],
 #       customer_email = request.form['customer_email'],
#        tickets_qty    = int(request.form['tickets_qty']),
#        payment_method = request.form['payment_method']
#    )
 #   db.session.add(b)
#    db.session.commit()

#    t = Transaction(
#        event_id = b.event_id,
#        amount   = b.tickets_qty * b.event.price,
#        status   = 'Manual'
#    )
#    db.session.add(t)
 #   db.session.commit()

#    flash("Manual booking added!", "success")
 #   return redirect(url_for('account') + '#bookings')

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Allow only the organizer or the user who booked it
    if current_user.role == 'organizer':
        is_authorized = booking.event.organizer_id == current_user.id
    else:
        is_authorized = booking.customer_email == current_user.email

    if not is_authorized:
        abort(403)

    # Delete associated tickets FIRST to avoid foreign key issues
    for ticket in booking.tickets:
        db.session.delete(ticket)

    # Restore the guests_limit
    booking.event.guests_limit += booking.tickets_qty
    
    # Delete associated transactions (if any)
    Transaction.query.filter_by(event_id=booking.event_id).delete()

    # Delete the booking
    db.session.delete(booking)
    db.session.commit()

    flash("Booking canceled successfully!", "success")

    # Redirect based on user type
    if current_user.role == 'organizer':
        return redirect(url_for('navigate_organizer_dashboard') + '#bookings')
    return redirect(url_for('navigate_user_dashboard') + '#bookings')

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
        event_type = request.form['event_type']
        
        # Handle VIP price (optional)
        vip_price = None
        if 'offer_vip' in request.form and request.form.get('vip_price'):
            vip_price = float(request.form['vip_price'])
        
        # Common fields for both event types
        common_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'location': request.form['location'],
            'general_price': float(request.form['general_price']),
            'vip_price': vip_price,
            'organizer_id': current_user.id,
            'guests_limit': int(request.form['capacity']),
            'event_type': event_type,
            'category': request.form.get('category'),
            'image_url': request.form.get('image_url'),
        }
        
        if event_type == 'single':
            # Single-day event
            event = Event(
                date=request.form['date_single'],
                time=request.form['time_single'],
                **common_data
            )
        else:
            # Multi-day event
            event = Event(
                date=request.form['date_start'],
                end_date=request.form['date_end'],
                time=request.form['time_start'],
                end_time=request.form['time_end'],
                **common_data
            )
        
        try:
            db.session.add(event)
            db.session.commit()
            flash("Event created successfully!", "success")
            return redirect(url_for('event_page', event_id=event.id))
        except Exception as e:
            db.session.rollback()
            flash("Error creating event. Please try again.", "danger")
            return render_template('launch_event.html')
    
    return render_template('launch_event.html')

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Only the organizer who created the event can delete it
    if current_user.role != 'organizer' or event.organizer_id != current_user.id:
        abort(403)

    # Delete all bookings and transactions tied to this event
    Booking.query.filter_by(event_id=event.id).delete()
    Transaction.query.filter_by(event_id=event.id).delete()

    # Finally delete the event itself
    db.session.delete(event)
    db.session.commit()

    flash("Event deleted successfully!", "success")
    return redirect(url_for('navigate_organizer_dashboard')) 

@app.route('/event/<int:event_id>')
def event_page(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', event=event)

@app.route('/book_event/<int:event_id>', methods=['POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)

    general_qty = int(request.form.get('general_qty', 0))
    vip_qty = int(request.form.get('vip_qty', 0)) if request.form.get('vip_qty') else 0

    total_price = (general_qty * event.general_price) + (vip_qty * event.vip_price)

    if general_qty == 0 and vip_qty == 0:
        flash("You must select at least one ticket.", "warning")
        return redirect(url_for('event_page', event_id=event.id))

    # Payment method validation
    card_option = request.form.get('card_option')
    payment_method = "Unknown"

    if card_option == 'saved':
        card_id = int(request.form.get('saved_card_id', 0))
        cvv = request.form.get('saved_card_cvv', '').strip()
        card = Card.query.filter_by(id=card_id, user_id=current_user.id).first()
        if not card or not cvv:
            flash("Invalid saved card or CVV.", "danger")
            return redirect(url_for('event_page', event_id=event.id))
        payment_method = f"Saved Card ending in {card.last4}"

    elif card_option == 'new':
        card_number = request.form.get('new_card_number', '').strip()
        cardholder_name = request.form.get('new_cardholder_name', '').strip()
        exp_month = request.form.get('new_expiry_month')
        exp_year = request.form.get('new_expiry_year')
        cvv = request.form.get('new_cvv', '').strip()

        if not all([card_number, cardholder_name, exp_month, exp_year, cvv]):
            flash("All new card fields are required.", "danger")
            return redirect(url_for('event_page', event_id=event.id))

        payment_method = f"New Card ending in {card_number[-4:]}"
    else:
        flash("Select a valid payment option.", "danger")
        return redirect(url_for('event_page', event_id=event.id))

    # Create pending booking
    booking = Booking(
        user_id=current_user.id,
        customer_id=current_user.id,
        customer_name=current_user.name,
        customer_email=current_user.email,
        event_id=event.id,
        vip_qty=vip_qty,
        general_qty=general_qty,
        tickets_qty=general_qty + vip_qty,
        total_price=total_price,
        payment_method=payment_method,
        status='pending'  # ← Wait for organizer approval
    )
    db.session.add(booking)

    # Create transaction record (not completed yet)
    transaction = Transaction(
        event_id=event.id,
        amount=total_price,
        status='pending'
    )
    db.session.add(transaction)

    db.session.commit()

    flash("Booking submitted. Awaiting organizer confirmation.", "info")
    return redirect(url_for('navigate_user_dashboard'))


@app.route('/approve_booking/<int:booking_id>', methods=['POST'])
@login_required
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    event = booking.event

    if current_user.id != event.organizer_id:
        abort(403)

    if event.guests_limit >= booking.tickets_qty:
        booking.status = 'approved'
        event.guests_limit -= booking.tickets_qty

    else:
        flash("Not enough spots available to approve this booking.", "danger")

    # Generate VIP tickets
    for i in range(booking.vip_qty):
        ticket_code = str(uuid.uuid4())[:12]
        qr_img = qrcode.make(ticket_code)
        filename = f"qr_{booking.id}_vip_{i}.png"
        folder_path = os.path.join("static", "qr")
        os.makedirs(folder_path, exist_ok=True)
        qr_img.save(os.path.join(folder_path, filename))

        ticket = Ticket(
            booking_id=booking.id,
            ticket_code=ticket_code,
            ticket_type="VIP",
            qr_code_path=f"qr/{filename}",
            status='Active'
        )
        db.session.add(ticket)

    # Generate General tickets
    for i in range(booking.general_qty):
        ticket_code = str(uuid.uuid4())[:12]
        qr_img = qrcode.make(ticket_code)
        filename = f"qr_{booking.id}_gen_{i}.png"
        folder_path = os.path.join("static", "qr")
        qr_img.save(os.path.join(folder_path, filename))

        ticket = Ticket(
            booking_id=booking.id,
            ticket_code=ticket_code,
            ticket_type="General",
            qr_code_path=f"qr/{filename}",
            status='Active'
        )

        db.session.add(ticket)

        # Send notification
        if booking.customer_id:
            db.session.add(Notification(
                recipient_id=booking.customer_id,
                sender_name=current_user.name,
                subject="Booking Approved",
                message=f"Your booking for '{event.title}' has been approved. Your tickets are now available."
            ))

    db.session.commit()
    flash("Booking approved.", "success")
    return redirect(url_for('navigate_organizer_dashboard'))


@app.route('/reject_booking/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    event = booking.event

    # Ensure current user is the organizer
    if current_user.id != event.organizer_id:
        abort(403)

    booking.status = 'rejected'

    # Create notification for customer
    if booking.customer_id:
        notif = Notification(
            recipient_id=booking.customer_id,
            sender_name=current_user.name,
            subject="Booking Rejected",
            message=f"Unfortunately, your booking for '{event.title}' was rejected. Please contact the organizer if you need more info.",
        )
        db.session.add(notif)

    db.session.commit()
    flash('Booking rejected and user notified.', 'warning')
    return redirect(url_for('navigate_organizer_dashboard'))


    
    
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
        event_type = request.form['event_type']

        # Store previous info for NTF-01 status comparison
        old_date = event.date
        old_end_date = event.end_date

        # Handle VIP price
        vip_price = None
        if 'offer_vip' in request.form and request.form.get('vip_price'):
            vip_price = float(request.form['vip_price'])

        # Update common fields
        event.title = request.form['title']
        event.description = request.form['description']
        event.location = request.form['location']
        event.general_price = float(request.form['general_price'])
        event.vip_price = vip_price
        event.guests_limit = int(request.form['capacity'])
        event.event_type = event_type
        event.category = request.form.get('category')
        event.image_url = request.form.get('image_url')

        # Update date/time fields
        if event_type == 'single':
            event.date = request.form['date_single']
            event.time = request.form['time_single']
            event.end_date = None
            event.end_time = None
        else:
            event.date = request.form['date_start']
            event.end_date = request.form['date_end']
            event.time = request.form['time_start']
            event.end_time = request.form['time_end']

        try:
            db.session.commit()

            ### ✅ NOTIFY ALL BOOKED USERS ABOUT CHANGES (NTF-02)
            booked_users = User.query.join(Booking, Booking.customer_id == User.id)\
                .filter(Booking.event_id == event.id).distinct().all()

            for user in booked_users:
                db.session.add(Notification(
                    recipient_id=user.id,
                    sender_name=current_user.name,
                    subject=f"Event Updated: {event.title}",
                    message=f"The event '{event.title}' has been updated. Please review the latest details.",
                ))

            ### DETECT & NOTIFY STATUS CHANGES (NTF-01)
            from datetime import date
            today = date.today()

            # Check current event status based on dates
            start_date = datetime.strptime(event.date, "%Y-%m-%d").date()
            end_date = datetime.strptime(event.end_date, "%Y-%m-%d").date() if event.end_date else start_date

            if today < start_date:
                status = "Open"
            elif start_date <= today <= end_date:
                status = "Running"
            else:
                status = "Closed"

            for user in booked_users:
                db.session.add(Notification(
                    recipient_id=user.id,
                    sender_name="System",
                    subject=f"Event Status: {event.title} is now {status}",
                    message=f"The event '{event.title}' is now marked as **{status}**. Stay updated via your dashboard.",
                ))

            db.session.commit()

            flash("Event updated successfully!", "success")
            return redirect(url_for('event_page', event_id=event.id))

        except Exception as e:
            db.session.rollback()
            flash("Error updating event. Please try again.", "danger")
            return render_template('edit_event.html', event=event)

    return render_template('edit_event.html', event=event)



@app.route('/generate_ticket/<int:booking_id>', methods=['POST'])
@login_required
def generate_ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Only the customer can generate
    if current_user.role != 'user' or booking.customer_email != current_user.email:
        abort(403)

    # Simulate generation (PDF/QR not needed for test)
    flash("Ticket generated successfully!", "success")
    return redirect(url_for('view_ticket', booking_id=booking.id))

@app.route('/ticket/<int:booking_id>')
@login_required
def view_ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Booking must be approved
    if booking.status != 'approved':
        flash("This booking has not been approved yet.", "danger")
        if current_user.role == 'organizer':
            return redirect(url_for('navigate_organizer_dashboard') + '#bookings')
        return redirect(url_for('navigate_user_dashboard') + '#bookings')

    # Authorization check
    if current_user.role == 'user' and booking.customer_email != current_user.email:
        abort(403)
    elif current_user.role == 'organizer' and booking.event.organizer_id != current_user.id:
        abort(403)

    return render_template('ticket.html', booking=booking)

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

def create_test_event(organizer_email):
    organizer = User.query.filter_by(email=organizer_email, role='organizer').first()
    if not organizer:
        print(f" Organizer with email {organizer_email} not found. Skipping event creation.")
        return

    if Event.query.filter_by(title="Test Event").first():
        print("Test event already exists. Skipping.")
        return

    from datetime import date

    e = Event(
        title="Test Event",
        description="This is a demo event created on app startup.",
        date=date.today().strftime('%Y-%m-%d'),
        location="New York",
        general_price=20.0,
        vip_price=30.0,
        guests_limit=100,
        organizer_id=organizer.id
    )
    db.session.add(e)
    db.session.commit()
    print(f"Created test event: {e.title} for organizer {organizer.email}")

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


#payment methods
@app.route('/add_card', methods=['POST'])
@login_required
def add_card():
    number = request.form['card_number'].strip().replace(" ", "")
    card = Card(
        user_id=current_user.id,
        cardholder_name=request.form['cardholder_name'],
        last4=number[-4:],
        expiry_month=int(request.form['expiry_month']),
        expiry_year=int(request.form['expiry_year'])
    )
    db.session.add(card)
    db.session.commit()
    flash("Card added successfully!", "success")
    return redirect(url_for('navigate_user_dashboard') + "#payments")

@app.route('/edit_card/<int:card_id>', methods=['POST'])
@login_required
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        abort(403)
    card.cardholder_name = request.form['cardholder_name']
    card.expiry_month = int(request.form['expiry_month'])
    card.expiry_year = int(request.form['expiry_year'])
    db.session.commit()
    flash("Card updated.", "success")
    return redirect(url_for('navigate_user_dashboard') + "#payments")


@app.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        abort(403)
    db.session.delete(card)
    db.session.commit()
    flash("Card deleted.", "success")
    return redirect(url_for('navigate_user_dashboard') + "#payments")




# -----------------------
# INIT & RUN 
# -----------------------
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Remove all existing tables
        db.create_all()  # create databases
        create_test_user("test_user@test.com", "user")  
        create_test_user("test_org@test.com", "organizer")
        create_test_event("test_org@test.com")
        # Every restart reset all data records
        # List all users
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        for user in users:
            print(f"  - {user.email} ({user.role})")
    app.run(debug=True)