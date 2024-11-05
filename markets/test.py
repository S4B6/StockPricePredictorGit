import yfinance as yf

# Define the S&P 500 Index ticker
list = ["^SPX", "^GSPC"]
for a in list:
    sp500 = yf.Ticker(a)
    print(sp500.info)