from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import BookingReport, PopularMovie, TheaterTraffic, ActiveUser

admin.site.register(BookingReport)
admin.site.register(PopularMovie)
admin.site.register(TheaterTraffic)
admin.site.register(ActiveUser)
