# Structure of Databases

#################################
# LIBRARIES

from django.db import models

#################################
# TICKERS AND OTHER RELEVANT DATA

# Equity model
class Equity(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    name_from_source = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    sub_region = models.CharField(max_length=100, null=True, blank=True)
    custom_region = models.CharField(max_length=50)
    constituents_count = models.PositiveIntegerField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=50, blank=True)

# Bond model
class Bond(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    custom_region = models.CharField(max_length=50)
    economic_power = models.CharField(max_length=50, null=True, blank=True)
    issuer_type = models.CharField(max_length=50, null=True, blank=True)
    maturity = models.DateField(null=True, blank=True)
    credit_quality = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=50, blank=True)

# Forex model
class Forex(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    domestic_country_or_region = models.CharField(max_length=100, null=True, blank=True)
    foreign_country_or_region = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=50, blank=True)

# Cryptocurrency model
class Cryptocurrency(models.Model):
    asset_class = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    token_category = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50, blank=True)

# Commodity model
class Commodity(models.Model):
    asset_class = models.CharField(max_length=50)
    commodity_category = models.CharField(max_length=50)
    commodity_subtype = models.CharField(max_length=50, null=True, blank=True)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    exchange = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50, blank=True)

#################################
# PRICE DATA

class DailyPrice(models.Model):
    date = models.DateField(db_index=True)
    ticker = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=20, null=True, blank=True)
    open = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    high = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    low = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    adj_close = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    volume = models.BigIntegerField(null=True)

#################################
# OTHER DATA

class CountryData(models.Model):
    country_name = models.CharField(max_length=100)
    country_second_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3)
    region = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    capital_city = models.CharField(max_length=100)
    most_recent_GDP_USD = models.DecimalField(max_digits=20, decimal_places=2)
    GDP_USD_2023 = models.DecimalField(max_digits=20, decimal_places=2)
    GDP_USD_2022 = models.DecimalField(max_digits=20, decimal_places=2)
    population_size_2023 = models.DecimalField(max_digits=20, decimal_places=2)
