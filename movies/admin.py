from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Movie, Theater, Seat, Booking

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'release_date', 'trailer_embed']
    search_fields = ['name', 'cast']
    list_filter = ['release_date', 'rating']
    ordering = ['release_date']

    def trailer_embed(self, obj):
        if obj.trailer_url:
            return mark_safe(f'<a href="{obj.trailer_url}" target="_blank">Watch Trailer</a>')
        return "No Trailer"
    
    trailer_embed.short_description = "Trailer"

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie', 'time']
    search_fields = ['name', 'movie__name']
    list_filter = ['movie']
    ordering = ['time']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']
    list_filter = ['is_booked', 'theater']
    search_fields = ['seat_number']
    ordering = ['theater', 'seat_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'booked_at']
    list_filter = ['booked_at', 'theater', 'movie']
    search_fields = ['user__username', 'seat__seat_number']
    ordering = ['-booked_at']
