from django.shortcuts import render
from django.db.models import Sum, Count
from movies.models import Booking, Movie
from django.contrib.auth.models import User
import datetime

def admin_dashboard(request):
    # Total Revenue
    total_revenue = Booking.objects.aggregate(total=Sum('price'))['total'] or 0

    # Total Bookings
    total_bookings = Booking.objects.count()

    # Total Users Registered
    total_users = User.objects.count()

    # Top Movies by Bookings
    top_movies = (
        Booking.objects.values('movie__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    # Bookings Over Time (Last 7 Days)
    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)
    bookings_over_time = (
        Booking.objects.filter(created_at__date__gte=last_week)
        .values('created_at__date')
        .annotate(total=Count('id'))
        .order_by('created_at__date')
    )

    context = {
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'total_users': total_users,
        'top_movies': top_movies,
        'bookings_over_time': bookings_over_time,
    }

    return render(request, 'analytics/admin_dashboard.html', context)
