from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm, ContactMessage
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from movies.models import Movie , Booking
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def home(request):
    movies= Movie.objects.all()
    return render(request,'home.html',{'movies':movies})
def register(request):
    if request.method == 'POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            user=authenticate(username=username,password=password)
            login(request,user)
            return redirect('profile')
    else:
        form=UserRegisterForm()
    return render(request,'users/register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('/')
    else:
        form=AuthenticationForm()
    return render(request,'users/login.html',{'form':form})

@login_required
def profile(request):
    bookings= Booking.objects.filter(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'u_form': u_form,'bookings':bookings})

@login_required
def reset_password(request):
    if request.method == 'POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=PasswordChangeForm(user=request.user)
    return render(request,'users/reset_password.html',{'form':form})

def about(request):
    return render(request, 'users/about.html')



def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            # Save message to database (optional)
            ContactMessage.objects.create(name=name, email=email, message=message)

            # Send an email (optional)
            send_mail(
                f'Contact Form Submission from {name}',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Replace with your email
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')

    return render(request, 'users/contact.html')