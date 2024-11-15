from django.shortcuts import render
from django.http import JsonResponse
from .models import AllCountriesStockPerformance

import json

def markets(request):
    return render(request, 'markets.html')


def countries_performance_data(request):
    # Fetch the necessary fields for each country
    data = AllCountriesStockPerformance.objects.values(
        'country_code', 
        'd_performance', 
        'security_name', 
        'index_most_recent_price', 
        'fetch_date'
    )
    return JsonResponse(list(data), safe=False)