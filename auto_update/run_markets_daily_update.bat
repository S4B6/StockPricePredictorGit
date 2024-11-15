@echo off
cd "C:\Users\goatm\Desktop\Stock Price Predictor\StockPricePredictorGit\auto_update"

REM Activate the virtual environment
call "C:\Users\goatm\Desktop\Stock Price Predictor\StockPricePredictorGit\venv\Scripts\activate.bat"

REM Run the Python script
python markets_daily_update.py

deactivate

