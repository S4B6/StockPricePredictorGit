# Structure of Databases

#################################
# LIBRARIES

from django.db import models
from django.utils import timezone

#################################
# TICKERS AND OTHER RELEVANT DATA

# Equity model
class Equity_Tickers(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    name_from_source = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    sub_region = models.CharField(max_length=100, null=True, blank=True)
    custom_region = models.CharField(max_length=50, null=True, blank=True)
    constituents_count = models.PositiveIntegerField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
        
    class Meta:
        unique_together = ('asset_class', 'name')

# Bond model
class Bond_Tickers(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    name_from_source = models.CharField(max_length=100, null=True, blank=True)    
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    custom_region = models.CharField(max_length=50, null=True, blank=True)
    economic_power_region = models.CharField(max_length=50, null=True, blank=True)
    issuer_type = models.CharField(max_length=50, null=True, blank=True)
    maturity = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    credit_quality = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
        
    class Meta:
        unique_together = ('asset_class', 'name')

# Forex model
class Forex_Tickers(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    name_from_source = models.CharField(max_length=100, null=True, blank=True)
    domestic_country_or_region = models.CharField(max_length=100, null=True, blank=True)
    foreign_country_or_region = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
        
    class Meta:
        unique_together = ('asset_class', 'name')

# Cryptocurrency model
class Cryptocurrency_Tickers(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    name_from_source = models.CharField(max_length=100, null=True, blank=True)
    token_category = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
        
    class Meta:
        unique_together = ('asset_class', 'name')

# Commodity model
class Commodity_Tickers(models.Model):
    asset_class = models.CharField(max_length=50)
    commodity_category = models.CharField(max_length=50)
    commodity_subtype = models.CharField(max_length=50, null=True, blank=True)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    name_from_source = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
        
    class Meta:
        unique_together = ('asset_class', 'name')

### To monitor if top markets are open or closed ###

# Exchanges
class Exchange(models.Model):
    country = models.CharField(max_length=100)
    exchange_short_name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50)  # e.g. "America/Mexico_City"
    market_open_local = models.TimeField()
    market_close_local = models.TimeField()

# Holiday
class Exchange_Holiday(models.Model):
    date = models.DateField()
    country = models.CharField(max_length=100)
    holiday_name = models.CharField(max_length=100)

#################################
# DAILYPRICE DATA

class DailyPrice(models.Model):
    date = models.DateField(db_index=True)
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    open = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    high = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    low = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    adj_close = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    fetch_date = models.DateTimeField(default=timezone.now)  # Set to current timestamp on creation
    is_live = models.BooleanField(default=False)
    time_utc = models.TimeField(null=True, blank=True)

#################################
# OUTPUTS

########### EQUITIES

# All Countries - Stock Performace
class AllCountriesStockPerformance(models.Model):
    country_code = models.CharField(max_length=3, blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    custom_region_name = models.CharField(max_length=100, null=True, blank=True)

    # Other info
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20)
    security_name = models.CharField(max_length=100)
    
    # Stock performance over different timeframes
    d_performance = models.FloatField(null=True, blank=True)
    w_performance = models.FloatField(null=True, blank=True)
    m_performance = models.FloatField(null=True, blank=True) 
    y_performance = models.FloatField(null=True, blank=True)
    decade_performance = models.FloatField(null=True, blank=True)

    # Index price (current or reference price)
    index_most_recent_price = models.FloatField(null=True, blank=True)

    # Track when this data was fetched from yfinance
    fetch_date = models.DateTimeField(default=timezone.now)  # Set to current timestamp on creation

# All Regions - Stock Performance
class AllRegionsStockPerformance(models.Model):

    region_name = models.CharField(max_length=100, null=True, blank=True)
    custom_region_name = models.CharField(max_length=100, null=True, blank=True)
    country_list = models.TextField(null=True, blank=True)  # To store country codes as a comma-separated string
    
    # Other info
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20)
    security_name = models.CharField(max_length=100)
    
    # Stock performance over different timeframes
    d_performance = models.FloatField(null=True, blank=True)
    w_performance = models.FloatField(null=True, blank=True)
    m_performance = models.FloatField(null=True, blank=True) 
    y_performance = models.FloatField(null=True, blank=True)
    decade_performance = models.FloatField(null=True, blank=True)

    # Index price (current or reference price)
    index_most_recent_price = models.FloatField(null=True, blank=True)

    # Track when this data was fetched from yfinance
    fetch_date = models.DateTimeField(default=timezone.now)  # Set to current timestamp on creation

#################################
# OTHER DATA

class CountryData(models.Model):
    country_name = models.CharField(max_length=100)
    country_second_name = models.CharField(max_length=100, null=True, blank=True)
    country_code = models.CharField(max_length=3)
    region = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    capital_city = models.CharField(max_length=100)
    most_recent_GDP_USD = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    GDP_USD_2023 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    GDP_USD_2022 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    population_size_2023 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
