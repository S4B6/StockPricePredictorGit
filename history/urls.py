from django.urls import path
from . import views

urlpatterns = [
    path("", views.history, name="history"),

    path("<str:category>/", views.history_category, name="history_category"),
]

"""    path("download/", views.download_macro_data, name="download_macro_data"),"""