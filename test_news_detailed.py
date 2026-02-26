import yfinance as yf
import requests
from bs4 import BeautifulSoup
from analyzer import StockAnalyzer

analyzer = StockAnalyzer()

def test_us_news_detailed(ticker):
    print(f"=== Testing Detailed US News for {ticker} ===")
    
    print("--- 1. Testing yfinance ---")
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news
        if raw_news:
            print(f"Found {len(raw_news)} items via yfinance")
            for item in raw_news[:2]:
                title = item.get('title')
                print(f"  - {title}")
        else:
            print("No news found via yfinance")
    except Exception as e:
        print(f"yfinance error: {e}")

    print("--- 2. Testing Google News RSS ---")
    try:
        clean_ticker = ticker.split('.')[0]
        search_query = f"{clean_ticker} stock"
        url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        print(f"Response status: {res.status_code}")
        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.find_all('item')
        print(f"Found {len(items)} items via Google News")
        for item in items[:2]:
            title = item.title.text if item.title else 'No Title'
            print(f"  - {title}")
    except Exception as e:
        print(f"Google News error: {e}")

    print("--- 3. Testing analyzer.fetch_news() ---")
    news = analyzer.fetch_news(ticker)
    print(f"Final result: {len(news)} items found")

test_us_news_detailed("AAPL")
