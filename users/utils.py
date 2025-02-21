from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_password_reset_email(request, user):
    subject = "Password Reset Requested"
    email_template_name = "users/password_reset_email.html"
    context = {
        "email": user.email,
        "domain": request.get_host(),
        "site_name": "Your Website",
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
        "protocol": "https" if request.is_secure() else "http",
    }
    email = render_to_string(email_template_name, context)
    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
