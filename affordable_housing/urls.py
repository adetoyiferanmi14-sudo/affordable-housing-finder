"""
URL configuration for the Affordable Housing Finder and Eligibility System.

Five pages only. No admin URL. No login URL. No register URL.
"""
from django.urls import path, include

from properties import views as properties_views

urlpatterns = [
    path('', include('properties.urls')),
    path('eligibility/', include('eligibility.urls')),
    path('data-protection/', properties_views.data_protection, name='data_protection'),
]
