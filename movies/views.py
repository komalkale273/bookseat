
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings




def movie_list(request):
    search_query = request.GET.get('search')
    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})


# @login_required(login_url='/login/')
# def book_seats(request, theater_id):
#     theaters = get_object_or_404(Theater, id=theater_id)
#     seats = Seat.objects.filter(theater=theaters)

#     if request.method == 'POST':
#         selected_seats = request.POST.getlist('seats') 
#         error_seats = []

        
#         if not selected_seats:
#             return render(request, "movies/seat_selection.html", {
#                 'theater': theaters, "seats": seats, 'error': "No seats were selected. Please select at least one seat."
#             })

#         try:
#             with transaction.atomic():
#                 for seat_id in selected_seats:
                    
#                     seat = get_object_or_404(Seat, id=seat_id, theater=theaters)

#                     if seat.is_booked:  
#                         continue

                    
#                     Booking.objects.create(
#                         user=request.user,
#                         seat=seat,
#                         movie=theaters.movie,
#                         theater=theaters
#                     )

                    
#                     seat.is_booked = True
#                     seat.save()

#         except Exception as e:
           
#             print(f"Error during booking: {e}")
#             return render(request, 'movies/seat_selection.html', {
#                 'theater': theaters,
#                 "seats": seats,
#                 'error': "An error occurred while processing your booking. Please try again."
#             })

        
#         if error_seats:
#             error_message = f"The following seats are already booked: {', '.join(map(str, error_seats))}"
#             return render(request, 'movies/seat_selection.html', {
#                 'theater': theaters, "seats": seats, 'error': error_message
#             })

        
#         return redirect('profile')

   
#     return render(request, 'movies/seat_selection.html', {
#         'theater': theaters, "seats": seats
#     })


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
                for seat_id in selected_seats:
                    seat = get_object_or_404(Seat, id=seat_id, theater=theater)

                    if seat.is_booked:
                        error_seats.append(seat.seat_number)
                        continue

                    # Create booking record
                    booking = Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theater.movie,
                        theater=theater
                    )

                    seat.is_booked = True
                    seat.save()

                    # Send confirmation email to the user
                    send_mail(
                        subject=f"Booking Confirmation - {theater.movie.name}",
                        message=f"Dear {request.user.username},\n\n"
                                f"Your booking for {theater.movie.name} at {theater.name} is confirmed.\n"
                                f"Seats Booked: {', '.join([seat.seat_number for seat in Seat.objects.filter(id__in=selected_seats)])}\n\n"
                                f"Thank you for booking with us!",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[request.user.email],  # Sends to the user who booked
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

        # Redirect to confirmation page
        return render(request, 'movies/confirmation.html', {
            'theater': theater,
            'selected_seats': selected_seats,
            'user': request.user
        })

    return render(request, 'movies/seat_selection.html', {
        'theater': theater, 'seats': seats
    })
def send_booking_confirmation_email(user, theater, selected_seats):
    # Generate the seat numbers and details
    seat_numbers = [Seat.objects.get(id=seat_id).seat_number for seat_id in selected_seats]
    seat_details = ", ".join(seat_numbers)

    # Prepare email content
    subject = f"Your Movie Seat Booking Confirmation: {theater.movie.name} at {theater.name}"
    message = f"Dear {user.username},\n\n"
    message += f"Thank you for booking seats for {theater.movie.name} at {theater.name}. Here are your seat details:\n"
    message += f"Seats: {seat_details}\n\n"
    message += "We look forward to seeing you at the theater.\n\n"
    message += "Best regards,\nThe Movie Booking Team"

    # Send the email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


