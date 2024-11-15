from django.urls import path
from . import views

urlpatterns = [
    path('', views.markets, name='markets'),  # Main page for displaying the charts
    path('countries-performance-data/', views.countries_performance_data, name='countries_performance_data'),
]