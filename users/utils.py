from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def password_reset_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # Get dynamic domain
    domain = get_current_site(request).domain
    protocol = "https" if request.is_secure() else "http"
    
    reset_link = f"{protocol}://{domain}/reset/{uid}/{token}/"
    
    subject = "Reset Your Password"
    email_body = render_to_string("users/password_reset_email.html", {
        "user": user,
        "reset_link": reset_link,
    })
    
    email = EmailMultiAlternatives(subject, "", settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(email_body, "text/html")
    email.send()
    
    return True
