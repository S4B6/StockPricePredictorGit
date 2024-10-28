import yfinance as yf

def fetch_data(ticker, period="1y"):
    """
    Fetch historical data for the specified ticker.
    """
    data = yf.Ticker(ticker).history(period=period)
    return {
        "date": data.index.strftime('%Y-%m-%d').tolist(),
        "close": data["Close"].tolist(),
    }

def fetch_north_america_data():
    """
    Fetch data for North America (e.g., S&P 500).
    """
    return fetch_data("^GSPC")  # S&P 500 as a representative of North America

def fetch_eastern_europe_data():
    """
    Fetch data for Eastern Europe (placeholder index).
    """
    return fetch_data("^N225")  # Placeholder: Nikkei 225 as a temporary representative
