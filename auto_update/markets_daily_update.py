import os
import django
import sys

# Add the project root to sys.path
sys.path.append("C:/Users/goatm/Desktop/Stock Price Predictor/StockPricePredictorGit")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SPPdjango.settings")
django.setup()

from django.core.management import call_command

call_command("frequent_update_dailyprice_db")  # Replace with your actual management command name
