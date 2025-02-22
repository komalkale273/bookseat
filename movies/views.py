from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.utils.timezone import now, timedelta
from django.urls import reverse
from django.contrib import messages
import uuid
from django.db.models import Count
from django.utils import timezone
from .models import Movie, Theater, Seat, Booking
from paypal.standard.forms import PayPalPaymentsForm
from django.utils.timezone import localtime
from urllib.parse import urlparse,parse_qs

def movie_list(request):
    search_query = request.GET.get('search', '')
    movies = Movie.objects.all()
    if search_query:
        movies = movies.filter(name__icontains=search_query)
    paginator = Paginator(movies, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "movies/movie_list.html", {"movies": page_obj})


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie_id=movie_id)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    video_id = None
    if movie.trailer_url:
        parsed_url = urlparse(movie.trailer_url)
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0] or (parsed_url.path[1:] if parsed_url.netloc in ["youtu.be", "www.youtu.be"] else None)
    embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None
    return render(request, "movies/movie_detail.html", {"movie": movie, "embed_url": embed_url})


def release_expired_reservations():
    expired_time = timezone.now() - timedelta(minutes=5)
    expired_seats = Seat.objects.filter(reserved_at__lt=expired_time, is_reserved=True)
    expired_seats.update(is_reserved=False, reserved_at=None)

def seat_selection(request, theater_id):
    release_expired_reservations()
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)
    return render(request, 'movies/seat_selection.html', {'theater': theater, 'seats': seats})

@login_required
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    selected_seats = request.POST.getlist('seats')

    if not selected_seats:
        messages.error(request, "No seats selected. Please select at least one seat.")
        return redirect('seat_selection', theater_id=theater.id)

    seats = Seat.objects.filter(id__in=selected_seats)
    remaining_seats = Seat.objects.filter(theater=theater, is_booked=False).count()
    showtime = theater.showtime
    time_to_show = (showtime - timezone.now()).total_seconds() / 3600
    base_price = 500
    price_multiplier = 1.0

    if remaining_seats < 10:
        price_multiplier += 0.2
    if 0 < time_to_show <= 3:
        price_multiplier += 0.15
    if time_to_show > 6:
        price_multiplier -= 0.1

    total_price = sum((seat.price or base_price) * price_multiplier for seat in seats)
    booked_seats = ', '.join(seat.seat_number for seat in seats)

    with transaction.atomic():
        for seat in seats:
            seat.refresh_from_db()
            if seat.is_booked or seat.is_reserved:
                messages.error(request, f"Seat {seat.seat_number} is no longer available.")
                return redirect('seat_selection', theater_id=theater.id)
            seat.is_reserved = True
            seat.reserved_at = now()
            seat.save()

    request.session['selected_seats'] = selected_seats
    request.session['theater_id'] = theater_id
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": str(total_price),
        "item_name": f"Movie Tickets - {theater.movie.name}",
        "invoice": str(uuid.uuid4()),
        "currency_code": "USD",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payment_success')),
        "cancel_return": request.build_absolute_uri(reverse('payment_cancel')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'movies/paypal_payment.html', {"form": form, "theater": theater, "total_price": total_price, "selected_seats": booked_seats})
@login_required
def payment_success(request):
    theater_id = request.session.pop('theater_id', None)
    selected_seats = request.session.pop('selected_seats', [])

    if not theater_id or not selected_seats:
        messages.error(request, "Payment successful, but booking information is missing.")
        return redirect('movie_list')

    theater = get_object_or_404(Theater, id=theater_id)
    with transaction.atomic():
        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=int(seat_id), theater=theater)
            if not seat.is_reserved:
                messages.error(request, f"Seat {seat.seat_number} reservation expired. Please rebook.")
                return redirect('seat_selection', theater_id=theater.id)
            seat.is_reserved = False
            seat.is_booked = True
            seat.reserved_at = None
            seat.save()
            Booking.objects.create(user=request.user, movie=theater.movie, theater=theater, seat=seat, amount=seat.price, is_paid=True)

    send_booking_confirmation_email(request.user, theater, selected_seats, len(selected_seats) * 500)
    messages.success(request, "Payment successful! Your booking is confirmed.")
    return render(request, "movies/booking_success.html", {"theater": theater, "selected_seats": selected_seats})
def send_booking_confirmation_email(user, theater, seat_numbers, amount):
    currency_symbol = "₹" if settings.CURRENCY == "INR" else "$"
    subject = f"Booking Confirmation - {theater.movie.name}"
    message = (f"Dear {user.username},\n\nYour booking for {theater.movie.name} at {theater.name} is confirmed.\nSeats: {', '.join(seat_numbers)}\nTotal: {currency_symbol}{amount}\n\nThank you for choosing our service!")
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

@login_required
def payment_cancel(request):
    selected_seats = request.session.pop('selected_seats', [])
    theater_id = request.session.pop('theater_id', None)
    if theater_id and selected_seats:
        theater = get_object_or_404(Theater, id=theater_id)
        Seat.objects.filter(id__in=selected_seats, theater=theater).update(is_reserved=False, reserved_at=None)
    messages.error(request, "Payment cancelled. Your reserved seats have been released.")
    return redirect('movie_list')

def payment_view(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    selected_seats = Seat.objects.filter(is_reserved=True, theater=theater)

    for seat in selected_seats:
        if seat.reserved_at:
            seat.expiry_time = localtime(seat.reserved_at) + timedelta(minutes=5)  # Ensure proper timezone handling
    
    return render(request, "payment.html", {
        "theater": theater,
        "selected_seats": selected_seats,
    })


@login_required
def recommendations(request):
    user = request.user

    # Get movies booked by the user
    user_booked_movies = Booking.objects.filter(user=user).values_list('movie_id', flat=True)

    # Get categories of the booked movies
    user_booked_categories = (
        Movie.objects.filter(id__in=user_booked_movies)
        .values_list('category', flat=True)
        .distinct()
    )

    # Recommend movies based on category preference, excluding already booked ones
    if user_booked_categories:
        recommended_movies = (
            Movie.objects.filter(category__in=user_booked_categories)
            .exclude(id__in=user_booked_movies)
            .order_by('-rating')[:6]
        )
    else:
        # Fallback: Show top-rated movies if no booking history
        recommended_movies = Movie.objects.all().order_by('-rating')[:6]

    return render(request, "movies/recommendations.html", {"movies": recommended_movies})
