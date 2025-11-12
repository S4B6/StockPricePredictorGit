# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('predictor/', views.predictor, name='predictor'),
    path('', views.predictor, name='predictor'),
    path("who-we-are/", views.who_we_are, name="who_we_are"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
]