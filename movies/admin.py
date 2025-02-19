from django.urls import path
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import Movie, Theater, Seat, Booking
from analytics.views import admin_dashboard  # Import your dashboard view

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
    list_display = ['name', 'get_movie_name', 'get_time']
    search_fields = ['name', 'movie__name']
    list_filter = ['name']  # Remove 'movie' if it's a ForeignKey

    def get_movie_name(self, obj):
        return obj.movie.name if obj.movie else "No Movie"
    get_movie_name.short_description = "Movie"

    def get_time(self, obj):
        return obj.show_time  # Ensure `show_time` exists in the `Theater` model
    get_time.short_description = "Show Time"
@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked', 'price']
    list_filter = ['is_booked', 'theater']
    search_fields = ['seat_number']
    ordering = ['theater', 'seat_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'get_movie_name', 'theater', 'booked_at', 'is_paid']
    list_filter = ['booked_at', 'theater', 'is_paid']
    search_fields = ['user__username', 'seat__seat_number']
    ordering = ['-booked_at']

    def get_movie_name(self, obj):
        return obj.seat.theater.movie.name if obj.seat and obj.seat.theater.movie else "No Movie"
    get_movie_name.short_description = "Movie"

class CustomAdminSite(admin.AdminSite):
    site_header = "BookMySeat Admin"

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("dashboard/", self.admin_view(admin_dashboard), name="admin_dashboard"),
        ]
        return extra_urls + urls

admin_site = CustomAdminSite(name="custom_admin")
