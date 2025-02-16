from django.db import models
from django.contrib.auth.models import User 
import re
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta


class Movie(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="movies/", blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    cast = models.TextField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    show_time = models.DateTimeField(null=True, blank=True)
    genre = models.CharField(max_length=100, default="Unknown")
    
    def get_embed_url(self):
        if not self.trailer_url:
            return None
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", self.trailer_url)
        if match:
            return f"https://www.youtube.com/embed/{match.group(1)}"
        return None
    
    def __str__(self):
        return self.name

    @staticmethod
    def get_recommended_movies(user):
        booked_movies = Movie.objects.filter(booking__user=user).distinct()
        if not booked_movies.exists():
            return Movie.objects.order_by('-rating')[:5]
        similar_movies = Movie.objects.filter(
            cast__in=booked_movies.values_list('cast', flat=True)
        ).exclude(id__in=booked_movies.values_list('id', flat=True)).distinct()
        if similar_movies.count() < 5:
            popular_movies = Movie.objects.annotate(bookings=Count('booking')).order_by('-bookings')[:5]
            return (similar_movies | popular_movies)[:5]
        return similar_movies[:5]


class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.TimeField()
    total_seats = models.PositiveIntegerField(default=50)
    show_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'



class Seat(models.Model):
    theater = models.ForeignKey('Theater', on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(null=True, blank=True)  # Stores reservation timestamp

    def is_currently_reserved(self):
        """Checks if the seat is still within the reservation timeout period (5 minutes)."""
        if self.reserved_at:
            return timezone.now() < self.reserved_at + timedelta(minutes=5)
        return False

    def release_if_expired(self):
        """Releases the seat if the reservation period has expired."""
        if not self.is_currently_reserved():  
            self.is_reserved = False
            self.reserved_at = None
            self.save()

    def __str__(self):
        return f'Seat {self.seat_number} in {self.theater.name} - {"Booked" if self.is_booked else "Available"}'
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    booked_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def calculate_dynamic_price(self):
        base_price = 200
        total_seats = Seat.objects.filter(theater=self.theater).count()
        remaining_seats = Seat.objects.filter(theater=self.theater, is_booked=False).count()

        if total_seats > 0 and remaining_seats / total_seats < 0.2:
            base_price *= 1.5 

        if self.theater.show_time:
            hours_left = (self.theater.show_time - timezone.now()).total_seconds() / 3600
            if hours_left < 3:
                base_price *= 1.3 
            elif hours_left < 6:
                base_price *= 1.2  

        return round(base_price, 2)

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
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
            self.seat.reserved_at = None
            self.seat.save()
            self.save()

    def __str__(self):
        return f"Seat {self.seat.seat_number} - {self.user.username} ({self.status})"
