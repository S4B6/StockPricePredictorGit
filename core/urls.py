# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('forecasts/', views.forecasts, name='forecasts'),
    path('', views.forecasts, name='forecasts'),
    path("who-we-are/", views.who_we_are, name="who_we_are"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
]