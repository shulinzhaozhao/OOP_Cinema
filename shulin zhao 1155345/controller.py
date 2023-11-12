# controller.py
from flask import Flask,render_template, request,session, redirect, url_for
from movie import Movie
from cinema_hall import *
import re
from datetime import datetime,timedelta
from payment import Coupon
from userManagement import *
from screening import Screening
import random
import csv
import json
from booking import Booking,Notification
app = Flask(__name__)
app.secret_key = 'your_secret_key'

class Controller:
    def __init__(self):
        self.users = []  # Initialize the list of users in the constructor
        self.customers = [] 
        self.screenings = [] 
        self.coupons = {}
        self.movies = []
        self.seats = {}  # Dictionary to store seat informaation
        self.load_seats()
        self.write_seats_to_file()
        self.load_users_from_file()
        self.load_coupons_from_file()
        self.load_screenings_from_file()
        self.read_seats_from_file()
        
    def load_coupons_from_file(self):
        try:
            with open('coupons.txt', 'r') as file:
                for line in file:
                    try:
                        payment_id, coupon_data, discount, expiry_date, username = line.strip().split(',')
                        discount = float(discount)
                        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                        coupon_id = coupon_data.split('$')[1]
                        
                        coupon = Coupon(payment_id, coupon_id, expiry_date, discount)
                        coupon.is_used = False 
                        self.coupons[coupon_id] = {'coupon': coupon, 'username': username}
                        
                        # Assuming you have a method to get customer by username
                        user = self.get_user_by_username(username)
                        if user:
                            user.add_coupon(coupon)  # Assuming your customer class has an add_coupon method
                            print(f"Coupon {coupon_id} added to user {username}")
                        else:
                            print(f"User {username} not found. Coupon {coupon_id} not added.")
                        
                        print(f"Coupon {coupon_id} loaded successfully.")
                        
                    except ValueError as e:
                        print(f"Error processing line '{line.strip()}': {str(e)}")
                    except Exception as e:
                        print(f"Unexpected error processing line '{line.strip()}': {str(e)}")
                        
            print("Coupons loaded successfully.")
            
        except FileNotFoundError:
            print("Coupons file not found.")
        except Exception as e:
            print(f"Error loading coupons: {str(e)}")
    def load_seats(self):
        seats_data = self.read_seats_from_file()
        for seat in seats_data:
            self.seats[seat['seat_id']] = seat
    def write_seats_to_file(self):
        halls = CinemaHallRepository.get_all_cinema_halls()
        with open('seats.txt', 'w') as file:
            seat_id = 1
            for hall in halls:
                for row in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:int(hall.total_seats / 10)]:
                    for seat_number in range(1, 11):
                        status = random.randint(0, 1)
                        file.write(f'{seat_id},{hall.name},{row},{seat_number},{status},{5.00}\n')
                        seat_id += 1
    def read_seats_from_file(self):
        seats_data = []
        with open('seats.txt', 'r') as file:
            for line in file:
                if line.strip():  # This will skip empty lines
                    seat_id, hall_name, row, seat_number, status, price = line.strip().split(',')
                    seat_info = {
                        "seat_id": int(seat_id),
                        "hall_name": hall_name,
                        "row": row,
                        "seat_number": int(seat_number),
                        "status": int(status),
                        "price": float(price)
                    }
                    seats_data.append(seat_info)
        return seats_data
    def get_seat_position(self, seat_id):
        seat_id = int(seat_id)  # Convert seat_id to integer
        if seat_id in self.seats:
            seat = self.seats[seat_id]
            return f"{seat['row']}{seat['seat_number']}"
        else:
            return None  # Or handle the case where the seat ID is not found
    def load_screenings_from_file(self):
        try:
            with open('screenings.txt', 'r') as file:
                for line in file:
                    movie_id, screening_date, start_time, hall_name = line.strip().split(',')
                    movie = self.get_movie_by_id(int(movie_id))
                    if movie is not None:
                        screening_date = datetime.strptime(screening_date, '%Y-%m-%d')
                        start_time = datetime.strptime(start_time, '%H:%M')
                        screening = Screening(
                            screening_date=screening_date,
                            start_time=start_time,
                            hall=self.get_cinema_hall_by_name(hall_name),
                            movie=movie
                        )
                        self.screenings.append(screening)
            print("Screenings loaded successfully.")
        except Exception as e:
            print(f"Error loading screenings: {str(e)}")    
    def get_screenings(self):
        screenings_info = []
        for screening in self.screenings:
            info = {
                "screening_date": screening.screening_date.strftime('%Y-%m-%d'),
                "start_time": screening.start_time.strftime('%H:%M'),
                "end_time": screening.end_time.strftime('%H:%M'),
                "hall": screening.hall.name,
                "movie_title": screening.movie.title,
            }
            screenings_info.append(info)
        return screenings_info
    def load_users_from_file(self):
        try:
            with open('users.txt', 'r') as file:
                lines = file.readlines()[1:]  # Skip the header line
                for line in lines:
                    data = line.strip().split(',')
                    name, address, email, phone, username, password, role = data
                    if role == 'admin':
                        user = Admin(name, address, email, phone, username, password, role)
                    elif role == 'front_desk_staff':
                        user = FrontDeskStaff(name, address, email, phone, username, password, role)
                    elif role == 'customer':
                        user = Customer(name, address, email, phone, username, password,role)
                    else:
                        # Handle other roles or raise an exception
                        raise ValueError(f"Invalid role: {role}")

                    self.users.append(user)

            print("Users loaded successfully.")
        except Exception as e:
            print(f"Error loading users: {str(e)}")
    def read_movie_data(self):
        Movie.nextID = 1  # Reset nextID to 1 before reading movie data
        movies = []  # Clear the existing movies list

        try:
            with open("movie.txt", "r") as file:
                for line in file:
                    data = line.strip().split(",")
                    movie_id, title, description, duration_mins, language, release_date, country, genre = data
                    movie = Movie(title, description, int(duration_mins), language, datetime.strptime(release_date, '%Y-%m-%d'), country, genre)
                    movie.movie_id = int(movie_id)  # Set the movie_id to the value read from file
                    movies.append(movie)
                    Movie.nextID = max(Movie.nextID, int(movie_id) + 1)  # Ensure nextID is set correctly

        except FileNotFoundError:
            print("movie.txt not found. Please create the file with movie information.")


        return movies
    def delete_movie(self, movie_id):
        movie_id = int(movie_id)
        schedules = self.get_schedules_for_movie(movie_id)
        if schedules:
            return ("Unable to delete movie. There are screenings associated with this movie. Please delete the screenings first.", "danger")
        else:
            self.movies = [movie for movie in self.movies if movie.movie_id != movie_id]
            self.delete_movie_from_file(movie_id)
            return ("Movie deleted successfully!", "success")       
    def delete_movie_from_file(self, movie_id_to_delete):
        # Store all lines except the one with the movie to delete
        lines_to_keep = []
        
        with open("movie.txt", "r") as file:
            for line in file:
                data = line.strip().split(",")
                movie_id = int(data[0])  # First item in the line is movie_id
                if movie_id != movie_id_to_delete:
                    lines_to_keep.append(line)
                
        # Write only the lines we want to keep back to the file
        with open("movie.txt", "w") as file:
            file.writelines(lines_to_keep)

        print(f"Movie with ID {movie_id_to_delete} has been deleted from the file.")
    def refund_booking(self, booking_id: int) -> bool:
        # Logic to process the refund
        try:
            print("bbbbookingid",booking_id)
            booking = Booking.find_booking_by_id(booking_id)
            print("booking",booking)
            print(booking.status)
            print("booking.status == '0'",booking and booking.status == '0')
            if booking and booking.status == 0:

                booking.status = 2
                # Add logic to handle refund, e.g., processing payment reversal
                # Potentially, you might send a notification about the refund here
                return True
            else:
                # Booking does not exist or has already been cancelled/refunded
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    def index(self):
        movies = self.read_movie_data()
        return render_template('index.html', movies=movies)
    def search_movie(self):
        search_input = request.form['searchInput'].lower()
        movies = self.read_movie_data()  # Read movies from the data source

        # Filter movies based on search criteria
        matching_movies = [
            movie for movie in movies
            if (
                search_input in movie.title.lower() or
                search_input in movie.description.lower() or
                search_input in movie.language.lower() or
                search_input in movie.genre.lower() or
                search_input in str(movie.release_date.date())

            )
        ]
        return render_template('search_result.html', movies=matching_movies)
    def view_movie(self,movie_id):
        movies = self.read_movie_data()
        for movie in movies:
            print(movie.movie_id)
        selected_movie = next((movie for movie in movies if movie.movie_id == int(movie_id)), None)

        if selected_movie:
            print(f"Selected Movie: {selected_movie}")
            return render_template('view_movie.html', movie=selected_movie)
        else:
            return "Movie not found"
    def register_user(self, name, address, email, phone, username, password,role):
        try:
            # Validate input
            self.validate_user_input(name, address, email, phone, username, password,role)

            # Check if the username is already taken
            if self.is_username_taken(username):
                raise ValueError("Username is already taken. Please choose a different username.")

            # Create a new User and add it to the list of users
            new_user = User(name, address, email, phone, username, password,role)
            # Logic to store the new user, possibly in a database or a list
            print(f"New user registered: {new_user.info()}")
            self.users.append(new_user)
            self.customers.append(new_user)
            return new_user, None
        except ValueError as ve:
            # Log the error or display an error message
            return None, str(ve)
        except Exception as e:
            # Log the unexpected error
            return None, str(e)
    def validate_user_input(self, name, address, email, phone, username, password,role):
        # Validate each field
        if not name or not address or not email or not phone or not username or not password:
            raise ValueError("All fields must be filled out. Please provide information for all fields.")

        # Validate name format (letters and spaces only)
        if not all(char.isalpha() or char.isspace() for char in name):
            raise ValueError("Invalid name format. Please provide a name with letters and spaces only.")

        # Validate email format
        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_pattern.match(email):
            raise ValueError("Invalid email format. Please provide a valid email address.")

        # Validate phone number format
        phone_pattern = re.compile(r"^\d+$")
        if not phone_pattern.match(phone):
            raise ValueError("Invalid phone number format. Please provide a valid phone number.")
    def is_username_taken(self, username):
        # Check if the given username is already taken
        return any(user.username == username for user in self.users)    
    def login_user(self, username, password):
        # Find the user with the given username
        user = next((user for user in self.users if user.username == username), None)
        if user is not None:
            # Verify the password regardless of user type
            if user.verify_password(password):
                print(f"User {username} logged in successfully.")
                session['user'] = {
                    'username': user.username,
                    'role': user.role,
                    'name': user.name
                }
                return user
            else:
                print(f"Login failed for user {username}. Incorrect password.")
                return None

        # If the user is not found, return None
        print(f"User {username} not found.")
        return None
    def is_admin_user(self,user):
        if user.role == "admin":
            return True
    def is_front_desk_user(self,user):
        if user.role == "front_desk_staff":
            return True
    def is_customer_user(self,user):
        if user.role == "customer":
            return True  
    def admin_dashboard(self):
        print('user' in session,"'user' in session")
        print("session['user']['role'].lower() == 'admin'",session['user']['role'].lower() == 'admin')
        if 'user' in session and session['user']['role'].lower() == 'admin': 
            movies = self.read_movie_data()
            
            return render_template('admin_dashboard.html', movies=movies)
        return redirect(url_for('login'))
    def front_desk_dashboard(self):
        if 'user' in session and session['user']['role'].lower() == 'front_desk_staff':
            movies = self.read_movie_data()
            return render_template('front_desk_dashboard.html', movies=movies)
        return redirect(url_for('login'))   
    def customer_dashboard(self):
        if 'user' in session and session['user']['role'].lower() == 'customer':
            movies = self.read_movie_data()
            return render_template('customer_dashboard.html', movies=movies)
        return redirect(url_for('login'))
    def get_user_bookings(self, username):
        print("username", username)
        user_bookings = []
        print("Booking.get_bookings()",Booking.get_bookings())
        for booking in Booking.get_bookings():
            print("booking.customer",booking.customer)
            if booking.customer:
                print("Booking customer:", booking.customer)
                if booking.customer == username:
                    user_bookings.append(booking)
        print("User bookings:", user_bookings)
        return user_bookings  
    def view_schedules(self, movie_id):
        movie = self.get_movie_by_id(movie_id)  
        
        if movie:
            # Inside the view_schedules method
            schedules = self.get_schedules_for_movie(int(movie_id))
            now = datetime.now()
            current_date = now.date()
            current_time = now.time()

            return render_template('view_schedules.html', current_date=current_date, current_time=current_time, schedules=schedules, movie=movie)

        else:
            return "Movie not found"
    def cancel_view_schedules(self, movie_id):
        movie = self.get_movie_by_id(movie_id)  
        
        if movie:
            # Inside the view_schedules method
            schedules = self.get_schedules_for_movie(int(movie_id))
            
            return render_template('cancel_view_schedules.html', movie=movie, schedules=schedules)
        else:
            return "Movie not found"

    def delete_screening(self, schedule_id):
        print("Attempting to delete screening with ID:", schedule_id)
        reserved_seats = {}
        deleted_schedule_seats = []
        matching_bookings = []
        seat_id_mapping = {str(seat['seat_id']): seat['row'] + str(seat['seat_number']) for seat in self.read_seats_from_file()}
        inverted_seat_id_mapping = {v: k for k, v in seat_id_mapping.items()}
        with open('reservations.txt', 'r') as file:
            for line in file:
                file_schedule_id, numeric_seat_id = line.strip().split(',')
                seat_id = seat_id_mapping.get(numeric_seat_id, numeric_seat_id)
                reserved_seats.setdefault(file_schedule_id, []).append(seat_id)
        print(reserved_seats, "reserved_seats")
        if str(schedule_id) in reserved_seats:
            matching_bookings = Booking.find_movie_by_seats(reserved_seats[str(schedule_id)])
            print("matching_bookings", matching_bookings)
            print("reserved_seats[str(schedule_id)]", reserved_seats[str(schedule_id)])
        if not matching_bookings:
            # If no matching bookings, proceed to delete the screening
            screening = self.remove_screening(schedule_id)
            return screening, True
        for booking in matching_bookings:
            booking.status = 2
            for seat_id in reserved_seats[str(schedule_id)]:
                print(f"Refund issued for seat {seat_id} of schedule {schedule_id}.")
        # Remove the reservations for the deleted screening
        with open('reservations.txt', 'w') as file:
            for sched_id, seat_ids in reserved_seats.items():
                for seat_id in seat_ids:
                    numeric_seat_id = inverted_seat_id_mapping.get(seat_id, seat_id)
                    file.write(f"{sched_id},{numeric_seat_id}\n")
        # Delete the screening after handling bookings and file operations
        return self.remove_screening(schedule_id)

    def remove_screening(self, schedule_id):
        screening = next((s for s in self.screenings if s.screening_id == schedule_id), None)
        if screening:
            print("Screening found. Deleting...")
            self.screenings.remove(screening)
            try:
                self.save_screenings()
                print("Screening deleted successfully.")
                return screening, True
            except Exception as e:
                print("Failed to save screenings:", str(e))
                return None, False
        else:
            print("Screening not found.")
            return None, False
    def format_screening_info(self, screening):
        print(screening,"screening.py")
        formatted_date = screening.screening_date.strftime('%Y-%m-%d')
        formatted_time = screening.start_time.strftime('%H:%M')
        return f"Screening on {formatted_date} at {formatted_time} in {screening.hall.name} for movie {screening.movie.title}"

    def save_screenings(self):
        with open('screenings.txt', 'w') as f:
            for screening in self.screenings:
                f.write(f"{screening.movie.movie_id},{screening.screening_date:%Y-%m-%d},{screening.start_time:%H:%M},{screening.hall.name}\n")

    def book_view_schedules(self, movie_id):
        movie = self.get_movie_by_id(movie_id)  
        if movie:
            # Inside the view_schedules method
            schedules = self.get_schedules_for_movie(int(movie_id)) 
            now = datetime.now()
            current_date = now.date()
            current_time = now.time()

            return render_template('book_view_schedules.html', current_date=current_date, current_time=current_time, schedules=schedules, movie=movie)
        else:
            return "Movie not found"

    def add_screening(self, movie_id, screening_date, start_time, hall_name):
        movie = self.get_movie_by_id(movie_id)
        hall = self.get_cinema_hall_by_name(hall_name)
        if not movie or not hall:
            return False

        # Load and parse existing screenings
        with open('screenings.txt', 'r') as file:
            existing_screenings = file.readlines()

        for line in existing_screenings:
            existing_id, existing_date, existing_time, existing_hall = line.strip().split(',')
            existing_date = datetime.strptime(existing_date, '%Y-%m-%d')
            existing_time = datetime.strptime(existing_time, '%H:%M')

            # Calculate the end time of the existing screening
            existing_movie = self.get_movie_by_id(int(existing_id))
            if existing_movie:
                existing_end_time = existing_time + timedelta(minutes=existing_movie.duration_mins)

                # Check for overlapping screenings in the same hall
                if (hall_name == existing_hall and
                    screening_date.date() == existing_date.date() and
                    not (start_time >= existing_end_time or
                        (start_time + timedelta(minutes=movie.duration_mins)) <= existing_time)):
                    return False  # Overlap detected

        # If no overlaps, proceed to add the screening
        screening = Screening(screening_date, start_time, hall, movie)
        self.screenings.append(screening)
        self.save_screening_to_file(screening)

        return True


    def save_screening_to_file(self, screening):
        with open('screenings.txt', 'a') as file:
            line = f"{screening.movie.movie_id},{screening.screening_date.strftime('%Y-%m-%d')},{screening.start_time.strftime('%H:%M')},{screening.hall.name}\n"
            file.write(line)
    def get_cinema_hall_by_name(self, hall_name):
        cinema_halls = CinemaHallRepository.get_all_cinema_halls()
        
        for hall in cinema_halls:
            if hall.name.lower() == hall_name.lower():
                return hall
                
        return None  # Return None if the hall was not found   
    def get_movie_by_id(self,movie_id):
        movies = self.read_movie_data()
        selected_movie = next((movie for movie in movies if movie.movie_id == int(movie_id)), None)

        if selected_movie:
            print(f"Selected Movie: {selected_movie}")
            return selected_movie
        else:
            return None
    def get_hall_for_schedule(self, schedule_id):
        for screening in self.screenings:
            if screening.screening_id == schedule_id:
                return screening.hall
        return None  # Return None if no matching schedule is found
    def get_all_movies(self):
        movies = self.read_movie_data()
        return movies
    def get_all_cinema_halls(self):
        halls=CinemaHallRepository.get_all_cinema_halls()
        return halls
    def get_schedules_for_movie(self, movie_id):
        schedules = []
        for screening in self.screenings:  # Assuming self.screenings is a list of all screening objects
            if screening.movie.movie_id == movie_id:
                schedules.append({
                    'id': screening.screening_id,  # Use screening_id here
                    'screening_date': screening.screening_date,
                    'start_time': screening.start_time,
                    'end_time': screening.end_time,  # Ensure you have this attribute in your Screening class
                    'hall_name': screening.hall.name,
                })

        return schedules
    def add_movie(self,title, description, duration_mins, language, release_date, country, genre):
        # Check if a movie with the same title already exists
        existing_movies = self.read_movie_data()
        for movie in existing_movies:
            if movie.title.lower() == title.lower():  # Case-insensitive comparison
                print("A movie with this title already exists.")
                return False
        try:
            new_movie = Movie(title, description, int(duration_mins), language, release_date, country, genre)
            self.save_movie_to_file(new_movie)
            return True
        except Exception as e:
            print("Error adding movie:", str(e))  # Log the error
            return False
    def save_movie_to_file(self, customer,new_movie):
        with open('movie.txt', 'a') as file:
            line = f"{new_movie.movie_id},{new_movie.title},{new_movie.description},{new_movie.duration_mins},{new_movie.language},{new_movie.release_date.strftime('%Y-%m-%d')},{new_movie.country},{new_movie.genre}\n"
            file.write(line)
    def book(self,schedule_id,selected_seats):
        for seat in selected_seats:
            self.reserve_seat(schedule_id, seat)

        return schedule_id, selected_seats

    def get_available_seats(self, schedule_id):
        hall = self.get_hall_for_schedule(schedule_id)
        if not hall:
            return [], []  # Return empty lists if no matching hall is found
        reservations = self.read_reservations_from_file()  # Read all reservations from file
        reserved_seat_ids = [reservation['seat_id'] for reservation in reservations if reservation['schedule_id'] == schedule_id]  # Find all reserved seat IDs for the given schedule
        all_seats = self.read_seats_from_file()  # Read all seats from file
        all_seats_in_hall = []
        available_seats = []
        unavailable_seats = []
        for seat in all_seats:
            if seat["hall_name"] == hall.name:
                all_seats_in_hall.append(seat)
        for seat in all_seats:
            if seat["hall_name"] == hall.name:
                if seat["seat_id"] not in reserved_seat_ids:
                    available_seats.append(seat)
                else:
                    unavailable_seats.append(seat)
        return available_seats, unavailable_seats,all_seats_in_hall
    def get_user_by_username(self, username):
        for user in self.users:
            print("user",user)
            print("self.users",self.users)
            if user.username == username and isinstance(user, User):
                print("uuuuuuser",user)
                return user
        return None
    def get_booking_details_data(self, session, booked_seats, schedule_id):
        data = {}  # To store the necessary data for booking details
        # Convert seat IDs to seat positions
        booked_seat_ids = booked_seats.split(",")
        booked_seat_positions = [self.get_seat_position(seat_id) for seat_id in booked_seat_ids]
        data['booked_seat_positions'] = booked_seat_positions

        # Get screening detail
        screeningDetail = self.get_screening_detail(schedule_id)
        print("screeningDetail",screeningDetail)
        data['screeningDetail'] = screeningDetail
        
        # Calculate order total
        orderTotal = self.calculate_order_total(booked_seat_ids)
        data['orderTotal'] = orderTotal

        username = session.get('user', {}).get('username')
        user = self.get_user_by_username(username) if username else None
        if user:
            print(f"{user.username} exists with coupons: {user.coupons}")
            data['available_coupons'] = user.get_coupons()
        else:
            data['available_coupons'] = []
            print("Customer not found or not logged in.")
        return data
    def reserve_seat(self, schedule_id, seat_id):
        with open('reservations.txt', 'a') as file:
            file.write(f'{schedule_id},{seat_id}\n')
    def read_reservations_from_file(self):
        reservations_data = []
        with open('reservations.txt', 'r') as file:
            for line in file:
                if line.strip():  # This will skip empty lines
                    schedule_id, seat_id = line.strip().split(',')
                    reservation_info = {
                        "schedule_id": int(schedule_id),
                        "seat_id": int(seat_id)
                    }
                    reservations_data.append(reservation_info)
                    
        return reservations_data
    def apply_discount(self, customer, coupon_code: str, order_total: float):
        if coupon_code not in customer.coupons:
            return {"status": "error", "message": "Coupon not found"}

        coupon = customer.coupons.get(coupon_code)
        if not coupon:
            return {"status": "error", "message": "Coupon not found"}

        if coupon.is_used:
            return {"status": "error", "message": "This coupon has already been used"}
        coupon.is_used = True
        # Remove coupon from the customer's available coupons (optional but recommended)
        customer.remove_coupon(coupon_code)
        discount = coupon.calc_discount()

        if discount == 0:
            return {"status": "error", "message": "Coupon is expired or not valid"}

        if discount > order_total:
            discount = order_total

        return {"status": "success", "discount": discount}
    def create_booking(self, form_data):
        payment_method = form_data.get('payment_method')
        seats = form_data.get('seats')
        order_total = form_data.get('final_total')
        movie_title = form_data.get('movie_title')
        start_time=form_data.get('start_time')
        end_time=form_data.get('end_time')
        screening_date=form_data.get('screening_date')
        number_of_seats=len(seats)
        screening_detail = {
            'movie_title': form_data.get('movie_title'),
            'start_time': form_data.get('start_time'),
            'end_time': form_data.get('end_time'),
            'screening_date': form_data.get('screening_date'),
        }
        print("screening_detail",screening_detail)
        if payment_method == 'credit_card':
            payment_details = {
                'credit_card_number': form_data.get('credit_card_number'),
                'expiry_date': form_data.get('expiry_date'),
                'name_on_card': form_data.get('name_on_card_credit'),
                'card_type': form_data.get('card_type'),
            }
        elif payment_method == 'debit_card':
            payment_details = {
                'debit_card_number': form_data.get('debit_card_number'),
                'expiry_date_debit': form_data.get('expiry_date_debit'),
                'name_on_card': form_data.get('name_on_card_debit'),
                'bank_name': form_data.get('bank_name'),
            }

        user = session['user']['username']
        booking = Booking(
            user, number_of_seats, datetime.now(), 1, screening_detail, seats, order_total,
            payment_method
        )
        
        role = session['user']['role'] 
        print("rrrrrole",role)
        order_total = float(order_total)
        
        notification_message = (
            f"Dear {user},\n"
            f"Your booking for {movie_title} from {start_time} to {end_time} on {screening_date} is confirmed!\n"
            f"Number of Seats: {seats}\n"
            f"Total Amount: ${order_total:.2f}\n"
            f"Thank you for choosing us!")

        notification = Notification(notification_message)
        customer_obj = self.get_user_by_username(user)  
        customer_obj.add_notification(notification)
        return booking, notification
    def calculate_order_total(self, booked_seats_list):
        total = 0
        for seat_id in booked_seats_list:
            if int(seat_id) in self.seats:
                total += self.seats[int(seat_id)]['price']
        return total
    def get_available_coupons(self, customer):
        if customer and isinstance(customer, Customer):
            return customer.get_coupons()
        else:
            return []
    def get_screening_detail(self, schedule_id):
        for screening in self.screenings:
            print("schedule_iddddd",schedule_id)
            
            if screening.screening_id == schedule_id:  # Check if the screening_id matches the provided schedule_id
                return {
                    "movie_title": screening.movie.title,
                    "screening_date": screening.screening_date.strftime('%Y-%m-%d'),
                    "start_time": screening.start_time.strftime('%H:%M:%S'),
                    "end_time": screening.end_time.strftime('%H:%M:%S'),
                    "hall_name": screening.hall.name
                }
        return None
    def view_notifications(self, username):
        # Get the customer object using the username
        customer_obj = self.get_user_by_username(username)
        
        if customer_obj is None:
            return "Error: User not found"
        
        # Get all notifications for the user
        all_notifications = customer_obj.get_notifications()
        
        # Filter notifications that include the username
        filtered_notifications = [notif for notif in all_notifications if username in notif.content]
        return render_template('view_notifications.html', notifications=filtered_notifications)

    def cancel_a_booking(self, booking_id):
        # Find the booking using the booking_id from the list of bookings
        booking = next((b for b in Booking.bookings if b.booking_id == booking_id), None)
        if not booking:
            return {"success": False, "message": "Booking not found."}        
        # Use the cancel_booking method from the Booking class to change the status to 0 (cancelled)
        booking.cancel_booking()        
        # Generate a cancellation notification
        user = session['user']['username']
        movie_title = booking.screeningDetail.get('movie_title', 'Unknown Movie')
        screening_date = booking.screeningDetail.get('screening_date', 'Unknown Date')
        start_time = booking.screeningDetail.get('start_time', 'Unknown Time')
        end_time = booking.screeningDetail.get('end_time', 'Unknown Time')
        
        notification_message = (
            f"Dear {user},\n"
            f"Your booking for {movie_title} on {screening_date} from {start_time} to {end_time}has been cancelled. "
            "We apologize for any inconvenience.\n"
        )

        notification = Notification(notification_message)
        customer_obj = self.get_user_by_username(user)  
        customer_obj.add_notification(notification)
        return {"success": True, "message": "Booking cancelled successfully! Notification has been sent."}

    def logout(self):
        session.pop('user', None)  # This line removes the username from the session
        return redirect(url_for('main_index'))  # Redirect the user to the login page