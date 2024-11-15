import yfinance as yf
import pandas as pd
from datetime import datetime

# Define the list of tickers
tickers = ["ROX.F", "^FCHI", "^GSPC", "^OMXC25", "^FTSE"]

# Set start and end dates
start_date = "2000-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")  # Today's date

# Create a dictionary to store each ticker's data
data_dict = {}

for ticker in tickers:
    # Download data using yf.download with an explicit end date
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    # Check if today's data is missing
    if end_date not in data.index.strftime('%Y-%m-%d'):
        print(f"Warning: Today's data is missing for ticker {ticker}")

    # Store data in the dictionary
    data_dict[ticker] = data

# Create a new Excel writer object
with pd.ExcelWriter("stock_data_multiple_tickers2.xlsx") as writer:
    for ticker, data in data_dict.items():
        # Write each ticker's data to a separate sheet in the Excel file
        data.to_excel(writer, sheet_name=ticker)

print("Data has been downloaded and saved to stock_data_multiple_tickers2.xlsx")

print(data)