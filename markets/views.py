from django.shortcuts import render
import yfinance as yf
from django.http import JsonResponse
from pytz import timezone
from datetime import datetime
from .utils import fetch_north_america_data, fetch_eastern_europe_data
import json

def markets(request):
    context = {
        "north_america_data": json.dumps(fetch_north_america_data()),  # Serialize to JSON
        "eastern_europe_data": json.dumps(fetch_eastern_europe_data()),  # Serialize to JSON
    }
    return render(request, 'markets.html', context)