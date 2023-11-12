import pytest
from flask import session
from booking import Booking, Notification
from cinema_hall import CinemaHallSeat, CinemaHall, CinemaHallRepository
from screening import Screening
from movie import Movie
from datetime import datetime, timedelta
from payment import CreditCard, Cash, DebitCard, Coupon
from userManagement import *
from controller import Controller
from unittest.mock import Mock


def test_create_booking():
    customer = "John Doe"
    numberOfSeats = 3
    createdOn = datetime.now()
    status = 1  # Assuming 1 means 'booked'
    screeningDetail = "Screening Detail"  # Replace with actual screening detail object
    seats = ["A1", "A2", "A3"]  # Replace with actual CinemaHallSeat objects if necessary
    orderTotal = 30.0
    payment_method = "credit_card"
    booking = Booking(customer, numberOfSeats, createdOn, status, screeningDetail, seats, orderTotal, payment_method)
    
    assert booking.booking_id == 1
    assert booking.customer == customer
    assert booking.numberOfSeats == numberOfSeats
    assert booking.status == status
    assert booking.paymentDetail['payment_method'] == payment_method
    assert booking in Booking.get_bookings()

def test_cancel_booking():
    booking = Booking("Jane Doe", 2, datetime.now(), 1, "Screening Detail", ["B1", "B2"], 20.0, "debit_card")
    booking.cancel_booking()
    
    assert booking.status == 0

def test_create_notification():
    content = "This is a test notification."
    notification = Notification(content)
    
    assert notification.notification_id == 1
    assert notification.content == content
    assert notification in Notification.notifications



def test_cinema_hall_seat():
    seat = CinemaHallSeat(1, 'A', 'Regular', False, 10.0)
    assert str(seat) == "Seat 1 (Column: A, Type: Regular, Reserved: False, Price: 10.0)"

def test_cinema_hall():
    hall = CinemaHall("Premier Hall", 120)
    assert str(hall) == "Cinema Hall: Premier Hall, Total Seats: 120"
    assert len(hall.list_of_seats) == 120
    assert isinstance(hall.list_of_seats[0], CinemaHallSeat)

def test_cinema_hall_repository():
    halls = CinemaHallRepository.get_all_cinema_halls()
    assert len(halls) == 4
    assert all(isinstance(hall, CinemaHall) for hall in halls)
    assert any(hall.name == "Premier Hall" for hall in halls)


def test_movie():
    movie = Movie("Inception", "A mind-bending thriller", 148, "English", 
                  datetime(2010, 7, 16), "USA", "Sci-Fi")
    assert str(movie) == ("Movie ID: 1, Title: Inception, Description: A mind-bending thriller, "
                          "Duration: 148 mins, Language: English, Release Date: 2010-07-16 00:00:00, "
                          "Country: USA, Genre: Sci-Fi")

def test_add_screening():
    movie = Movie("Inception", "A mind-bending thriller", 148, "English", 
                  datetime(2010, 7, 16), "USA", "Sci-Fi")
    hall = CinemaHall("Main Hall", 150)
    screening_date = datetime(2023, 11, 15)
    start_time = datetime(2023, 11, 15, 20, 0)

    screening = movie.add_screening(screening_date, start_time, hall)
    assert screening.movie == movie
    assert screening.hall == hall
    assert screening.screening_date == screening_date
    assert screening.start_time == start_time

def test_get_screenings():
    movie = Movie("Inception", "A mind-bending thriller", 148, "English", 
                  datetime(2010, 7, 16), "USA", "Sci-Fi")
    hall = CinemaHall("Main Hall", 150)
    screening_date = datetime(2023, 11, 15)
    start_time = datetime(2023, 11, 15, 20, 0)

    screening = movie.add_screening(screening_date, start_time, hall)
    screenings = movie.get_screenings()
    assert len(screenings) == 1
    assert screenings[0] == screening


def test_credit_card_payment():
    credit_card_payment = CreditCard(100, "1", "1234567890123456", "Visa", "12/23", "John Doe")
    assert credit_card_payment.calc_final_payment() == 100  # Assuming no discount for credit card
    assert credit_card_payment.payment_id == "1"

def test_cash_payment():
    cash_payment = Cash(100, "2")
    assert cash_payment.calc_final_payment() == 100  # Assuming no discount for cash
    assert cash_payment.payment_id == "2"

def test_debit_card_payment():
    debit_card_payment = DebitCard(100, "3", "9876543210123456", "Bank of Test", "Jane Doe")
    assert debit_card_payment.calc_final_payment() == 100  # Assuming no discount for debit card
    assert debit_card_payment.payment_id == "3"

def test_coupon_expired():
    expired_coupon = Coupon("4", "C1", datetime.now() - timedelta(days=1), 10)
    assert expired_coupon.calc_discount() == 0

def test_coupon_valid():
    valid_coupon = Coupon("5", "C2", datetime.now() + timedelta(days=1), 10)
    assert valid_coupon.calc_discount() == 10

def test_user_creation():
    user = User("John Doe", "123 Street", "john@example.com", "1234567890", "johndoe", "password123", "customer")
    assert user.name == "John Doe"
    assert user.address == "123 Street"
    assert user.email == "john@example.com"
    assert user.phone == "1234567890"
    assert user.username == "johndoe"
    assert user.password == "password123"
    assert user.role == "customer"

def test_user_login():
    user = User("John Doe", "123 Street", "john@example.com", "1234567890", "johndoe", "password123", "customer")
    assert user.login("password123") == True
    assert user.login("wrongpassword") == False

def test_user_logout():
    user = User("John Doe", "123 Street", "john@example.com", "1234567890", "johndoe", "password123", "customer")
    assert user.logout() == True
def test_admin_functions():
    admin = Admin("Admin", "123 Street", "admin@example.com", "1234567890", "admin", "adminpassword", "admin")
    assert admin.add_movie() == True
    assert admin.add_screening() == True
    assert admin.cancel_movie() == True
    assert admin.cancel_screening() == True
def test_front_desk_staff_functions():
    staff = FrontDeskStaff("Staff", "123 Street", "staff@example.com", "1234567890", "staff", "staffpassword", "staff")
    assert staff.make_booking() == True
    assert staff.cancel_booking() == True
    staff.add_notification("New booking")
    assert "New booking" in staff.get_notifications()
def test_customer_functions():
    customer = Customer("Customer", "123 Street", "customer@example.com", "1234567890", "customer", "customerpassword", "customer")
    assert customer.cancel_booking() == True
    customer.add_notification("Booking canceled")
    assert "Booking canceled" in customer.get_notifications()

def setup_controller():
    controller = Controller()
    # Assuming that the 'seats' dictionary should be in the format {seat_id: {'row': 'A', 'seat_number': 1}}
    controller.seats = {
        1: {'row': 'A', 'seat_number': 1},
        2: {'row': 'B', 'seat_number': 2},
        # ... other seats ...
    }
    return controller

def test_get_seat_position():
    controller = setup_controller()
    # Test existing seat
    result = controller.get_seat_position(1)
    assert result == "A1", f"Expected A1, but got {result}"

    # Test non-existing seat
    result = controller.get_seat_position(999)
    assert result is None, f"Expected None, but got {result}"

    # Test invalid seat_id (not an integer)
    with pytest.raises(ValueError):
        controller.get_seat_position("invalid_seat_id")
def test_get_screenings():
    controller = setup_controller()
    screenings = controller.get_screenings()
    assert any(s['movie_title'] == 'Inception' for s in screenings), "Expected a screening of Inception"

@pytest.fixture
def controller():
    ctrl = Controller()
    # Setup your controller instance here if needed
    return ctrl

def test_delete_movie(controller):
    # Add a movie to delete
    movie = Movie("Test Movie", "Some description", 120, "English", "2020-01-01", "USA", "Action")
    controller.movies.append(movie)
    movie_id_to_delete = movie.movie_id  # Assuming your Movie class generates an ID
    
    # Test deleting the movie
    message, status = controller.delete_movie(movie_id_to_delete)
    assert status == "success"
    assert len(controller.movies) == 0, "Expected the movie to be deleted"

@pytest.fixture
def mock_booking():
    # Create mock values for each parameter needed by the Booking class
    mock_customer = Mock()  # Assuming you have a Customer class
    mock_screening_detail = Mock()  # Assuming you have a screeningDetail structure
    mock_seats = Mock()  # Assuming you have a list or structure of seats

    booking = Booking(
        customer=mock_customer,
        numberOfSeats=2,
        createdOn=datetime.now(),
        status=1,  # assuming 1 is for 'booked' status
        screeningDetail=mock_screening_detail,
        seats=[mock_seats],
        orderTotal=20.0,
        payment_method='Credit Card'
    )
    return booking


