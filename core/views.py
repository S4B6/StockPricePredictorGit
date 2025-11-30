from django.shortcuts import render
from datetime import datetime

# Create your views here.

def about(request):
    return render(request, 'about.html')

def forecasts(request):
    return render(request, 'forecasts.html')

from datetime import datetime

def who_we_are(request):
    return render(request, "pages/who_we_are.html")

def disclaimer(request):
    return render(request, "pages/disclaimer.html")
