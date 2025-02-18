from django.urls import path
from . import views
from users.forms import CustomSetPasswordForm, CustomPasswordChangeForm

from .views import (register, login_view, profile,user_bookings,  home, about, contact ,change_password_view,
CustomPasswordResetView                
)

from django.contrib.auth import views as auth_views

# class CustomLogoutView(auth_views.LogoutView):
#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)

urlpatterns = [
    path('',home,name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile, name='profile'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('user_bookings/', user_bookings, name='user_bookings'),
    

    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path("forget-password/", CustomPasswordResetView.as_view(), name="forget_password"),
    path("passwordreset/", auth_views.PasswordResetView.as_view(
        template_name="users/password_reset_form.html"
    ), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html"
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete"),
    
    # Change Password
    path("change-password/", change_password_view, name="change_password"),
]
