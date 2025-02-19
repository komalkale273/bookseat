from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from users.forms import UserRegisterForm, UserUpdateForm, ContactMessage, CustomPasswordChangeForm
from movies.models import Movie, Booking
from users.utils import password_reset_email

def home(request):
    movies= Movie.objects.all()
    return render(request,'home.html',{'movies':movies})
# Custom Password Reset View
class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


# User Registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# User Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# User Profile@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form, 'bookings': bookings})

# Contact Page
def contact(request):
    if request.method == "POST":
        name, email, message = request.POST.get('name'), request.POST.get('email'), request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            send_mail(f'Contact Form Submission from {name}', message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL], fail_silently=False)
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    return render(request, 'users/contact.html')
def validate_password(password, username, email):
    if username.lower() in password.lower() or email.split('@')[0].lower() in password.lower():
        raise ValidationError("Your password can’t be too similar to your personal information.")
    
    if password.isnumeric():
        raise ValidationError("Your password can’t be entirely numeric.")
    
    if len(password) < 8:
        raise ValidationError("Your password must contain at least 8 characters.")
    
    common_passwords = ["password", "123456", "qwerty", "letmein"]
    if password.lower() in common_passwords:
        raise ValidationError("Your password can’t be a commonly used password.")


# Change Password@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

# Logout@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Password Reset


def send_password_reset_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = get_current_site(request).domain
    protocol = "https" if request.is_secure() else "http"

    reset_link = f"{protocol}://{domain}{reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

    # ✅ Render the HTML template
    email_subject = "Password Reset Request"
    email_body = render_to_string("password_reset_email.html", {
        "user": user,
        "protocol": protocol,
        "domain": domain,
        "uid": uid,
        "token": token
    })

    # ✅ Send the email as an HTML email
    email = EmailMultiAlternatives(email_subject, "", settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(email_body, "text/html")  
    email.send()

# Reset Password View
def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'users/change_password.html', {"valid": True})

            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully. You can now log in.")
            return redirect('login')
    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('forget_password')

    return render(request, 'users/change_password.html', {"valid": True})

def forget_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, 'No user found with this email.')
            return redirect('forget-password')

        send_password_reset_email(request, user)  
        messages.success(request, 'An email has been sent with password reset instructions.')
        return redirect('forget-password')

    return render(request, 'users/forget_password.html')

def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/user_bookings.html', {'form': form, 'bookings': bookings})





# About Page
def about(request):
    return render(request, "users/about.html")
