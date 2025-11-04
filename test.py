import yfinance as yf

t = yf.Ticker("^IRX")

# Just print all available info
print(t.info)