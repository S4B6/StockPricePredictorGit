# markets/management/commands/fetch_data.py
import yfinance as yf
import pandas as pd  # Ensure pandas is imported to use pd.isna
from django.core.management.base import BaseCommand
from markets.models import Asset, DailyPrice  # Ensure this matches your actual app path
from decimal import Decimal

class Command(BaseCommand):
    help = 'Fetches and stores data for specified assets'

    def handle(self, *args, **options):
        # Define the asset classes and assets to fetch
        asset_classes = {
            "Equity Index": [
                {
                    "symbol": "^GSPC",
                    "country": "United States",
                    "constituents_count": 500,
                    "market_cap_coverage": Decimal("80.00"),
                    "currency": "USD"
                },
                {
                    "symbol": "^GSPTSE",
                    "country": "Canada",
                    "constituents_count": 200,
                    "market_cap_coverage": Decimal("70.00"),
                    "currency": "CAD"
                },
                {
                    "symbol": "^MXX",
                    "country": "Mexico",
                    "constituents_count": 35,
                    "market_cap_coverage": None,
                    "currency": "MXN"
                },
                {
                    "symbol": "^BVSP",
                    "country": "Brazil",
                    "constituents_count": 80,
                    "market_cap_coverage": Decimal("70.00"),
                    "currency": "BRL"
                },

                {
                    "symbol": "^IPSA",
                    "country": "Chile",
                    "constituents_count": 28,
                    "market_cap_coverage": None,
                    "currency": "CLP"
                },
                {
                    "symbol": "^MERV",
                    "country": "Argentina",
                    "constituents_count": 22,
                    "market_cap_coverage": None,
                    "currency": "ARS"
                },
            ]
        }

        missing_symbols = []

        # Iterate over each asset class and symbol to fetch data and store it
        for asset_class, assets in asset_classes.items():
            for asset_info in assets:
                # Fetch data from yfinance
                ticker = yf.Ticker(asset_info["symbol"])
                data = yf.download(asset_info["symbol"], start="2020-01-01")  # Adjust the date range as needed
                short_name = ticker.info.get('shortName')  # Get short name
                if data.empty:
                    print(f"No data found for ({asset_info['symbol']}). Skipping.")
                    missing_symbols.append(asset_info["symbol"])
                    continue

                # Create or update the asset entry
                asset, created = Asset.objects.update_or_create(
                    symbol=asset_info["symbol"],
                    defaults={
                        "name": short_name,  # Use the short name from Yahoo Finance
                        "asset_class": asset_class,
                        "country": asset_info["country"],
                        "constituents_count": asset_info["constituents_count"],
                        "market_cap_coverage": asset_info["market_cap_coverage"],
                        "currency": asset_info["currency"]
                    }
                )

                # Store OHLCV data in the database using iloc for specific elements
                for i in range(len(data)):
                    row = data.iloc[i]
                    date = data.index[i]

                    # Extract OHLCV data using iloc with specific indices
                    open_price = float(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                    high_price = float(row.iloc[1]) if pd.notna(row.iloc[1]) else None
                    low_price = float(row.iloc[2]) if pd.notna(row.iloc[2]) else None
                    close_price = float(row.iloc[3]) if pd.notna(row.iloc[3]) else None
                    volume = int(row.iloc[4]) if pd.notna(row.iloc[4]) else None

                    # Update or create the DailyPrice entry
                    DailyPrice.objects.update_or_create(
                        asset=asset,
                        date=date,
                        defaults={
                            'symbol': asset.symbol,
                            'open': open_price,
                            'high': high_price,
                            'low': low_price,
                            'adj_close': close_price,
                            'volume': volume,
                        }
                    )
        if missing_symbols:
            print("The following symbols were not found:")
            for symbol in missing_symbols:
                print(symbol)
        self.stdout.write(self.style.SUCCESS("Data fetching and storing completed successfully!"))

