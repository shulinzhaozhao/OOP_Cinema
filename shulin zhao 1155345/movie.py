from datetime import datetime
from typing import List
from cinema_hall import CinemaHall
from screening import Screening

class Movie:
    nextID = 1  # Initialize nextID to 1

    def __init__(self, title: str, description: str, duration_mins: int, language: str,
                 release_date: datetime, country: str, genre: str):
        self.movie_id = Movie.nextID  # Assign a unique ID to the movie
        self.title = title
        self.description = description
        self.duration_mins = duration_mins
        self.language = language
        self.release_date = release_date
        self.country = country
        self.genre = genre
        self.screening_list: List[Screening] = []
        Movie.nextID += 1

    def add_screening(self, screening_date: datetime, start_time: datetime, hall: CinemaHall):
        screening = Screening(screening_date, start_time, hall, self)
        self.screening_list.append(screening)
        return screening

    def get_screenings(self) -> List[Screening]:
        return self.screening_list

    def __str__(self):
        return f"Movie ID: {self.movie_id}, Title: {self.title}, Description: {self.description}, " \
               f"Duration: {self.duration_mins} mins, Language: {self.language}, " \
               f"Release Date: {self.release_date}, Country: {self.country}, Genre: {self.genre}"
