from django.urls import path
from . import views

urlpatterns = [
    path("", views.history_index, name="history_index"),
]
