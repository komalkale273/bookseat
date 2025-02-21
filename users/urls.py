from django.urls import path
from . import views
from users.forms import CustomSetPasswordForm, CustomPasswordChangeForm
from .views import faq_view

from .views import (
    register, login_view, profile, user_bookings, home, about, contact,
    CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView, CustomPasswordChangeView, CustomPasswordChangeDoneView,
    CustomLogoutView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile, name='profile'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('user_bookings/', user_bookings, name='user_bookings'),
    path('faq/', faq_view, name='faq'),

    # Password Reset URLs
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password Change URLs
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Logout
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
