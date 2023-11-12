from datetime import datetime
from abc import ABC, abstractmethod
class Payment(ABC):
    def __init__(self, amount, payment_id):
        self.amount = amount
        self.created_on = datetime.now()
        self.payment_id = payment_id

    def calc_final_payment(self):
        return self.amount - self.calc_discount()

class CreditCard(Payment):
    def __init__(self, amount, payment_id, credit_card_number, card_type, expiry_date, name_on_card):
        super().__init__(amount, payment_id)
        self.credit_card_number = credit_card_number
        self.card_type = card_type
        self.expiry_date = expiry_date
        self.name_on_card = name_on_card
        

    def calc_discount(self):
        # Implement the logic for calculating discount for credit card payments
        return 0
class Cash(Payment):
    def calc_discount(self):
        # Implement the logic for calculating discount for cash payments
        return 0
class DebitCard(Payment):
    def __init__(self, amount, payment_id, card_number, bank_name, name_on_card):
        super().__init__(amount, payment_id)
        self.card_number = card_number
        self.bank_name = bank_name
        self.name_on_card = name_on_card

    def calc_discount(self):
        # Implement the logic for calculating discount for debit card payments
        return 0


class Coupon(Payment):
    def __init__(self, payment_id, coupon_id, expiry_date, discount):
        super().__init__(0, payment_id)  # Amount set to 0 as it's not used for coupons
        self.coupon_id = coupon_id
        self.is_used = False
        # Make sure expiry_date is a datetime object
        if isinstance(expiry_date, str):
            self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        else:
            self.expiry_date = expiry_date
        self.discount = float(discount)  # Ensure discount is a float

    def calc_discount(self):
        # Check if the coupon is expired
        if datetime.now() > self.expiry_date:
            return 0
        return self.discount




