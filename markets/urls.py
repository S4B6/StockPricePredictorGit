from django.urls import path
from . import views

urlpatterns = [
    path('', views.markets, name='markets'),  # Main page for displaying the charts
]