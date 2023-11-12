
class CinemaHallSeat:
    def __init__(self, seat_number: int, seat_column: int, seat_type: int, is_reserved: bool, seat_price: float):
        self.seat_number = seat_number
        self.seat_column = seat_column
        self.seat_type = seat_type
        self.is_reserved = is_reserved
        self.seat_price = seat_price

    def __str__(self):
        return f"Seat {self.seat_number} (Column: {self.seat_column}, Type: {self.seat_type}, " \
               f"Reserved: {self.is_reserved}, Price: {self.seat_price})"


class CinemaHall:
    def __init__(self, name: str, total_seats: int):
        self.name = name
        self.total_seats = total_seats
        self.list_of_seats: List[CinemaHallSeat] = [
            CinemaHallSeat(seat_number=i, seat_column=1, seat_type=1, is_reserved=False, seat_price=0.0)
            for i in range(1, total_seats + 1)
        ]

    def __str__(self):
        return f"Cinema Hall: {self.name}, Total Seats: {self.total_seats}"
class CinemaHallRepository:
    @staticmethod
    def get_all_cinema_halls():
        # Define cinema halls with their names and seats
        halls = [
            CinemaHall(name="Premier Hall", total_seats=120),
            CinemaHall(name="Royal Suite", total_seats=90),
            CinemaHall(name="Economy Class", total_seats=110),
            CinemaHall(name="Deluxe Room", total_seats=80),
        ]
        return halls


