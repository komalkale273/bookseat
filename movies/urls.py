
from django.urls import path
from . import views
# from .views import recommendations
from .views import payment_success, payment_cancel, seat_selection, payment_cancel
from django.urls import include

urlpatterns=[
    path('',views.movie_list,name='movie_list'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/',views.book_seats,name='book_seats'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:theater_id>/seats/', views.seat_selection, name='seat_selection'),
    path('movies/<int:theater_id>/book/', views.book_seats, name='book_seats'),
    # path('recommendations/', recommendations, name='recommendations'),
    # path("create-payment/<int:booking_id>/", create_payment, name="create_payment"),
    path('paypal/', include('paypal.standard.ipn.urls')),  # PayPal IPN handler
    path('book-seat/<int:theater_id>/', views.book_seats, name='book_seats'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
      # path('<int:movie_id>/payment/', views.initiate_payment, name='initiate_payment'),
    # path('<int:movie_id>/confirm-payment/', views.confirm_payment, name='confirm_payment'),


]