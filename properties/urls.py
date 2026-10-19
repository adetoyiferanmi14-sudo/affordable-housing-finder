from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.search, name='property_search'),
    path('properties/<int:pk>/', views.detail, name='property_detail'),
]
