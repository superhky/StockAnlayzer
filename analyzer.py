import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import requests
from bs4 import BeautifulSoup
import os
import re
import google.generativeai as genai
from datetime import datetime
import pytz
import json

class StockAnalyzer:
    def __init__(self):
        pass

    def get_ticker(self, name, api_key=None):
        """Attempts to convert a company name to a ticker with AI fallback."""
        name = name.strip()
        if name.isdigit() and len(name) == 6:
            return f"{name}.KS"
        if "." in name or (name.isupper() and 1 <= len(name) <= 5):
            return name
        is_korean = bool(re.search('[가-힣]', name))
        try:
            search = yf.Search(name, max_results=5)
            if search.quotes:
                if is_korean:
                    for quote in search.quotes:
                        if quote['symbol'].endswith(('.KS', '.KQ')):
                            return quote['symbol']
                return search.quotes[0]['symbol']
        except: pass
        if api_key and len(name) > 1:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Find the stock ticker for company '{name}'. Respond ONLY with the ticker symbol (e.g. 005930.KS or AAPL)."
                response = model.generate_content(prompt)
                ticker = response.text.strip()
                if ticker and len(ticker) <= 10: return ticker
            except: pass
        return name

    def fetch_data(self, ticker, period="1y"):
        """Fetches historical price data using yfinance, patched with Naver for KR stocks."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if ticker.endswith(('.KS', '.KQ')):
                try:
                    naver_data = self._fetch_naver_price(ticker)
                    if naver_data:
                        tz = pytz.timezone('Asia/Seoul')
                        now = datetime.now(tz)
                        today_ts = pd.Timestamp(now.date(), tz='Asia/Seoul')
                        close, open_p, high, low, vol = float(naver_data['Close']), float(naver_data['Open']), float(naver_data['High']), float(naver_data['Low']), int(naver_data['Volume'])
                        if not df.empty:
                            last_date = df.index[-1].normalize()
                            if last_date == today_ts.normalize():
                                df.iloc[-1, df.columns.get_loc('Close')] = close
                                df.iloc[-1, df.columns.get_loc('Open')] = open_p
                                df.iloc[-1, df.columns.get_loc('High')] = high
                                df.iloc[-1, df.columns.get_loc('Low')] = low
                                df.iloc[-1, df.columns.get_loc('Volume')] = vol
                            elif last_date < today_ts.normalize():
                                new_row = pd.DataFrame([{'Open': open_p, 'High': high, 'Low': low, 'Close': close, 'Volume': vol, 'Dividends': 0.0, 'Stock Splits': 0.0}], index=[today_ts])
                                df = pd.concat([df, new_row])
                except: pass
            if df.empty: return None, f"No data found for {ticker}"
            return df, None
        except Exception as e: return None, str(e)

    def calculate_indicators(self, df):
        """Calculates RSI, MACD, and Bollinger Bands."""
        if len(df) < 30: return df
        df['RSI'] = RSIIndicator(close=df['Close'], window=20).rsi()
        macd = MACD(close=df['Close'])
        df['MACD'], df['MACD_Signal'], df['MACD_Diff'] = macd.macd(), macd.macd_signal(), macd.macd_diff()
        bb = BollingerBands(close=df['Close'])
        df['BB_High'], df['BB_Low'], df['BB_Mid'] = bb.bollinger_hband(), bb.bollinger_lband(), bb.bollinger_mavg()
        return df

    def fetch_news(self, ticker):
        """Google News RSS (Financial Filter)를 사용하여 미국 주식 뉴스를 가장 안정적으로 가져옵니다."""
        if ticker.endswith(('.KS', '.KQ')):
            return self._fetch_naver_news(ticker)
        
        try:
            # Google News RSS with a more robust search query
            clean_ticker = ticker.split('.')[0]
            search_query = f"{clean_ticker} stock"
            url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            res = requests.get(url, headers=headers, timeout=10)
            
            # Use res.content instead of res.text to let BeautifulSoup handle encoding detection
            soup = BeautifulSoup(res.content, 'xml')
            items = soup.find_all('item')
            processed_news = []
            
            for item in items[:5]:
                title = item.title.text if item.title else '주요 뉴스'
                link = item.link.text if item.link else None
                
                if title and link:
                    # Clean up common encoding issues, curly quotes, and double spaces
                    title = title.replace('\xa0', ' ').replace('', "'").strip()
                    # More thorough cleanup for Windows-1252/UTF-8 mismatches
                    title = title.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
                    processed_news.append({'title': title, 'link': link})
            
            # Fallback if Google News is empty
            if not processed_news:
                return self._fetch_yfinance_news_fallback(ticker)
                
            return processed_news
        except Exception as e:
            print(f"Google News error: {e}")
            return self._fetch_yfinance_news_fallback(ticker)

    def _fetch_yfinance_news_fallback(self, ticker):
        """Backup news source using yfinance with direct link extraction."""
        try:
            stock = yf.Ticker(ticker)
            raw_news = stock.news
            processed_news = []
            for item in (raw_news or [])[:5]:
                content = item.get('content', {})
                title = item.get('title') or content.get('title') or '주요 뉴스'
                link = item.get('link') or item.get('url') or content.get('canonicalUrl', {}).get('url')
                if title:
                    processed_news.append({'title': title, 'link': link})
            return processed_news
        except: return []

    def _fetch_naver_price(self, ticker):
        try:
            code = ticker.replace('.KS', '').replace('.KQ', '')
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            dl = soup.select_one('dl.blind')
            if not dl: return None
            text = dl.get_text()
            def ex(k, t):
                m = re.search(rf"{k}\s+([\d,]+)", t)
                return m.group(1).replace(',', '') if m else None
            data = {k: ex(v, text) for k, v in {'Close': '현재가', 'Open': '시가', 'High': '고가', 'Low': '저가', 'Volume': '거래량'}.items()}
            return data if all(data.values()) else None
        except: return None

    def _fetch_naver_news(self, ticker):
        code = ticker.replace('.KS', '').replace('.KQ', '')
        url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            res = requests.get(url, headers=headers)
            res.encoding = 'euc-kr'
            soup = BeautifulSoup(res.text, 'html.parser')
            news_items = []
            for a in soup.select('td.title a')[:5]:
                link = a['href']
                if not link.startswith('http'): link = f"https://finance.naver.com{link}"
                news_items.append({'title': a.get_text(strip=True), 'link': link})
            return news_items
        except: return []

    def generate_ai_analysis(self, ticker, price_info, technicals, news, api_key, avg_purchase_price=None):
        if not api_key: return "API Key is required."
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Analyze {ticker}. Price: {price_info}, Technicals: {technicals}, News: {news}. Context: {avg_purchase_price}. Respond in Korean."
            return model.generate_content(prompt).text
        except Exception as e: return str(e)

if __name__ == "__main__":
    analyzer = StockAnalyzer()
    print(analyzer.fetch_news("AAPL"))
