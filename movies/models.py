from django.db import models
from django.contrib.auth.models import User
import re
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)

class Actor(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    CATEGORY_CHOICES = [
        ("Action", "Action"),
        ("Comedy", "Comedy"),
        ("Drama", "Drama"),
        ("Horror", "Horror"),
        ("Romance", "Romance"),
        ("Sci-Fi", "Sci-Fi"),
        ("Thriller", "Thriller"),
        ("Animation", "Animation"),
        ("Documentary", "Documentary"),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="movies/", blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    actors = models.ManyToManyField(Actor, related_name="movies", blank=True)
    trailer_url = models.URLField(blank=True, null=True)
    genre = models.CharField(max_length=100, default="Unknown")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Action")
    is_recommended = models.BooleanField(default=False)
    cast = models.TextField(default="Bollywood")

    def get_embed_url(self):
        if not self.trailer_url:
            return None
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", self.trailer_url)
        return f"https://www.youtube.com/embed/{match.group(1)}" if match else None

    def __str__(self):
        return self.name

    @staticmethod
    def get_recommended_movies(user):
        booked_movies = Movie.objects.filter(bookings__user=user).distinct()
        if not booked_movies.exists():
            return Movie.objects.order_by('-rating')[:5]

        most_booked_category = (
            Movie.objects.filter(bookings__user=user)
            .values('category')
            .annotate(count=Count('category'))
            .order_by('-count')
            .first()
        )

        if most_booked_category:
            category_name = most_booked_category['category']
            category_movies = Movie.objects.filter(category=category_name).exclude(id__in=booked_movies).order_by('-rating')[:5]
        else:
            category_movies = Movie.objects.none()

        return category_movies if category_movies.exists() else Movie.objects.annotate(bookings=Count('bookings')).order_by('-bookings')[:5]

class Theater(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Unknown Location")
    capacity = models.IntegerField(default=100)
    base_price = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="theaters")
    show_time = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return self.name

class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def is_currently_reserved(self):
        if not self.reserved_at:
            return False
        return timezone.now() < self.reserved_at + timedelta(minutes=5)

    def release_if_expired(self):
        if not self.is_currently_reserved():
            self.is_reserved = False
            self.is_booked = False
            self.reserved_at = None
            self.save()

    def calculate_dynamic_price(self):
        base_price = self.theater.base_price
        total_seats = self.theater.seats.count()
        available_seats = self.theater.seats.filter(is_booked=False).count()
        demand_factor = 1 + ((total_seats - available_seats) / total_seats) * 0.5 if total_seats else 1
        time_remaining = (self.theater.show_time - now()).total_seconds() / 3600 if self.theater.show_time else 0
        time_factor = 1
        if time_remaining < 24:
            time_factor = 1.2
        elif time_remaining < 12:
            time_factor = 1.5
        elif time_remaining < 6:
            time_factor = 2
        return round(base_price * demand_factor * time_factor, 2)

    def __str__(self):
        return f'Seat {self.seat_number} in {self.theater.name} - {"Booked" if self.is_booked else "Available"}'

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="bookings")
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    booked_at = models.DateTimeField(auto_now_add=True)

class SeatReservation(models.Model):
    STATUS_CHOICES = [("Pending", "Pending"), ("Confirmed", "Confirmed"), ("Expired", "Expired"), ("Cancelled", "Cancelled")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="reservations")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    paypal_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    def is_expired(self):
        return not self.is_confirmed and timezone.now() > self.reserved_at + timedelta(minutes=5)

    def expire_reservation(self):
        if self.is_expired():
            self.status = "Expired"
            self.seat.is_booked = False
            self.seat.is_reserved = False
            self.seat.reserved_at = None
            self.seat.save()
            self.save()
