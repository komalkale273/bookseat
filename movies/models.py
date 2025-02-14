from django.db import models
from django.contrib.auth.models import User 
import re
from django.utils import timezone


from datetime import datetime


class Movie(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="movies/", blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    cast = models.TextField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    show_time = models.DateTimeField(null=True, blank=True)
    
    def get_embed_url(self):
        if not self.trailer_url:
            return None
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", self.trailer_url)
        if match:
            return f"https://www.youtube.com/embed/{match.group(1)}"
        return None
    
    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.TimeField()
    total_seats = models.PositiveIntegerField(default=50)
    show_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'

class Booking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    theater = models.ForeignKey('Theater', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    booked_at = models.DateTimeField(auto_now_add=True) 

    def calculate_dynamic_price(self):
        base_price = 200
        total_seats = Seat.objects.filter(theater=self.theater).count()
        remaining_seats = Seat.objects.filter(theater=self.theater, is_booked=False).count()

        if total_seats == 0:  
            return round(base_price, 2)

        if remaining_seats / total_seats < 0.2:
            base_price *= 1.5 

        show_time = self.theater.show_time
        if show_time is None:
            return round(base_price, 2)  
        hours_left = (show_time - timezone.now()).total_seconds() / 3600

        if hours_left < 3:
            base_price *= 1.3 
        elif hours_left < 6:
            base_price *= 1.2  

        return round(base_price, 2)

    def save(self, *args, **kwargs):
        """Override save method to calculate price automatically"""
        if self.amount == 0.0: 
            self.amount = self.calculate_dynamic_price()
        super().save(*args, **kwargs)
