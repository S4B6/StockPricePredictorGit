import os
import pandas as pd
import yfinance as yf
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from markets.models import Equity_Tickers, Bond_Tickers, Forex_Tickers, Cryptocurrency_Tickers, Commodity_Tickers

# Suppress yfinance logging for errors and warnings
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

class Command(BaseCommand):
    help = 'Updates the ticker tables with the latest information (from a CSV file + yfinance)'

    def handle(self, *args, **kwargs):
        # Define the file paths
        file_paths = {
            'bond': os.path.join(settings.BASE_DIR, 'markets', 'tickers', 'bond_export.csv'),
            'commodity': os.path.join(settings.BASE_DIR, 'markets', 'tickers', 'commodity_export.csv'),
            'cryptocurrency': os.path.join(settings.BASE_DIR, 'markets', 'tickers', 'cryptocurrency_export.csv'),
            'equity': os.path.join(settings.BASE_DIR, 'markets', 'tickers', 'equity_export.csv'),
            'forex': os.path.join(settings.BASE_DIR, 'markets', 'tickers', 'forex_export.csv'),
        }

        # Process each file and populate the database
        for model_name, file_path in file_paths.items():
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                self.stdout.write(f"Processing {file_name}")
                
                # Load the data and fill NaN with None
                data = pd.read_csv(file_path, encoding='ISO-8859-1')
                data = data.where(pd.notnull(data), None)

                if model_name == 'equity':
                    for _, row in data.iterrows():
                        Equity_Tickers.objects.update_or_create(
                            asset_class=row.get('asset_class'),
                            name=row.get('name'),  # Use asset_class and name as the unique identifiers
                            defaults={
                                'asset_class': row.get('asset_class'),
                                'ticker': row.get('ticker'),
                                'name': row.get('name'),
                                'name_from_source': row.get('name_from_source', ''),
                                'country': row.get('country'),
                                'region': row.get('region'),
                                'sub_region': row.get('sub_region'),
                                'custom_region': row.get('custom_region'),
                                'constituents_count': row.get('constituents_count') if pd.notnull(row.get('constituents_count')) else None,
                                'market_cap': row.get('market_cap'),
                                'source': row.get('source', '')
                            }
                        )

                elif model_name == 'bond':
                    for _, row in data.iterrows():
                        Bond_Tickers.objects.update_or_create(
                            asset_class=row.get('asset_class'),
                            name=row.get('name'),  # Use asset_class and name as the unique identifiers
                            defaults={
                                'asset_class': row.get('asset_class'),
                                'ticker': row.get('ticker'),
                                'name': row.get('name'),
                                'name_from_source': row.get('name_from_source', ''),
                                'country': row.get('country'),
                                'region': row.get('region'),
                                'custom_region': row.get('custom_region'),
                                'economic_power_region': row.get('economic_power_region'),
                                'issuer_type': row.get('issuer_type'),
                                'maturity': row.get('maturity') if pd.notnull(row.get('maturity')) else None,
                                'credit_quality': row.get('credit_quality'),
                                'source': row.get('source', '')
                            }
                        )

                elif model_name == 'forex':
                    for _, row in data.iterrows():
                        Forex_Tickers.objects.update_or_create(
                            asset_class=row.get('asset_class'),
                            name=row.get('name'),  # Use asset_class and name as the unique identifiers
                            defaults={
                                'asset_class': row.get('asset_class'),
                                'ticker': row.get('ticker'),
                                'name': row.get('name'),
                                'name_from_source': row.get('name_from_source', ''),
                                'domestic_country_or_region': row.get('domestic_country_or_region'),
                                'foreign_country_or_region': row.get('foreign_country_or_region'),
                                'source': row.get('source', '')
                            }
                        )

                elif model_name == 'cryptocurrency':
                    for _, row in data.iterrows():
                        Cryptocurrency_Tickers.objects.update_or_create(
                            asset_class=row.get('asset_class'),
                            name=row.get('name'),  # Use asset_class and name as the unique identifiers
                            defaults={
                                'asset_class': row.get('asset_class'),
                                'ticker': row.get('ticker'),
                                'name': row.get('name'),
                                'name_from_source': row.get('name_from_source', ''),
                                'token_category': row.get('token_category'),
                                'source': row.get('source', '')
                            }
                        )

                elif model_name == 'commodity':
                    for _, row in data.iterrows():
                        Commodity_Tickers.objects.update_or_create(
                            asset_class=row.get('asset_class'),
                            name=row.get('name'),  # Use asset_class and name as the unique identifiers
                            defaults={
                                'asset_class': row.get('asset_class'),
                                'ticker': row.get('ticker'),
                                'commodity_category': row.get('commodity_category'),
                                'commodity_subtype': row.get('commodity_subtype'),
                                'name': row.get('name'),
                                'name_from_source': row.get('name_from_source', ''),
                                'source': row.get('source', '')
                            }
                        )

                # Populate name_from_source for each model
                self.populate_name_from_source(model_name)

            else:
                self.stdout.write(f"File {file_path} not found.")

        # Print a success message if everything went smoothly
        self.stdout.write("All files processed successfully and database updated.")

    def populate_name_from_source(self, model_name):
        # Dictionary mapping model names to actual models
        model_mapping = {
            'equity': Equity_Tickers,
            'bond': Bond_Tickers,
            'forex': Forex_Tickers,
            'cryptocurrency': Cryptocurrency_Tickers,
            'commodity': Commodity_Tickers,
        }

        model = model_mapping.get(model_name)
        if model:
            instances = model.objects.all()

            for instance in instances:
                if instance.ticker:
                    # Attempt to fetch data from yfinance
                    ticker_data = yf.Ticker(instance.ticker)
                    info = ticker_data.info

                    # Get the name from source
                    name_from_source = info.get('longName') or info.get('shortName')
                    
                    # Only proceed if name_from_source is found
                    if name_from_source:
                        instance.name_from_source = name_from_source
                        instance.save()
                    else:
                        self.stdout.write(f"No name_from_source found for ticker {instance.ticker}")