from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import datetime
import json
import random

app = Flask(__name__)
app.secret_key = "skyline_super_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skyline.db'
db = SQLAlchemy(app)



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'neuviseon@gmail.com'
app.config['MAIL_PASSWORD'] = 'nlas ktzw xxpx zpzc'
app.config['MAIL_DEFAULT_SENDER'] = 'neuviseon@gmail.com'

mail = Mail(app)

COUNTRIES_LIST = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", 
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", 
    "Belgium", "Belize", "Bolivia", "Brazil", "Canada", "Chile", "China", "Colombia", 
    "Croatia", "Cuba", "Czech Republic", "Denmark", "Egypt", "Ethiopia", "Fiji", 
    "Finland", "France", "Germany", "Greece", "Hong Kong", "Hungary", "Iceland", 
    "India", "Indonesia", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", 
    "Kenya", "Kuwait", "Lebanon", "Malaysia", "Maldives", "Mexico", "Morocco", 
    "Netherlands", "New Zealand", "Nigeria", "Norway", "Oman", "Pakistan", "Panama", 
    "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Russia", "Saudi Arabia", 
    "Singapore", "South Africa", "South Korea", "Spain", "Sri Lanka", "Sweden", 
    "Switzerland", "Taiwan", "Thailand", "Turkey", "Ukraine", "United Arab Emirates", 
    "United Kingdom", "Vietnam"
]
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    yob = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_country = db.Column(db.String(50), nullable=False)
    from_city = db.Column(db.String(50), nullable=False)
    to_country = db.Column(db.String(50), nullable=False)
    to_city = db.Column(db.String(50), nullable=False)
    dep_date = db.Column(db.String(20), nullable=False)
    dep_time = db.Column(db.String(20), nullable=False)
    ret_date = db.Column(db.Text, nullable=False) 
    ret_time = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    tickets_economy = db.Column(db.Integer)
    tickets_business = db.Column(db.Integer)
    tickets_first = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    promo_code = db.Column(db.String(50), nullable=False)
    trip_type=db.Column(db.String(50), nullable=False)
    status=db.Column(db.String(20),nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    flight = db.relationship('Flight', backref='bookings')
    first_name = db.Column(db.String(100))
    middle_initial = db.Column(db.String(1))
    last_name = db.Column(db.String(100))
    suffix = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    nationality = db.Column(db.String(50))
    status = db.Column(db.String(50)) 
    tier = db.Column(db.String(20)) 
    seat_number = db.Column(db.String(10))
    total_paid = db.Column(db.Float)
    return_date = db.Column(db.String(50))
    return_time = db.Column(db.String(50))
    seat_status = db.Column(db.String(20))

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=False) 
    category = db.Column(db.String(50), nullable=False)  

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    topic = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)   


@app.route('/')
def index():
    return render_template('index.html')



@app.template_filter('format_json_dates')
def format_json_dates(json_str):
    if not json_str or json_str == "none" or json_str == "[]":
        return "N/A"
    try:
        data = json.loads(json_str)
        return ", ".join([f"{item['date']} ({item['time']})" for item in data])
    except:
        return json_str 

@app.after_request
def add_header(response):
  
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/booking')
def booking():

  
    now = datetime.datetime.now()
    twenty_four_hours_later = now + timedelta(hours=24)
    current_date_str = now.strftime('%Y-%m-%d')
    
  
    upcoming_flights = Flight.query.filter(Flight.dep_date >= current_date_str).all()
    
  
    unique_timetable = {}

    for f in upcoming_flights:
        try:
  
            dep_time_obj = datetime.datetime.strptime(f"{f.dep_date} {f.dep_time}", "%Y-%m-%d %H:%M")
            
  
            if now <= dep_time_obj <= twenty_four_hours_later:
                
                key = f"{f.dep_date}_{f.dep_time}_{f.to_city}"
                
                if key not in unique_timetable:
                    unique_timetable[key] = f
        except ValueError:
            continue
    
    
    timetable_flights = list(unique_timetable.values())
    timetable_flights.sort(key=lambda x: x.dep_time)
    


    query = Flight.query


    trip_type = request.args.get('trip_type')
    if trip_type:
        query = query.filter(Flight.trip_type == trip_type)


    seat_class = request.args.get('seat_class')
    if seat_class == 'economy':
        query = query.filter(Flight.tickets_economy > 0)
    elif seat_class == 'business':
        query = query.filter(Flight.tickets_business > 0)
    elif seat_class == 'first':
        query = query.filter(Flight.tickets_first > 0)


    from_city = request.args.get('from_city')
    if from_city:
        query = query.filter(Flight.from_city.contains(from_city))
    
    to_city = request.args.get('to_city')
    if to_city:
        query = query.filter(Flight.to_city.contains(to_city))


    dep_date = request.args.get('dep_date')
    if dep_date:
        query = query.filter(Flight.dep_date == dep_date)


    if request.args.get('has_promo') == 'yes':
        query = query.filter(Flight.promo_code != 'none', Flight.promo_code != '')


    sort_by = request.args.get('sort_by', 'dep_date')
    if sort_by == 'price':
        query = query.order_by(Flight.price.asc())
    else:
        query = query.order_by(Flight.dep_date.asc())


    flights = query.all()



    return render_template('booking.html', 
                           flights=flights, 
                           timetable=timetable_flights, 
                           calc_arrival=calculate_arrival)


@app.route('/checkout/<int:flight_id>', methods=['GET', 'POST'])
def checkout(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    


    saved_data = None
    if session.get('pending_flight_id') == flight_id:
        saved_data = session.get('pending_booking')
    

    all_bookings = Booking.query.filter_by(flight_id=flight_id).all()
    

    occupied_by_tier = {
        'first': [b.seat_number for b in all_bookings if b.tier == 'first'],
        'business': [b.seat_number for b in all_bookings if b.tier == 'business'],
        'economy': [b.seat_number for b in all_bookings if b.tier == 'economy']
    }

    return render_template('checkout.html', 
                           flight=flight, 
                           calc_arrival=calculate_arrival,
                           occupied_seats=occupied_by_tier,
                           restored_data=saved_data)

@app.route('/book_flight/<int:flight_id>')
def book_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id) #
    return render_template('checkout.html', flight=flight, calc_arrival=calculate_arrival)

@app.route('/about')
def about():
    return render_template('index.html')
@app.route('/contact')
def contact():
    return render_template('index.html')

@app.route('/baggage')
def baggage():
    return render_template('baggage.html')
@app.route('/payment')
def payment():
    return render_template('payment.html')
@app.route('/booking&checkin')
def bookinginfo():
    return render_template('checkininfo.html')
@app.route('/specialassistance')
def specialassist():
    return render_template('special.html')
@app.route('/airlinepolicies')
def policies():
    return render_template('policies.html')
@app.route('/popular')
def popular():
    local_dest = Destination.query.filter_by(category='local').all()
    intl_dest = Destination.query.filter_by(category='international').all()
    return render_template('popular.html', local=local_dest, international=intl_dest)

def calculate_arrival(start_time_str, duration_str):
    if not start_time_str or start_time_str == "none" or not duration_str:
        return "--:--"
    
    try:
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M")
        
        clean_duration = duration_str.lower().replace('hrs', 'h').strip()
        
        if 'h' in clean_duration:
            hours = int(clean_duration.split('h')[0].strip())
            minutes = 0
            if 'm' in clean_duration:
                minutes = int(clean_duration.split('h')[1].split('m')[0].strip())
        else:
            hours = int(clean_duration)
            minutes = 0
            
        arrival_time = start_time + timedelta(hours=hours, minutes=minutes)
        return arrival_time.strftime("%H:%M")
    except (ValueError, IndexError):
        return "--:--"

@app.route('/edittickets/<int:flight_id>', methods=['GET', 'POST'])
def edittickets(flight_id):
    flight = Flight.query.get_or_404(flight_id)

    if request.method == 'POST':
        try:
            flight.trip_type = request.form.get('trip_type')
            flight.from_country = request.form.get('from_country')
            flight.from_city = request.form.get('from_city')
            flight.to_country = request.form.get('to_country')
            flight.to_city = request.form.get('to_city')
            
            flight.dep_date = request.form.get('dep_date')
            flight.dep_time = request.form.get('dep_time')
            
            if flight.trip_type == "one way trip":
                flight.ret_date = "none"
                flight.ret_time = "none"
            else:
                bubble_data = request.form.get('ret_date')
                flight.ret_date = bubble_data if bubble_data else "[]"
                flight.ret_time = "multiple"
            
            flight.tickets_economy = int(request.form.get('tickets_economy') or 0)
            flight.tickets_business = int(request.form.get('tickets_business') or 0)
            flight.tickets_first = int(request.form.get('tickets_first') or 0)
            flight.price = float(request.form.get('price') or 0)
            
            if flight.trip_type == "round trip" and (not flight.ret_date or flight.ret_date == "[]"):
                flight.status = "CANCELLED"[cite: 2]
            
            db.session.commit()
            flash("Flight Updated Successfully!")
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Update Error: {e}")
            return f"Error: {e}"

    return render_template('edittickets.html', flight=flight, countries=COUNTRIES_LIST)

@app.route('/addpromos')
def addpromos():
    return render_template('index.html')

@app.route('/editpromos')
def editpromos():
    return render_template('index.html')

@app.route('/archivetickets')
def archivetickets():
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/archivepromos')
def archivepromos():
    return render_template('index.html')

@app.route('/managebook')
def managebook():
    return render_template('index.html')

@app.route('/archivebook')
def archivebook():
    return render_template('index.html')

@app.route('/manageuser')
def manageuser():
    return render_template('index.html')

@app.route('/logs')
def logs():
    return render_template('index.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['first_name'] = user.first_name
            session['role'] = user.role
            session['is_admin'] = user.role == "admin"
            
            flash(f"Welcome back, {user.first_name}!", "success")

            if 'pending_booking' in session:
                flight_id = session.get('pending_flight_id')
                return redirect(url_for('checkout', flight_id=flight_id))
            
            return redirect(url_for('index'))
        
        else:
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        yob = request.form.get('yob')
        email = request.form.get('email')
        pw = request.form.get('password')
        pw_confirm = request.form.get('confirm_password')
        if pw != pw_confirm:
            return "Passwords do not match!"

        if User.query.filter_by(email=email).first():
            return "Email already exists!"

        hashed_pw = generate_password_hash(pw, method='scrypt')

        new_user = User(first_name=fname, last_name=lname, yob=yob, email=email, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration Successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/addtickets', methods=['GET', 'POST'])
def addtickets():
    countries_list = ["Afghanistan", "Australia", "Japan", "Philippines", "United States"]
    
    if request.method == 'POST':
        try:
            from_country = request.form.get('from_country')
            from_city = request.form.get('from_city')
            to_country = request.form.get('to_country')
            to_city = request.form.get('to_city')
            
            if from_city == to_city:
                flash("Error: Origin and Destination cities cannot be the same.")
                return render_template('addtickets.html', countries=countries_list)

            economy_seats = int(request.form.get('tickets_economy') or 0)
            business_seats = int(request.form.get('tickets_business') or 0)
            first_seats = int(request.form.get('tickets_first') or 0)
            flight_price = float(request.form.get('price') or 0)

            new_flight = Flight(
                from_country=from_country,
                from_city=from_city,
                to_country=to_country,
                to_city=to_city,
                dep_date=request.form.get('dep_date'),
                dep_time=request.form.get('dep_time'),
                ret_date="none",
                ret_time="none",
                duration=request.form.get('duration') or "N/A",
                tickets_economy=economy_seats,
                tickets_business=business_seats,
                tickets_first=first_seats,
                trip_type="one way trip", 
                price=flight_price,
                promo_code=request.form.get('promo_code') or "none",
                status = "active"
            )
            
            db.session.add(new_flight)
            db.session.commit()
            
            flash("Flight Created Successfully!")
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            db.session.rollback()
            print(f"System Log - Add Flight Failure: {e}") 
            return f"Error: {e}. Please ensure all required fields are filled."

    return render_template('addtickets.html', countries=COUNTRIES_LIST)

@app.route('/addticketsround', methods=['GET', 'POST'])
def addticketsround():

    if request.method == 'POST':
        raw_price = float(request.form.get('price', 0))
        final_price = raw_price * 2
        trip_type_value = "round trip"
        
        return_schedules = request.form.get('return_schedules_data') 
        
        new_flight = Flight(
            from_country=request.form.get('from_country'),
            from_city=request.form.get('from_city'),
            to_country=request.form.get('to_country'),
            to_city=request.form.get('to_city'),
            dep_date=request.form.get('dep_date'),
            dep_time=request.form.get('dep_time'),
            ret_date=return_schedules, 
            ret_time="multiple", 
            duration=request.form.get('duration'),
            tickets_economy=request.form.get('tickets_economy'),
            tickets_business=request.form.get('tickets_business'),
            tickets_first=request.form.get('tickets_first'),
            trip_type=trip_type_value, 
            price=final_price,
            promo_code=request.form.get('promo_code'),
            status="active"
        )
        
        db.session.add(new_flight)
        db.session.commit()
        flash("Round-Trip Flight with Multiple Returns Added!")
        return redirect(url_for('admin_dashboard'))

    return render_template('addticketsround.html', countries=COUNTRIES_LIST)
@app.route('/delete_flight/<int:flight_id>', methods=['POST'])
def delete_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    db.session.delete(flight)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/booked-flights')
def bookedflights():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_tickets = Booking.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('bookedflights.html', purchased_tickets=user_tickets)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    now = datetime.datetime.now()
    ten_hours_later = now + timedelta(hours=120)
    current_date_str = now.strftime('%Y-%m-%d')
    
    today_flights = Flight.query.filter(Flight.dep_date == current_date_str).all()
    
    timetable_flights = []
    for f in today_flights:
        try:
            dep_time_obj = datetime.datetime.strptime(f"{f.dep_date} {f.dep_time}", "%Y-%m-%d %H:%M")
            if now <= dep_time_obj <= ten_hours_later:
                timetable_flights.append(f)
        except ValueError:
            continue
    
    timetable_flights.sort(key=lambda x: x.dep_time)
   

   
    all_flights = Flight.query.all()
    all_bookings = Booking.query.order_by(Booking.id.desc()).all()
    all_users = User.query.order_by(User.role.asc()).all()
    all_destinations = Destination.query.all()
    all_messages = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).all()

   
    return render_template('admin.html', 
                           flights=all_flights, 
                           bookings=all_bookings, 
                           users=all_users,
                           destinations=all_destinations,
                           messages=all_messages,
                           timetable=timetable_flights)

@app.route('/process_booking/<int:flight_id>', methods=['POST'])
def process_booking(flight_id):
    if 'user_id' not in session:
        session['pending_booking'] = request.form.to_dict()
        session['pending_flight_id'] = flight_id
        flash("Please log in to complete your booking. Your details have been saved!", "info")
        return redirect(url_for('login'))

    u_id = session.get('user_id')
    flight = Flight.query.get_or_404(flight_id)
    
    ret_selection = request.form.get('selected_return') 
    ret_date, ret_time = (None, None)
    if ret_selection:
        ret_date, ret_time = ret_selection.split('|')

    try:
        p_count = int(request.form.get('p_count', 1))
        tier = request.form.get('tier', 'economy')
        total_amount = float(request.form.get('total_amount', '0').replace(',', ''))
        selected_seats_str = request.form.get('selected_seat', "")
        
        seats_list = [s.strip() for s in selected_seats_str.split(',') if s.strip()]

        if seats_list:
            seat_stat = "CHOSEN"
        if not seats_list:
            import random
            
            rows = 5 if tier == 'first' else (10 if tier == 'business' else 20)
            side_seats = 1 if tier == 'first' else (2 if tier == 'business' else 3)
            letters = "ABCDEF"[:side_seats * 2]

            all_possible_seats = [f"{r}{l}" for r in range(1, rows + 1) for l in letters]

            occupied = [b.seat_number for b in Booking.query.filter_by(flight_id=flight_id, tier=tier).all()]
            
            available_seats = [s for s in all_possible_seats if s not in occupied]
            random.shuffle(available_seats)
            
            seats_list = available_seats[:p_count]
            seat_stat = "AUTO-ASSIGNED"

        for i in range(1, p_count + 1):
            if tier == 'economy': 
                flight.tickets_economy -= 1
            elif tier == 'business': 
                flight.tickets_business -= 1
            elif tier == 'first': 
                flight.tickets_first -= 1

            current_seat = seats_list[i-1] if i <= len(seats_list) else "N/A"

                

            new_booking = Booking(
                user_id=session.get('user_id'),
                flight_id=flight.id,
                first_name=request.form.get(f'first_name_{i}'),
                middle_initial=request.form.get(f'mi_{i}'),
                last_name=request.form.get(f'last_name_{i}'),
                dob=request.form.get(f'dob_{i}'),
                nationality=request.form.get(f'nationality_{i}'),
                status=request.form.get(f'status_{i}'),
                tier=tier,
                seat_number= current_seat,
                total_paid=total_amount / p_count,
                return_date=ret_date,
                return_time=ret_time,
                seat_status = seat_stat
            )
            db.session.add(new_booking)

        db.session.commit()

        session.pop('pending_booking', None)
        session.pop('pending_flight_id', None)

        return redirect(url_for('success'))

    except Exception as e:
        db.session.rollback()
        print(f"Booking Error: {e}")
        return f"Error: {e}"
@app.route('/edit-ticket/<int:booking_id>', methods=['GET', 'POST'])
def edit_ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        new_seat = request.form.get('seat_number')
        if new_seat:
            booking.seat_number = new_seat
        db.session.commit()
        return redirect(url_for('bookedflights'))

    tier_prefix = booking.tier[0].lower()
    occupied_seats = [
        b.seat_number for b in Booking.query.filter_by(flight_id=booking.flight_id).all() 
        if b.seat_number != booking.seat_number and b.seat_number.startswith(tier_prefix)
    ]

    return render_template('edit_booking.html', 
                           booking=booking, 
                           flight=booking.flight, 
                           occupied_seats=occupied_seats)

@app.route('/refund-ticket/<int:booking_id>', methods=['POST'])
def refund_ticket(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != session['user_id']:
        flash("Unauthorized action.")
        return redirect(url_for('bookedflights'))

    db.session.delete(booking)
    db.session.commit()
    flash("Ticket refunded and removed successfully.")
    return redirect(url_for('bookedflights'))

@app.route('/ban-user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized action.")
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash("Cannot ban an administrator.")
    else:
        user.role = 'banned'
        db.session.commit()
        flash(f"User {user.email} has been banned.")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/add_destination', methods=['POST'])
def add_destination():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    image_file = request.form.get('image_path') 
    image_path = f"static/images/{image_file}"
    category = request.form.get('category')

    new_dest = Destination(name=name, description=description, image_path=image_path, category=category)
    db.session.add(new_dest)
    db.session.commit()
    flash("Destination Added!")
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_destination/<int:dest_id>', methods=['POST'])
def edit_destination(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    dest.name = request.form.get('name')
    dest.description = request.form.get('description')
    
    new_img = request.form.get('image_path')
    if new_img:
        dest.image_path = f"static/images/{new_img}"
        
    dest.category = request.form.get('category')
    db.session.commit()
    flash("Destination Updated!")
    return redirect(url_for('admin_dashboard'))


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        
        new_message = ContactMessage(
            first_name=request.form.get('fname'),
            last_name=request.form.get('lname'),
            email=request.form.get('email'),
            phone=request.form.get('number'),
            topic=request.form.get('topic'),
            message=request.form.get('message')
        )
        db.session.add(new_message)
        db.session.commit()
        
        return f'<script>alert("Message saved successfully!"); window.location.href="{url_for("index")}#contact";</script>'
        
    except Exception as e:
        db.session.rollback()
        return f'<script>alert("Error: Could not save message."); window.location.href="{url_for("index")}#contact";</script>'

@app.route('/admin/delete_message/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    
    return f'<script>alert("Message ignored and deleted."); window.location.href="{url_for("admin_dashboard")}";</script>'

@app.route('/admin/reply_message/<int:msg_id>', methods=['POST'])
def reply_message(msg_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    
    msg_to_reply = ContactMessage.query.get_or_404(msg_id)
    admin_response = request.form.get('reply_text')
    
    try:
        
        email_content = Message(
            subject=f"SkyLine Support: {msg_to_reply.topic}",
            recipients=[msg_to_reply.email],
            body=f"Hello {msg_to_reply.first_name},\n\n{admin_response}\n\n---\nSkyLine Administration"
        )
        
        mail.send(email_content)
        
        
        db.session.delete(msg_to_reply)
        db.session.commit()
        
        return f'<script>alert("Reply sent successfully!"); window.location.href="{url_for("admin_dashboard")}";</script>'
    
    except Exception as e:
        db.session.rollback()
        print(f"Mail Error: {e}")
        return f'<script>alert("Failed to send email. Check SMTP settings."); window.location.href="{url_for("admin_dashboard")}";</script>'

def send_receipt_email(recipient, booking):
    try:
        msg = Message(
            subject=f"SkyLine Receipt: {booking.flight.from_city} to {booking.flight.to_city}",
            recipients=[recipient]
        )
        
        
        arr_time = calculate_arrival(booking.flight.dep_time, booking.flight.duration)
        
        msg.html = render_template(
            'receipt_email.html', 
            booking=booking, 
            arrival_time=arr_time,
            print_date=datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
        )
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/admin/cancel_flight/<int:flight_id>', methods=['POST'])
def cancel_flight(flight_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    flight = Flight.query.get_or_404(flight_id)
    flight.status = "REFUNDED"
    db.session.commit()
    flash(f"Flight to {flight.to_city} has been CANCELLED and marked for refund.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delay_flight/<int:flight_id>', methods=['POST'])
def delay_flight(flight_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    flight = Flight.query.get_or_404(flight_id)
    new_time = request.form.get('new_time')
    
    if new_time:
        flight.status = f"Delayed: {new_time}"
        db.session.commit()
        flash(f"Flight to {flight.to_city} updated with delay.")
    
    return redirect(url_for('admin_dashboard'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)