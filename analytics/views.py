from django.shortcuts import render
from django.db.models import Count, Sum
from django.apps import apps  # ✅ Import get_model utility

def admin_dashboard(request):
    Booking = apps.get_model('movies', 'Booking')  # ✅ Dynamically load the model

    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_users = Booking.objects.values('user').distinct().count()
    total_seats = Booking.objects.count()

    top_movies = (
        Booking.objects.values('movie__name')
        .annotate(bookings=Count('id'))
        .order_by('-bookings')[:5]
    )

    top_theaters = (
        Booking.objects.values('theater__name')
        .annotate(bookings=Count('id'))
        .order_by('-bookings')[:5]
    )

    active_users = (
        Booking.objects.values('user__username')
        .annotate(bookings=Count('id'))
        .order_by('-bookings')[:5]
    )

    recent_bookings = Booking.objects.select_related('user', 'movie', 'theater').order_by('-booked_at')[:5]

    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'total_seats': total_seats,
        'top_movies': top_movies,
        'top_theaters': top_theaters,
        'active_users': active_users,
        'recent_bookings': recent_bookings,
    }

    return render(request, 'analytics/dashboard.html', context)
