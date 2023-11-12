from typing import List
from abc import ABC, abstractmethod
import bcrypt

class Guest():
    def register(self, name, address, email, phone) -> 'User':
        new_user = User(name, address, email, phone)
        # Logic to store the new user, possibly in a database or a list
        print(f"New user registered: {new_user.info()}")
        return new_user

class Person(ABC):
    def __init__(self, name: str, address: str, email: str, phone: str):
        super().__init__()  # Call the init method of the parent class if needed
        self._name = name
        self._address = address
        self._email = email
        self._phone = phone
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def address(self) -> str:
        return self._address
    
    @address.setter
    def address(self, value):
        self._address = value
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value):
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone
    
    @phone.setter
    def phone(self, value):
        self._phone = value

    def info(self):
        return f"Name: {self.name}, Address: {self.address}, Email: {self.email}, Phone: {self.phone}"

class User(Person):
    def __init__(self, name: str, address: str, email: str, phone: str, username: str, password: str, role: str):
        super().__init__(name, address, email, phone)  # Call the init method of the parent class
        self._username = username
        self._password = password
        self._role = role
        self.coupons = {}
    def get_coupons(self):
        return list(self.coupons.keys())
    def add_coupon(self, coupon):
        self.coupons[coupon.coupon_id] = coupon  # Use coupon_id instead of code
        
    def remove_coupon(self, coupon_code: str):
        if coupon_code in self.coupons:
            del self.coupons[coupon_code]

    @property
    def role(self) -> str:
        return self._role

    @role.setter
    def role(self, value: str):
        self._role = value

    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, value):
        self._username = value
    
    @property
    def password(self) -> str:
        return self._password

    def verify_password(self, input_password: str) -> bool:
        return input_password == self._password

    def set_password(self, new_password: str):
        # Method for setting a new password
        self._password = new_password

    def login(self, password: str) -> bool:
        if self.verify_password(password):
            # Successful login logic
            print(f"User {self.username} logged in successfully.")
            return True
        else:
            # Failed login logic
            print(f"Login failed for user {self.username}. Incorrect password.")
            return False

    def logout(self) -> bool:
        # Implement logout logic (return True if successful, False otherwise)
        print(f"User {self.username} logged out.")
        return True
 
    def info(self):
        person_info = super().info()
        return f"{person_info}, Username: {self.username}, Hashed Password: {self.password}"

class Admin(User):
    def add_movie(self) -> bool:
        # Implement add movie logic
        print("Admin added a new movie.")
        return True

    def add_screening(self) -> bool:
        # Implement add screening logic
        print("Admin added a new screening.")
        return True

    def cancel_movie(self) -> bool:
        # Implement cancel movie logic
        print("Admin canceled a movie.")
        return True

    def cancel_screening(self) -> bool:
        # Implement cancel screening logic
        print("Admin canceled a screening.")
        return True

class FrontDeskStaff(User):
    def __init__(self, name: str, address: str, email: str, phone: str, username: str, password: str, role: str):
        super().__init__(name, address, email, phone, username, password, role)
        self._notifications = []  # List to store notifications
    def make_booking(self):
        # logic for making a booking
        return True
    def cancel_booking(self):
        # logic for canceling a booking
        return True

    def add_notification(self, notification: str):
        self._notifications.append(notification)
        print(f"Notification added to Front Desk Staff {self.username}")

    def get_notifications(self):
        return self._notifications
    
    def view_notifications(self):
        for notification in self._notifications:
            print(notification)
    
class Customer(User):
    def __init__(self, name: str, address: str, email: str, phone: str, username: str, password: str, role: str):
        super().__init__(name, address, email, phone, username, password, role)
        self._notifications = []  # List to store notifications
        self.username = username
    def cancel_booking(self):
        # logic for canceling a booking
        return True
    def get_booking_list(self):
        # Return the booking list
        return self._booking_list
        
    def add_notification(self, notification):
        self._notifications.append(notification)

    def get_notifications(self):
        return self._notifications
    
    def info(self):
        user_info = super().info()
        booking_info = ", ".join([str(booking) for booking in self._booking_list])
        notification_info = ", ".join([str(notification) for notification in self._notification_list])
        return f"{user_info}, Bookings: {booking_info}, Notifications: {notification_info}"
