from django.shortcuts import render 
from django.db.models import Count, Sum  
from movies.models import Booking, Movie 
from django.shortcuts import render, get_object_or_404
from movies.models import Booking, Seat


def admin_dashboard(request):
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(total=Sum('amount'))['total'] or 0
    seats_booked = Booking.objects.count()

    recent_bookings = Booking.objects.select_related('user', 'movie', 'seat').order_by('-booked_at')[:10]

    popular_movie = Movie.objects.annotate(bookings=Count('booking')).order_by('-bookings').first()

    context = {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "seats_booked": seats_booked,
        "recent_bookings": recent_bookings,
        "popular_movie": popular_movie or {"title": "No Data", "bookings": 0}
    }

    return render(request, "analytics/dashboard.html", context) 

def reserve_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    return render(request, "analytics/reserve_seat.html", {"seat": seat})

def complete_booking(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    return render(request, "analytics/complete_booking.html", {"seat": seat})
