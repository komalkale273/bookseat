from django.db import models
from movies.models import Booking  # Ensure Booking is properly imported

class BookingReport(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="report")
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for Booking ID {self.booking.id} - {self.revenue}"

class PopularMovie(models.Model):
    movie_name = models.CharField(max_length=255)
    total_bookings = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.movie_name} - {self.total_bookings} bookings"

class TheaterTraffic(models.Model):
    theater_name = models.CharField(max_length=255)
    total_visits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.theater_name} - {self.total_visits} visits"

class ActiveUser(models.Model):
    username = models.CharField(max_length=150)
    total_bookings = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} - {self.total_bookings} bookings"
