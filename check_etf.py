import yfinance as yf
import requests
from bs4 import BeautifulSoup

def get_naver_price(ticker):
    code = ticker.replace('.KS', '').replace('.KQ', '')
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        no_today = soup.select_one('.no_today')
        if no_today:
            price_span = no_today.select_one('.blind')
            if price_span:
                return price_span.get_text(strip=True).replace(',', '')
        return None
    except Exception as e:
        print(f"Error scraping Naver: {e}")
        return None

ticker = "069500.KS" # KODEX 200
print(f"Checking {ticker}...")

# YFinance
stock = yf.Ticker(ticker)
hist = stock.history(period="5d")
yf_price = hist['Close'].iloc[-1]
yf_date = hist.index[-1]

print(f"YFinance Date: {yf_date}")
print(f"YFinance Close: {yf_price}")

# Naver
nav_price = get_naver_price(ticker)
print(f"Naver Price: {nav_price}")

if nav_price:
    diff = float(nav_price) - yf_price
    print(f"Difference: {diff}")
else:
    print("Could not fetch Naver price")
