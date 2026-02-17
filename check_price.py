import yfinance as yf
from datetime import datetime

ticker = "005930.KS"
print(f"Checking data for {ticker} at {datetime.now()}")

stock = yf.Ticker(ticker)
df = stock.history(period="5d")

print(df.tail())
print(f"\nLast Date: {df.index[-1]}")
