from django.urls import path
from .views import admin_dashboard  # Removed missing imports

urlpatterns = [
    path("dashboard/", admin_dashboard, name="admin_dashboard"),
]
