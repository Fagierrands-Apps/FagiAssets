from django.urls import path
from . import views

urlpatterns = [
    path('', views.discovery_dashboard, name='discovery_dashboard'),
    # Add more discovery URLs as needed
]