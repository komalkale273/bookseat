from django.shortcuts import render
from movies.models import Booking, Seat, Theater, Movie  # Import models

def admin_dashboard(request):
    # Calculate some analytics data
    total_bookings = Booking.objects.count()
    total_seats = Seat.objects.count()
    total_movies = Movie.objects.count()
    total_theaters = Theater.objects.count()

    context = {
        "total_bookings": total_bookings,
        "total_seats": total_seats,
        "total_movies": total_movies,
        "total_theaters": total_theaters,
    }
    return render(request, "analytics/dashboard.html", context)
