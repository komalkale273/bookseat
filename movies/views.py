from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator
from urllib.parse import urlparse, parse_qs
import re
from .models import Movie, get_recommended_movies


from .models import Movie, Theater, Seat, Booking


def movie_list(request):
    """ View to list movies with search and pagination. """
    search_query = request.GET.get('search', '')
    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(name__icontains=search_query)

    # Pagination: Show 4 movies per page
    paginator = Paginator(movies, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "movies/movie_list.html", {"movies": page_obj})


def theater_list(request, movie_id):
    """ View to list theaters for a selected movie. """
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        error_seats = []

        if not selected_seats:
            return render(request, "movies/seat_selection.html", {
                'theater': theater, 'seats': seats, 'error': "No seats were selected. Please select at least one seat."
            })

        try:
            with transaction.atomic():
                total_price = 0

                for seat_id in selected_seats:
                    seat = get_object_or_404(Seat, id=seat_id, theater=theater)

                    if seat.is_booked:
                        error_seats.append(seat.seat_number)
                        continue

                    # ✅ Create booking record with dynamic pricing
                    booking = Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theater.movie,
                        theater=theater
                    )
                    booking.amount = booking.calculate_dynamic_price()
                    booking.save()

                    seat.is_booked = True
                    seat.save()
                    total_price += booking.amount

                # ✅ Send confirmation email with dynamic price
                send_mail(
                    subject=f"Booking Confirmation - {theater.movie.name}",
                    message=f"Dear {request.user.username},\n\n"
                            f"Your booking for {theater.movie.name} at {theater.name} is confirmed.\n"
                            f"Seats Booked: {', '.join([seat.seat_number for seat in Seat.objects.filter(id__in=selected_seats)])}\n"
                            f"Total Amount Paid: ₹{total_price}\n\n"
                            f"Thank you for booking with us!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False
                )

        except Exception as e:
            print(f"Error during booking: {e}")
            return render(request, 'movies/seat_selection.html', {
                'theater': theater, 'seats': seats, 'error': "An error occurred while processing your booking."
            })

        if error_seats:
            return render(request, 'movies/seat_selection.html', {
                'theater': theater, 'seats': seats,
                'error': f"The following seats are already booked: {', '.join(error_seats)}"
            })

        return render(request, 'movies/confirmation.html', {
            'theater': theater,
            'selected_seats': selected_seats,
            'total_price': total_price,
            'user': request.user
        })

    return render(request, 'movies/seat_selection.html', {
        'theater': theater, 'seats': seats
    })

def send_booking_confirmation_email(user, theater, seat_numbers, amount):
    """ Sends booking confirmation email to the user. """
    subject = f"Booking Confirmation - {theater.movie.name}"
    message = f"Dear {user.username},\n\n" \
              f"Your booking for {theater.movie.name} at {theater.name} is confirmed.\n" \
              f"Seats Booked: {', '.join(seat_numbers)}\n" \
              f"Amount Paid: ₹{amount}\n\n" \
              f"Thank you for booking with us!"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )


def movie_detail(request, movie_id):
    """ View to display movie details including embedded trailer video. """
    movie = get_object_or_404(Movie, id=movie_id)

    # Extract YouTube video ID from various formats
    video_id = None
    if movie.trailer_url:
        parsed_url = urlparse(movie.trailer_url)
        query_params = parse_qs(parsed_url.query)

        if "v" in query_params:
            video_id = query_params["v"][0]  # Extract video ID from URL
        elif parsed_url.netloc in ["youtu.be", "www.youtu.be"]:
            video_id = parsed_url.path[1:]  # Extract from shortened URL format

    embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None

    return render(request, "movies/movie_detail.html", {"movie": movie, "embed_url": embed_url})


@login_required(login_url='/login/')
def my_bookings(request):  # <- If this exists instead of `user_bookings`
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'movies/user_bookings.html', {'bookings': bookings})
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'theater': booking.theater if booking.theater else None,
        'selected_seats': booking.seats.all() if booking.seats.exists() else [],
    }
    return render(request, 'movies/booking_success.html', context)


@login_required
def recommendations(request):
    user = request.user

    # Get the list of movies the user has booked
    user_booked_movies = Booking.objects.filter(user=user).values_list('movie', flat=True).distinct()

    # Recommend movies that the user has NOT booked yet
    recommended_movies = Movie.objects.exclude(id__in=user_booked_movies).order_by('-rating')[:6]

    return render(request, "movies/recommendations.html", {"movies": recommended_movies})
