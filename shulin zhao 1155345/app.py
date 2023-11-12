# app.py
from flask import Flask, render_template, request, redirect, url_for, session,flash
from controller import Controller
from datetime import datetime
import json
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'
controller = Controller()  # Instantiate the Controller


@app.route('/dashboard')
def dashboard():
    print(session)  # Debug: Print the session to see what's inside
    if 'user' in session:
        user = session['user']
        role = user.get('role', '').lower()
        if role == 'admin':
            return controller.admin_dashboard()
        elif role == 'front_desk_staff':
            return controller.front_desk_dashboard()
        elif role == 'customer':
            return controller.customer_dashboard()
        # Handle other roles...
    return redirect(url_for('login'))

@app.route('/')
def main_index():
    return controller.index()

@app.route('/search', methods=['POST'])
def main_search_movie():
    return controller.search_movie()

@app.route('/view/<movie_id>')
def main_view_movie(movie_id):
    return controller.view_movie(movie_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success_message = None
    if request.method == 'POST':
        # Get user input from the registration form
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        # Call the register_user function in Controller
        role = "customer"
        new_user, error = controller.register_user(name, address, email, phone, username, password,role)
        if error is None:
            # Redirect to a success page or login page
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('registration_form.html', error=error,success_message=success_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        controller.load_users_from_file()
        username = request.form['username']
        password = request.form['password']
        user = controller.login_user(username, password)

        if user:
            session['user'] = {'username': user.username, 'role': user.role}
            # Redirect to the appropriate view based on the role
            if controller.is_admin_user(user):
                return controller.admin_dashboard()
            elif controller.is_front_desk_user(user):
                return controller.front_desk_dashboard()
            elif controller.is_customer_user(user):
                return controller.customer_dashboard()

        else:
            error = "Invalid username or password."
            
    #session.pop('_flashes', None)
    return render_template('login.html', error=error)

@app.route('/view_schedules/<int:movie_id>')
def view_schedules(movie_id):
   return controller.view_schedules(movie_id)
@app.route('/cancel_view_schedules/<int:movie_id>')
def cancel_view_schedules(movie_id):
   return controller.cancel_view_schedules(movie_id)

@app.route('/book_view_schedules/<int:movie_id>')
def book_view_schedules(movie_id):
   return controller.book_view_schedules(movie_id)

@app.route('/admin/add_screening/<int:movie_id>', methods=['GET', 'POST'])
def admin_add_screening(movie_id):
    movie = controller.get_movie_by_id(movie_id)
    if not movie:
        return "Movie not found", 404
    if request.method == 'POST':
        screening_date = datetime.strptime(request.form.get('screening_date'), '%Y-%m-%d')
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M')
        hall_name = request.form.get('hall_name')  
        
        success = controller.add_screening(movie_id, screening_date, start_time, hall_name)

        if success:
            flash('Screening added for the movie successfully.', 'success')
        else:
            flash('Failed to add screening because the selected time overlaps with an existing screening.', 'error')

        return redirect(url_for('cancel_view_schedules', movie_id=movie_id))
                
    else:
        halls = controller.get_all_cinema_halls()
        today = datetime.now().date()
        return render_template('admin_add_screening.html', movie=movie, halls=halls, today=today, movie_id=movie_id)

@app.route('/admin/add_movie', methods=['GET', 'POST'])
def admin_add_movie():
    # If accessing the page via GET, clear any previously flashed messages
    if request.method == 'GET':
        session.pop('_flashes', None)

    if 'user' in session and session['user']['role'].lower() == 'admin':
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            duration_mins = request.form.get('duration_mins')
            language = request.form.get('language')
            genre = request.form.get('genre')
            country = request.form.get('country')
            release_date = datetime.strptime(request.form.get('release_date'), "%Y-%m-%d")

            if len(title) > 255 or len(description) > 2000:  
                flash('Title or description too long.', 'custom-error')
                return controller.admin_dashboard()

            if not title or not description or not duration_mins or not language or not release_date or not country or not genre:
                flash('All fields are required.', 'custom-error')
                return controller.admin_dashboard()

            try:
                duration_mins = int(duration_mins)
                if duration_mins <= 0:
                    flash('Duration should be a positive integer.', 'custom-error')
                    return controller.admin_dashboard()
            except ValueError:
                flash('Duration should be a positive integer.', 'custom-error')
                return controller.admin_dashboard()

            success = controller.add_movie(title, description, duration_mins, language, release_date, country, genre)

            if success:
                flash('Movie added successfully.', 'success')
            else:
                flash('Failed to add movie. Make sure the movie title is unique.', 'custom-error')

            return controller.admin_dashboard()
        else:
            return render_template('admin_add_movie.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    return controller.logout()

@app.route('/book/<int:schedule_id>', methods=['GET', 'POST'])
def book(schedule_id):
    if request.method == 'POST':
        selected_seats = request.form.getlist('seats')
        if not selected_seats:
            flash('Please select at least one seat.', 'danger')
            return redirect(url_for('book', schedule_id=schedule_id))

        booking_id, booked_seats = controller.book( schedule_id, selected_seats)
        # booking_id, booked_seats = controller.book(customer, schedule_id, selected_seats, order_total, payment_method)
        return redirect(url_for('booking_details',schedule_id=schedule_id, booked_seats=",".join(booked_seats)))

    available_seats, unavailable_seats, all_seats_in_hall = controller.get_available_seats(schedule_id)
    return render_template('booking.html', all_seats_in_hall=all_seats_in_hall, schedule_id=schedule_id, available_seats=available_seats, unavailable_seats=unavailable_seats)

@app.route('/booking_details/<int:schedule_id>/<booked_seats>', methods=['GET', 'POST'])
def booking_details(schedule_id, booked_seats):
    data = controller.get_booking_details_data(session, booked_seats, schedule_id)
    if data['screeningDetail'] is None:
        flash('Screening not found!', 'error')
        return redirect(url_for('dashboard'))
    discountedAmount = 0  # Initialize discounted amount
    if request.method == 'POST':
        if session.get('discount_applied'):
            flash('A discount has already been applied!', 'error')
        else:
            coupon_code = request.form.get('discount_coupon')
            username = session['user']['username'] 
            user = controller.get_user_by_username(username) 
            
            if user:
                result = controller.apply_discount(user,coupon_code, data['orderTotal'])
                if result['status'] == 'success':
                    discountedAmount = result['discount']
                    flash('Discount applied successfully!', 'success')
                else:
                    flash(result['message'], 'error')
            
    finalTotal = data['orderTotal'] - discountedAmount
    print("finalTotal",finalTotal)
    print("discountedAmount",discountedAmount)
    
    return render_template('booking_details.html', 
                           schedule_id=schedule_id, 
                           booked_seats=data['booked_seat_positions'],
                           screeningDetail=data['screeningDetail'], 
                           orderTotal=data['orderTotal'], 
                           discountedAmount=discountedAmount,
                           finalTotal=finalTotal,
                           available_coupons=data['available_coupons'])
@app.route('/process_payment', methods=['POST'])
def process_payment():
    form_data = {
        'payment_method': request.form.get('payment_method'),
        'credit_card_number': request.form.get('credit_card_number'),
        'expiry_date': request.form.get('expiry_date'),
        'name_on_card_credit': request.form.get('name_on_card_credit'),
        'card_type': request.form.get('card_type'),
        'debit_card_number': request.form.get('debit_card_number'),
        'expiry_date_debit': request.form.get('expiry_date_debit'),
        'name_on_card_debit': request.form.get('name_on_card_debit'),
        'bank_name': request.form.get('bank_name'),
        'movie_title': request.form.get('movie_title', 'N/A'),
        'screening_date': request.form.get('screening_date', 'N/A'),
        'start_time': request.form.get('start_time', 'N/A'),
        'end_time': request.form.get('end_time', 'N/A'),
        'seats': request.form.getlist('seats'),  # This gets all values for 'seats' as a list
        'final_total': request.form.get('final_total', '0'),
    }
    print(form_data,"form_data")

    booking, notification = controller.create_booking(form_data)
    flash('Your payment was successful!', 'success')

    # Flash the notification content
    flash(notification.content, 'info')

    # Redirecting to booking_details.html with all necessary information
    return render_template('booking_confirmation.html', booking=booking, notification=notification)
@app.route('/view_bookings')
def view_bookings():
    if 'user' in session:
        user = session['user']
        role = session['user']['role']
        print(role,"rrrole")
        bookings = controller.get_user_bookings(user['username'])

        return render_template('view_bookings.html', bookings=bookings,role=role)
    else:
        return redirect(url_for('login'))  # Assuming you have a login route defined

@app.route('/refund_booking/<int:booking_id>', methods=['POST'])
def refund_booking(booking_id):
    if 'user' in session and session['user']['role'] == 'front_desk_staff':
        print("bookingidddd",booking_id)
        success = controller.refund_booking(booking_id)
        if success:
            return jsonify({'success': True, 'message': 'Booking refunded successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Error refunding booking.'}), 500
    else:
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403
@app.route('/view_notifications')
def view_notifications():
    username=session['user']['username']
    return controller.view_notifications(username)
@app.route('/booking_confirmation')
def booking_confirmation():
    return render_template('booking_confirmation.html')
@app.route('/delete-booking/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    success = controller.delete_booking_by_id(booking_id)
    if success:
        return jsonify({"success": True, "message": "Booking deleted successfully!"})
    else:
        return jsonify({"success": False, "message": "Error deleting booking."})
from flask import jsonify
@app.route('/cancel-schedule/<int:schedule_id>', methods=['DELETE'])
def cancel_schedule(schedule_id):
    return controller.cancel_schedule_and_refund(schedule_id)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    response = controller.cancel_a_booking(booking_id)
    if response["success"]:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id): 
    user = session.get('user')
    if user:
        message, category = controller.delete_movie(movie_id)
        flash(message, category)
        return redirect(url_for('dashboard'))
    else:
        flash("You are not logged in", "danger")  # 'danger' for error messages
        return redirect(url_for('login'))  # Redirect to login page or wherever appropriate

@app.route('/delete-schedule/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    screening, was_deleted  = controller.delete_screening(schedule_id)
    if was_deleted:
        # screening_info = controller.format_screening_info(screening)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Schedule not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
