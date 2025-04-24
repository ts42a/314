from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -----------------------
# DATABASE MODELS
# -----------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'organizer'
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    dob = db.Column(db.String(50))   # for users
    abn = db.Column(db.String(50))   # for organizers

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(300))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    organizer = db.relationship('User', backref='events')

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
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    user_type = request.form.get('type', 'user')
    phone = request.form.get('phone')
    address = request.form.get('address')
    abn = request.form.get('abn') if user_type == 'organizer' else None
    dob = request.form.get('dob') if user_type == 'user' else None

    if password != confirm_password:
        flash("Passwords do not match", "signup")
        return redirect(url_for('home'))

    if User.query.filter_by(email=email).first():
        flash("Email already exists. Try logging in.", "signup")
        return redirect(url_for('home'))

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password, role=user_type, phone=phone, address=address, abn=abn, dob=dob)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash("Signup successful!", "signup")
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user_type = request.form.get('type', 'user')

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("No account found with that email.", "signin")
        return redirect(url_for('home'))

    if user.role != user_type:
        flash("Account role mismatch. Please select the correct role.", "signin")
        return redirect(url_for('home'))

    if not check_password_hash(user.password, password):
        flash("Invalid password", "signin")
        return redirect(url_for('home'))

    login_user(user)
    flash("Logged in successfully!", "signin")
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "signin")
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return f"""
    <h2>Welcome, {current_user.name}!</h2>
    <p>Your role: {current_user.role}</p>
    <p>Email: {current_user.email}</p>
    <p>Phone: {current_user.phone}</p>
    <p>Address: {current_user.address}</p>
    {'<p>ABN: ' + current_user.abn + '</p>' if current_user.role == 'organizer' else ''}
    {'<p>Date of Birth: ' + current_user.dob + '</p>' if current_user.role == 'user' else ''}
    <a href="/logout">Logout</a>
    """

@app.route('/launch_event', methods=['GET', 'POST'])
@login_required
def launch_event():
    if current_user.role != 'organizer':
        flash("You must be an organizer to create events.", "signin")
        return redirect(url_for('home'))

    if request.method == 'POST':
        event_type = request.form.get('event_type')

        # Validation
        if event_type == 'multi':
            required_fields = ['date_start', 'date_end', 'time_start', 'time_end']
        else:
            required_fields = ['date_single', 'time_single']
        
        for field in required_fields:
            if not request.form.get(field):
                flash("Please fill out all required date and time fields.", "signup")
                return redirect(url_for('launch_event'))

        # Parse date and time
        if event_type == 'multi':
            date = f"{request.form['date_start']} to {request.form['date_end']}"
            time = f"{request.form['time_start']} - {request.form['time_end']}"
        else:
            date = request.form['date_single']
            time = request.form['time_single']

        event = Event(
            title=request.form['title'],
            description=request.form['description'],
            date=date,
            time=time,
            location=request.form['location'],
            price=float(request.form['price']),
            capacity=int(request.form['capacity']),
            category=request.form['category'],
            image_url=request.form.get('image_url'),
            organizer_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for('event_page', event_id=event.id))

    return render_template('lunch_event.html')

@app.route('/event/<int:event_id>')
def event_page(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', event=event)

# -----------------------
# RUN
# -----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
