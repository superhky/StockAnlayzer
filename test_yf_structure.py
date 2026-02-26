import yfinance as yf
import json

stock = yf.Ticker("AAPL")
raw_news = stock.news
print(json.dumps(raw_news[:1], indent=2))
