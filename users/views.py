from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from .models import FAQ
from .forms import FAQForm
from django.views.decorators.csrf import csrf_protect
from users.forms import (
    UserRegisterForm, UserUpdateForm, ContactMessage,
    CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
)
from movies.models import Movie, Booking
from .utils import send_password_reset_email
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView, LogoutView
)



def home(request):
    movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies})



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


from django.middleware.csrf import get_token

@csrf_protect
def login_view(request):
    print("CSRF Token:", get_token(request))  # Debugging Line

    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('core:index')

    if request.method == "POST":
        print("Received CSRF Token:", request.POST.get('csrfmiddlewaretoken'))  # Debugging Line
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}!!')
                return redirect('/')

            else:
                messages.warning(request, f'User {username} .. Wrong credentials!!')

        except User.DoesNotExist:
            messages.warning(request, f'User {username} does not exist')

    return render(request, 'users/login.html', {})

    return render(request, 'users/login.html')
@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form, 'bookings': bookings})



def contact(request):
    if request.method == "POST":
        name, email, message = request.POST.get('name'), request.POST.get('email'), request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            send_mail(
                f'Contact Form Submission from {name}', message, settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL], fail_silently=False
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    return render(request, 'users/contact.html')



@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'users/user_bookings.html', {'bookings': bookings})



def about(request):
    return render(request, "users/about.html")



class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm  

    def form_valid(self, form):
        messages.success(self.request, "Password reset email sent. Check your inbox.")
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy('password_reset_complete')
    form_class = CustomSetPasswordForm 


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"



class CustomPasswordChangeView(PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy('password_change_done')
    form_class = CustomPasswordChangeForm


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "users/password_change_done.html"



class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
    
def faq_view(request):
    faqs = FAQ.objects.all()
    form = FAQForm()

    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('faq')  

    return render(request, 'users/faq.html', {'faqs': faqs, 'form': form})
