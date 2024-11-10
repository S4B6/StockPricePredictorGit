#Structure of Databases
from django.db import models

class Asset(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # e.g., "^GSPC"
    name = models.CharField(max_length=100)  # e.g., "S&P 500"
    asset_class = models.CharField(max_length=50)  # e.g., "Equity Index"
    
    # Optional fields specific to equity indices
    country = models.CharField(max_length=100, null=True, blank=True, default="unkown")
    custom_region = models.CharField(max_length=50)
    constituents_count = models.PositiveIntegerField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.name} ({self.symbol})"

class DailyPrice(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    symbol = models.CharField(max_length=20, null=True, blank=True)
    open = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    high = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    low = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    adj_close = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    volume = models.BigIntegerField(null=True)

      # New optional fields for calculated metrics
    # moving_average_50 = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    # moving_average_200 = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    # volatility = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)

    class Meta:
        unique_together = ('asset', 'date')

    def __str__(self):
        return f"{self.asset.symbol} on {self.date}: O={self.open}, H={self.high}, L={self.low}, C={self.adj_close}, V={self.volume}"
