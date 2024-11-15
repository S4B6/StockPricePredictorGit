from django.core.management.base import BaseCommand
from django.db.models import Avg, Max, Min
from datetime import timedelta
from markets.models import Equity_Tickers, AllRegionsStockPerformance, AllCountriesStockPerformance, DailyPrice

class Command(BaseCommand):
    help = 'Populate the AllRegionsStockPerformance table with custom regions, individual ticker data, and calculated averages'

    def handle(self, *args, **kwargs):
        # Stage 1: Populate with unique custom regions
        self.populate_custom_regions()

        # Stage 2: Populate with individual tickers
        self.populate_individual_tickers()

        # Stage 3: Populate missing fields for custom regions
        self.populate_region_performance()

        self.stdout.write("AllRegionsStockPerformance table successfully populated in three stages.")

    def populate_custom_regions(self):
        # Fetch unique custom regions without duplicates
        unique_regions = Equity_Tickers.objects.values_list('custom_region', flat=True).distinct()

        for custom_region in unique_regions:
            if not custom_region:
                continue

            # Create or update entry in AllRegionsStockPerformance for each custom region
            AllRegionsStockPerformance.objects.update_or_create(
                custom_region_name=custom_region,
                defaults={
                    'asset_class': "Equity Basket",
                }
            )

        self.stdout.write("AllRegionsStockPerformance table populated with unique custom regions and asset class set.")

    def populate_individual_tickers(self):
        tickers = Equity_Tickers.objects.filter(ticker__isnull=False, country__isnull=True).exclude(ticker='')

        for ticker_entry in tickers:
            region = ticker_entry.region
            custom_region = ticker_entry.custom_region

            latest_data = DailyPrice.objects.filter(ticker=ticker_entry.ticker).order_by('-date').values_list('adj_close', 'fetch_date').first()
            latest_price, fetch_date = latest_data if latest_data else (None, None)

            d_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=1)
            w_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=7)
            m_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=30)
            y_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=365)
            decade_performance = self.calculate_performance(ticker_entry.ticker, latest_price, days=3650)

            AllRegionsStockPerformance.objects.update_or_create(
                region_name=region,
                custom_region_name=custom_region,
                asset_class=ticker_entry.asset_class,
                ticker=ticker_entry.ticker,
                security_name=ticker_entry.name,
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

    def populate_region_performance(self):
        # Get all unique custom regions from AllRegionsStockPerformance
        regions = AllRegionsStockPerformance.objects.values_list('custom_region_name', flat=True).distinct()

        for region in regions:
            # Skip if no region name is specified
            if not region:
                continue

            # Calculate average performance metrics for the custom region
            performance_data = AllCountriesStockPerformance.objects.filter(custom_region_name=region).aggregate(
                avg_d_performance=Avg('d_performance'),
                avg_w_performance=Avg('w_performance'),
                avg_m_performance=Avg('m_performance'),
                avg_y_performance=Avg('y_performance'),
                avg_decade_performance=Avg('decade_performance'),
                latest_fetch_date=Min('fetch_date')
            )

            # Update the AllRegionsStockPerformance with the calculated averages
            AllRegionsStockPerformance.objects.filter(custom_region_name=region).update(
                d_performance=performance_data['avg_d_performance'],
                w_performance=performance_data['avg_w_performance'],
                m_performance=performance_data['avg_m_performance'],
                y_performance=performance_data['avg_y_performance'],
                decade_performance=performance_data['avg_decade_performance'],
                fetch_date=performance_data['latest_fetch_date']
            )

        self.stdout.write("AllRegionsStockPerformance table updated with calculated average performances for each custom region.")

    def calculate_performance(self, ticker, latest_price, days):
        if latest_price is None:
            return None
        
        latest_price_entry = DailyPrice.objects.filter(ticker=ticker).order_by('-date').first()
        latest_price_date = latest_price_entry.date if latest_price_entry else None

        if not latest_price_date:
            return None

        target_date = latest_price_date - timedelta(days=days)
        target_price = DailyPrice.objects.filter(ticker=ticker, date__lte=target_date).order_by('-date').values_list('adj_close', flat=True).first()

        if target_price:
            return ((latest_price - target_price) / target_price) * 100
        else:
            return None
