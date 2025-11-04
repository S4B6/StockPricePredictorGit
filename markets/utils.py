from django.utils import timezone
import pytz
from markets.models import Exchange, Exchange_Holiday

MAIN_COUNTRIES = [
    "Mexico", "US", "Canada", "Australia", "France",
    "Germany", "United Kingdom", "China", "India", "Japan",
    "South Korea", "Hong Kong", "Saudi Arabia", "Brazil"
]

def get_market_status(country):
    # Look up the country's exchange
    ex = Exchange.objects.filter(country__iexact=country).first()

    # If no record at all in the database
    if not ex:
        return {"country": country, "is_open": False, "reason": "Closed"}

    # Convert UTC → local
    now_utc = timezone.now()
    local_tz = pytz.timezone(ex.timezone)
    local_time = now_utc.astimezone(local_tz)
    local_date = local_time.date()

    # Weekend
    if local_time.weekday() >= 5:
        return {"country": country, "is_open": False, "reason": "Closed – Weekend"}

    # Holiday
    holiday = Exchange_Holiday.objects.filter(date=local_date, country__iexact=country).first()
    if holiday:
        return {
            "country": country,
            "is_open": False,
            "reason": f"Closed – {holiday.holiday_name.strip()}"
        }

    # Trading hours
    if ex.market_open_local <= local_time.time() <= ex.market_close_local:
        return {"country": country, "is_open": True, "reason": "Open"}

    # Before or after hours
    return {"country": country, "is_open": False, "reason": "Closed"}

def get_main_countries_status():
    return [get_market_status(c) for c in MAIN_COUNTRIES]