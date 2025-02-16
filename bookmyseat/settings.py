from pathlib import Path
import os
import dj_database_url 
# import paypalrestsdk


EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key')



DEBUG = True
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'users',
    'movies',
    'analytics',
    'paypal.standard.ipn',
]
SITE_ID = 1  
PAYMENT_HOST = "http://127.0.0.1:8000"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Make sure this is here
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # This comes after SessionMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL='auth.User'
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
MEDIA_URL='media'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

ROOT_URLCONF = 'bookmyseat.urls'
LOGIN_URL='/login/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookmyseat.wsgi.application'


 

DATABASES = {
    'default': dj_database_url.parse(
        "postgresql://postgres:uHxydXAGVjfGesSejLQWacKXviEJUJLQ@roundhouse.proxy.rlwy.net:50985/railway",
         conn_max_age=600,
    )
}






AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static/'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP server
EMAIL_PORT = 587  # For TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'komalkale157@gmail.com'
EMAIL_HOST_PASSWORD = 'zgon jjwy buls eaxf'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# PayPal Settings for django-paypal
PAYPAL_RECEIVER_EMAIL = 'sb-algki32074342@business.example.com'
PAYPAL_TEST = True  # Set to False in production
PAYPAL_RETURN_URL = "http://127.0.0.1:8000/payment_success/"
PAYPAL_CANCEL_URL = "http://127.0.0.1:8000/payment_cancel/"