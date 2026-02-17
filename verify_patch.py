from analyzer import StockAnalyzer
import time

analyzer = StockAnalyzer()
ticker = "005930.KS"

print(f"Fetching data for {ticker}...")
df, err = analyzer.fetch_data(ticker)

if err:
    print(f"Error: {err}")
else:
    last_row = df.iloc[-1]
    last_date = df.index[-1]
    print(f"Last Date: {last_date}")
    print(f"Last Close: {last_row['Close']}")
    print(f"Last Vol: {last_row['Volume']}")
    print("-" * 20)
    print(df.tail())

print("\nVerifying if this matches Naver real-time...")
naver_data = analyzer._fetch_naver_price(ticker)
if naver_data:
    print(f"Naver Close: {naver_data['Close']}")
    
    if float(naver_data['Close']) == last_row['Close']:
        print("SUCCESS: Data matches Naver source.")
    else:
        print("WARNING: Mismatch! (This implies patching might have failed or yfinance overwrote incorrectly??)")
        # Note: If yfinance updated since my last check and differs slightly from Naver (unlikely for closed market), this might trigger.
else:
    print("Could not fetch Naver data for comparison.")
