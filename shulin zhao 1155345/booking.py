from datetime import datetime
from typing import List, Dict

class Booking:
    nextID = 1  # Initialize nextID to 1
    bookings = []  # List to store all bookings

    def __init__(self, customer, numberOfSeats: int, createdOn: datetime, status: int, 
                  screeningDetail, seats: List, orderTotal: float, payment_method: str):
        self.booking_id = Booking.nextID
        self.customer = customer  # This assumes a separate Customer class is defined.
        self.numberOfSeats = numberOfSeats
        self.createdOn = createdOn
        self.status = status
        
        self.screeningDetail = screeningDetail
        self.seats = seats  # List of CinemaHallSeat objects
        self.orderTotal = orderTotal
        self.paymentDetail = self.process_payment(payment_method)
        Booking.nextID += 1
        Booking.bookings.append(self)  # Add the booking to the list of bookings

    def process_payment(self, payment_method):
        # Process the payment based on the payment_method and additional kwargs
        # You can add the payment processing logic here
        # For simplicity, let's just return the kwargs as payment details
        return {
            'payment_method': payment_method,
        
        }

    def get_notification(self):
        return self.notification
 
    @classmethod
    def find_movie_by_seats(cls, seats: List[str]):
        print("Searching for seats:", seats)  # Debugging line to see what seats we're searching for
        matching_bookings = []
        for booking in cls.bookings:
            print("Current booking seats:", booking.seats)  # See the seats in the current booking
            if any(seat in booking.seats for seat in seats):
                matching_bookings.append(booking)
                print(f"Found matching booking: {booking.booking_id} with seats {booking.seats}")  # This line will confirm a match has been found
        return matching_bookings

    @classmethod
    def get_bookings(cls):
        return cls.bookings

    def cancel_booking(self):
        if self.status == 1:  # If the status is booked
            self.status = 0  # Change the status to cancelled
    @classmethod
    def find_booking_by_id(cls, booking_id: int) :
        for booking in cls.bookings:
            if booking.booking_id == booking_id:
                return booking
        return None
        
class Notification:
    nextID = 1
    notifications = []

    def __init__(self, content):
        self.notification_id = Notification.nextID
        self.created_on = datetime.now()
        self.content = content
        Notification.nextID += 1
        Notification.notifications.append(self)

    def __str__(self):
        return f"Notification ID: {self.notification_id}\nCreated On: {self.created_on.strftime('%Y-%m-%d %H:%M:%S')}\nContent: {self.content}"
