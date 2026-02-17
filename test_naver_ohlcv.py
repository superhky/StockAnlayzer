import requests
from bs4 import BeautifulSoup
import re

def get_naver_ohlcv(ticker):
    code = ticker.replace('.KS', '').replace('.KQ', '')
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Use the hidden definition list which contains accessibility text
        dl = soup.select_one('dl.blind')
        if not dl:
            return None
            
        data = {}
        text = dl.get_text()
        
        # Extract using regex is safest or string splitting
        # The text usually looks like:
        # 2026년 02월 02일 16시 10분 기준 장마감
        # 종목명 삼성전자
        # ...
        # 현재가 150,400 ...
        # 시가 155,700
        # ...
        
        # Helper to extract value after key
        def extract_value(key, text):
            # Match "Key Value" where value can contain commas
            pattern = rf"{key}\s+([\d,]+)"
            match = re.search(pattern, text)
            if match:
                return match.group(1).replace(',', '')
            return None
            
        data['Close'] = extract_value("현재가", text)
        data['Open'] = extract_value("시가", text)
        data['High'] = extract_value("고가", text)
        data['Low'] = extract_value("저가", text)
        data['Volume'] = extract_value("거래량", text)
        
        # Ensure all are found
        if all(k in data and data[k] for k in ['Close', 'Open', 'High', 'Low', 'Volume']):
             return data
        
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

ticker = "005930.KS"
print(f"Fetching OHLCV for {ticker}...")
data = get_naver_ohlcv(ticker)
print(data)
