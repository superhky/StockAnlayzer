from analyzer import StockAnalyzer

analyzer = StockAnalyzer()

print("--- Testing US News (AAPL) ---")
us_news = analyzer.fetch_news("AAPL")
for item in us_news:
    print(f"- {item['title']}")

print("\n--- Testing KR News (005930.KS) ---")
kr_news = analyzer.fetch_news("005930.KS")
for item in kr_news:
    print(f"- {item['title']}")
