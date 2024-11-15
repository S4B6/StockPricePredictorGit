import yfinance as yf
import pandas as pd
from datetime import timedelta
from django.core.management.base import BaseCommand
from markets.models import DailyPrice, Equity_Tickers, Bond_Tickers, Forex_Tickers, Cryptocurrency_Tickers, Commodity_Tickers
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate the DailyPrice table with historical price data from yfinance'

    def handle(self, *args, **kwargs):
        asset_class_models = {
            'equity': Equity_Tickers,
            'bond': Bond_Tickers,
            'forex': Forex_Tickers,
            'cryptocurrency': Cryptocurrency_Tickers,
            'commodity': Commodity_Tickers,
        }

        not_found_tickers = []

        for asset_class, model in asset_class_models.items():
            self.stdout.write(f"Processing {asset_class} tickers")
            tickers = model.objects.values_list('ticker', 'name')

            for ticker, name in tickers:
                if ticker:
                    if not self.fetch_and_save_daily_price_data(ticker, name, asset_class):
                        not_found_tickers.append({'ticker': ticker, 'name': name, 'asset_class': asset_class})

        if not_found_tickers:
            self.stdout.write("Tickers not found or encountered errors:")
            for ticker_info in not_found_tickers:
                self.stdout.write(f"{ticker_info['ticker']} - {ticker_info['name']} ({ticker_info['asset_class']})")
        else:
            self.stdout.write("All tickers processed successfully without errors.")

    def fetch_and_save_daily_price_data(self, ticker, name, asset_class):
        try:
            # Find the latest date available for this ticker in the database
            last_entry = DailyPrice.objects.filter(ticker=ticker, asset_class=asset_class).order_by('-date').first()
            
            # If data exists, set start date as three days before the last entry
            # If no data exists, set a default start date
            start_date = (last_entry.date - timedelta(days=3)) if last_entry else "2000-01-01"

            # Fetch new data from start_date to today
            data = yf.download(ticker, start=start_date, progress=False)

            # Check if data is empty, meaning no data was found for the ticker
            if data.empty:
                return False  # No data found for this ticker

            # Capture the current timestamp once per batch
            fetch_timestamp = timezone.now()

            # Use `iloc` to access columns by index position
            for i in range(len(data)):
                row = data.iloc[i]
                date = data.index[i].date()  # Convert timestamp index to date

                # Using `iloc` with assumed column indices:
                # 0: Adj Close, 1: Close, 2: High, 3: Low, 4: Open, 5: Volume
                DailyPrice.objects.update_or_create(
                    date=date,
                    asset_class=asset_class,
                    ticker=ticker,
                    defaults={
                        'name': name,
                        'open': float(row.iloc[4]) if pd.notna(row.iloc[4]) else None,  # Open
                        'high': float(row.iloc[2]) if pd.notna(row.iloc[2]) else None,  # High
                        'low': float(row.iloc[3]) if pd.notna(row.iloc[3]) else None,   # Low
                        'adj_close': float(row.iloc[0]) if pd.notna(row.iloc[0]) else None, # Adj Close
                        'volume': int(row.iloc[5]) if pd.notna(row.iloc[5]) else None, # Volume
                        'fetch_date': fetch_timestamp  # Update with the current timestamp
                    }
                )
            return True  # Data was successfully found and processed    

        except Exception as e:
            self.stdout.write(f"Error fetching data for ticker {ticker} ({asset_class}): {e}")
            return False  # Return False on error