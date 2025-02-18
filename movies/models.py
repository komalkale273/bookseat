from django.db import models
from django.contrib.auth.models import User 
import re
from django.utils import timezone
from django.db.models import Count, Q, Prefetch
from datetime import timedelta
import logging
from django.shortcuts import render

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
    show_time = models.DateTimeField(null=True, blank=True)
    genre = models.CharField(max_length=100, default="Unknown")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Action")  # New Field
    is_recommended = models.BooleanField(default=False)

    def get_embed_url(self):
        """Extracts video ID from YouTube URL and returns an embeddable link."""
        if not self.trailer_url:
            return None
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", self.trailer_url)
        return f"https://www.youtube.com/embed/{match.group(1)}" if match else None

    def __str__(self):
        return self.name

    @staticmethod
    def get_recommended_movies(user):
        """Recommends movies based on the user's most booked category."""
        booked_movies = Movie.objects.filter(booking__user=user).distinct()

        if not booked_movies.exists():
            return Movie.objects.order_by('-rating')[:5]  # Default to top-rated movies

        # Find the most booked category by the user
        most_booked_category = (
            Movie.objects.filter(booking__user=user)
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

        if category_movies.exists():
            return category_movies  # Return category-based recommendations

        # If not enough category-based recommendations, suggest trending movies
        popular_movies = Movie.objects.annotate(bookings=Count('booking')).order_by('-bookings')[:5]
        return popular_movies
    


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
    is_reserved = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(null=True, blank=True)

    def is_currently_reserved(self):
        """Checks if the seat is still within the 5-minute reservation timeout."""
        return self.reserved_at and timezone.now() < self.reserved_at + timedelta(minutes=5)

    def release_if_expired(self):
        """Releases the seat if the reservation period has expired."""
        if not self.is_currently_reserved():
            self.is_reserved = False
            self.is_booked = False  # Ensure seat is available again
            self.reserved_at = None
            self.save()

    def __str__(self):
        return f'Seat {self.seat_number} in {self.theater.name} - {"Booked" if self.is_booked else "Available"}'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="bookings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="bookings")
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name="bookings")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    booked_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Automatically update category recommendation after booking."""
        super().save(*args, **kwargs)  # Save booking first
        self.user.profile.update_most_booked_category()  # Update user preference


    def calculate_dynamic_price(self):
        """Dynamically calculates the seat price based on availability and showtime proximity."""
        base_price = 200
        total_seats = self.theater.seats.count()
        remaining_seats = self.theater.seats.filter(is_booked=False).count()

        if total_seats > 0 and remaining_seats / total_seats < 0.2:
            base_price *= 1.5  # Increase price if <20% seats remain

        if self.theater.show_time:
            hours_left = (self.theater.show_time - timezone.now()).total_seconds() / 3600
            if hours_left < 3:
                base_price *= 1.3  # Increase price if showtime is within 3 hours
            elif hours_left < 6:
                base_price *= 1.2  # Increase price if showtime is within 6 hours

        final_price = round(base_price, 2)
        logger.info(f"Dynamic price calculated: ₹{final_price}")
        return final_price

    def save(self, *args, **kwargs):
        if self.amount == 0.0: 
            self.amount = self.calculate_dynamic_price()
        super().save(*args, **kwargs)


class SeatReservation(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Expired", "Expired"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="reservations")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    paypal_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    def is_expired(self):
        """Checks if the reservation has expired (5-minute timeout)."""
        return not self.is_confirmed and timezone.now() > self.reserved_at + timedelta(minutes=5)

    def expire_reservation(self):
        """Marks reservation as expired and releases the seat."""
        if self.is_expired():
            self.status = "Expired"
            self.seat.is_booked = False
            self.seat.is_reserved = False
            self.seat.reserved_at = None
            self.seat.save()
            self.save()

    def __str__(self):
        return f"Seat {self.seat.seat_number} - {self.user.username} ({self.status})"
def home(request):
    return render(request, 'home.html')