import os
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from markets.models import Exchange, Exchange_Holiday


class Command(BaseCommand):
    help = "Import exchanges and holidays from CSV files"

    def handle(self, *args, **kwargs):
        exchanges_path = os.path.join(settings.BASE_DIR, 'markets', 'market data', 'exchanges_export.csv')
        holidays_path = os.path.join(settings.BASE_DIR, 'markets', 'market data', 'holiday_export.csv')

        exchanges = pd.read_csv(exchanges_path, encoding='ISO-8859-1').where(pd.notnull, None)
        holidays = pd.read_csv(holidays_path, encoding='ISO-8859-1').where(pd.notnull, None)

        for _, row in exchanges.iterrows():
            Exchange.objects.update_or_create(
                country=row.get('country'),
                exchange_short_name=row.get('exchange'),
                defaults={
                    'market_open_local': pd.to_datetime(str(row.get('market_open_local'))).time() if row.get('market_open_local') else None,
                    'market_close_local': pd.to_datetime(str(row.get('market_close_local'))).time() if row.get('market_close_local') else None,
                    'timezone': row.get('timezone')
                }
            )

        for _, row in holidays.iterrows():
            Exchange_Holiday.objects.update_or_create(
                date=pd.to_datetime(row.get('date')).date() if row.get('date') else None,
                country=row.get('country'),
                defaults={'holiday_name': row.get('holiday_name')}
            )

        self.stdout.write("Import completed.")
