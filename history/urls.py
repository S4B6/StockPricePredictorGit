from django.urls import path
from . import views

urlpatterns = [

    # 1) CHART FETCH (must be FIRST)
    path("chart/<int:chart_id>/", views.fetch_chart, name="fetch_chart"),

    # Download CSV
    path("download/", views.download_chart_csv, name="history_download"),

    # Landing page (your animated page)
    path("", views.history_home, name="history"),

    # Category page (macro, rates, equity…)
    path("<str:category>/", views.history_category, name="history_category"),

    # Article pages (ECB, Fed, etc.)
    path("<path:slug>/", views.history_detail, name="history_detail"),

    
]
