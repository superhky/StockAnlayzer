from analyzer import StockAnalyzer

def test_korean_news():
    analyzer = StockAnalyzer()
    ticker = "005930.KS" # Samsung Electronics
    print(f"Testing fetch_news for {ticker}...")
    
    news = analyzer.fetch_news(ticker)
    
    if not news:
        print("FAILED: No news returned.")
    else:
        print(f"SUCCESS: Found {len(news)} items.")
        for item in news:
            print(f"- {item['title']} ({item['link']})")

if __name__ == "__main__":
    test_korean_news()
