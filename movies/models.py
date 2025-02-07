from django.db import models
from django.contrib.auth.models import User 
from django.utils.timezone import now
from urllib.parse import urlparse, parse_qs  # ✅ Import required modules
import re


class Movie(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensure unique movie names
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)  # Optional release date
    image = models.ImageField(upload_to="movies/", blank=True, null=True)  # Optional image
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    cast = models.TextField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)  # YouTube trailer URL

    
    
    def get_embed_url(self):
        """Extracts the YouTube video ID and returns an embed URL."""
        if not self.trailer_url:
            return None  # If no URL is provided, return None

        # Try extracting video ID from different YouTube URL formats
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", self.trailer_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        
        return None  # Return None if no valid ID is found

    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.TimeField() 

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'
