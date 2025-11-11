from datetime import datetime, timedelta, date
from django.utils import timezone
import pytz
from markets.models import Exchange, Exchange_Holiday

MAIN_COUNTRIES = [
    "Mexico", "US", "Canada", "Australia", "France",
    "Germany", "United Kingdom", "China", "India", "Japan",
    "South Korea", "Hong Kong", "Saudi Arabia",
]


def get_market_info(country):
    """Return complete open/close status, timing info, and next holiday."""
    ex = Exchange.objects.filter(country__iexact=country.strip()).first()
    if not ex:
        return {
            "country": country.strip(),
            "is_open": False,
            "reason": "No exchange data",
            "open_in": None,
            "close_in": None,
            "next_holiday": "N/A",
            "market_open_local": None,
            "market_close_local": None,
            "timezone": None,
            "local_time_now": None,
        }

    # Convert current UTC → local time
    now_utc = timezone.now()
    local_tz = pytz.timezone(ex.timezone)
    local_time = now_utc.astimezone(local_tz)
    local_date = local_time.date()

    # --- Build localized datetime objects for today ---
    open_dt_naive = datetime.combine(local_date, ex.market_open_local)
    close_dt_naive = datetime.combine(local_date, ex.market_close_local)
    open_dt = local_tz.localize(open_dt_naive)
    close_dt = local_tz.localize(close_dt_naive)

    # --- Check if today is weekend or holiday ---
    is_weekend = local_time.weekday() >= 5
    today_holiday = Exchange_Holiday.objects.filter(
        country__iexact=country.strip(), date=local_date
    ).first()

    # --- Find next holiday (today or after today) ---
    next_holiday_obj = (
        Exchange_Holiday.objects
        .filter(country__iexact=country.strip(), date__gte=local_date)
        .order_by("date")
        .first()
    )
    next_holiday = (
        f"{next_holiday_obj.holiday_name.strip()} ({next_holiday_obj.date.strftime('%d %b %Y')})"
        if next_holiday_obj
        else "No upcoming holiday"
    )

    # --- Initialize defaults ---
    is_open = False
    reason = "Closed"
    open_in = None
    close_in = None

    # --- Determine exact market status ---
    if is_weekend:
        reason = "Closed – Weekend"
    elif today_holiday:
        reason = f"Closed – {today_holiday.holiday_name.strip()}"
    elif ex.market_open_local <= local_time.time() <= ex.market_close_local:
        is_open = True
        delta = close_dt - local_time
        h, rem = divmod(delta.total_seconds(), 3600)
        m = int(rem // 60)
        close_in = f"Closes in {int(h)}h {m}m"
        reason = "Open"
    elif local_time.time() < ex.market_open_local:
        delta = open_dt - local_time
        h, rem = divmod(delta.total_seconds(), 3600)
        m = int(rem // 60)
        open_in = f"Opens in {int(h)}h {m}m"
        reason = "Pre-market"
    else:
        # Market closed for today → find next valid open date
        next_day = local_date + timedelta(days=1)
        while (
            next_day.weekday() >= 5
            or Exchange_Holiday.objects.filter(country__iexact=country.strip(), date=next_day).exists()
        ):
            next_day += timedelta(days=1)

        next_open_naive = datetime.combine(next_day, ex.market_open_local)
        next_open_dt = local_tz.localize(next_open_naive)
        delta = next_open_dt - local_time
        h, rem = divmod(delta.total_seconds(), 3600)
        m = int(rem // 60)
        open_in = f"Opens in {int(h)}h {m}m"
        reason = "Closed"

    return {
        "country": country.strip(),
        "is_open": is_open,
        "reason": reason,  # "Open" / "Closed" / "Pre-market"
        "local_time_now": local_time.strftime("%H:%M"),
        "market_open_local": ex.market_open_local.strftime("%H:%M"),
        "market_close_local": ex.market_close_local.strftime("%H:%M"),
        "open_in": open_in,
        "close_in": close_in,
        "next_holiday": next_holiday,
        "timezone": ex.timezone,
    }

def get_all_market_info():
    """Return info for all main countries."""
    return [get_market_info(c) for c in MAIN_COUNTRIES]
