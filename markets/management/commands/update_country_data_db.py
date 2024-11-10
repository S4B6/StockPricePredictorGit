import os
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from markets.models import CountryData  # Make sure this model exists
from decimal import Decimal

class Command(BaseCommand):
    help = 'Updates the CountryData table with the latest information'

    def handle(self, *args, **kwargs):
        # Construct the absolute path to the CSV file
        file_path = os.path.join(settings.BASE_DIR, 'markets', 'country_data_export.csv')
        data = pd.read_csv(file_path, encoding='ISO-8859-1')
        
        # Assuming `most_recent_GDP_USD`, `GDP_USD_2023`, `GDP_USD_2022`, and `population_size_2023` are in millions
        data['most_recent_GDP_USD'] = data['most_recent_GDP_USD (m)'] * 1_000_000  # Convert to whole units
        data['GDP_USD_2023'] = data['GDP_USD (2023) (m)'] * 1_000_000
        data['GDP_USD_2022'] = data['GDP_USD (2022) (m)'] * 1_000_000
        data['population_size_2023'] = data['population_size (2023) (m)'] * 1_000_000
        
        # Update the database
        for _, row in data.iterrows():
            # For example, update or create each country
            CountryData.objects.update_or_create(
                country_name=row['country_name'],
                country_second_name = row['country_name_2'],
                defaults={
                    'region': row['region'],
                    'country_code': row['country_code'],
                    'currency': row['currency'],
                    'capital_city': row['capital_city'],
                    'most_recent_GDP_USD': row['most_recent_GDP_USD'],
                    'GDP_USD_2023': row['GDP_USD_2023'],
                    'GDP_USD_2022': row['GDP_USD_2022'],
                    'population_size_2023': row['population_size_2023'],
                }
            )
        self.stdout.write(self.style.SUCCESS("Database updated successfully!"))
