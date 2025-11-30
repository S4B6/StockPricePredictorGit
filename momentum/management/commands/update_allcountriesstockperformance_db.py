from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from momentum.models import Equity_Tickers, CountryData, AllCountriesStockPerformance, DailyPrice

class Command(BaseCommand):
    help = 'Populate the AllCountriesStockPerformance table with initial data'

    def handle(self, *args, **kwargs):
        # Fetch non-empty tickers from Equity_Tickers with non-null values in countries
        tickers = Equity_Tickers.objects.filter(ticker__isnull=False, country__isnull=False).exclude(ticker='')

        for ticker_entry in tickers:
            # Determine the country to use for the country code lookup
            country = ticker_entry.country
            custom_region = ticker_entry.custom_region
            country_code = CountryData.objects.filter(country_name=country).values_list('country_code', flat=True).first()

            # Get the most recent price and fetch date for the ticker
            latest_data = DailyPrice.objects.filter(ticker=ticker_entry.ticker).order_by('-date').values_list('adj_close', 'fetch_date').first()
            latest_price, fetch_date = latest_data if latest_data else (None, None)

            # Calculate performance metrics based on different timeframes
            d_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=1)
            w_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=7)
            m_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=30)
            y_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=365)
            decade_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=3650)

            # Update or create entry in AllCountriesStockPerformance
            AllCountriesStockPerformance.objects.update_or_create(
                country_code=country_code,  # This can be None if neither country nor region yields a code
                asset_class=ticker_entry.asset_class,
                ticker=ticker_entry.ticker,
                security_name=ticker_entry.name,
                country_name=country,
                custom_region_name=custom_region,

                defaults={
                    'index_most_recent_price': latest_price,
                    'fetch_date': fetch_date,
                    'd_performance': d_performance,
                    'w_performance': w_performance,
                    'm_performance': m_performance,
                    'y_performance': y_performance,
                    'decade_performance': decade_performance
                }
            )

        self.stdout.write("AllCountriesStockPerformance table successfully populated.")

    def calculate_performance(self, ticker, latest_price, days):
        """Calculate performance over a specific number of days."""
        if latest_price is None:
            return None
        
        # Get the date of the latest price
        latest_price_entry = DailyPrice.objects.filter(ticker=ticker).order_by('-date').first()
        latest_price_date = latest_price_entry.date if latest_price_entry else None

        if not latest_price_date:
            return None

        # Calculate the target date based on the latest price date
        target_date = latest_price_date - timedelta(days=days)
                
        # Get the closing price on or before the target date
        target_price = DailyPrice.objects.filter(ticker=ticker, date__lte=target_date).order_by('-date').values_list('adj_close', flat=True).first()

        # Calculate and return the performance percentage
        if target_price:
            return ((latest_price - target_price) / target_price) * 100
        else:
            return None
