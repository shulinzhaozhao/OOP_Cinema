from datetime import datetime, timedelta
from cinema_hall import CinemaHall

class Screening:
    nextID = 1  # Initialize nextID to 1
    def __init__(self, screening_date: datetime, start_time: datetime, hall: CinemaHall, movie: 'Movie'):
        from movie import Movie
        self.screening_id = Screening.nextID  # Assign a unique ID to the movie
        self.screening_date = screening_date
        self.start_time = start_time
        self.end_time = start_time + timedelta(minutes=movie.duration_mins)
        self.hall = hall
        self.movie = movie
        Screening.nextID += 1

    def __str__(self):
        return f"Screening on {self.screening_date} at {self.start_time} in {self.hall.name}"
