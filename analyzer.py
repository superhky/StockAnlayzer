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

class StockAnalyzer:
    def __init__(self):
        pass

    def get_ticker(self, name, api_key=None):
        """
        Attempts to convert a company name to a ticker with AI fallback.
        """
        name = name.strip()
        
        # 1. If it's 6 digits, assume KR stock
        if name.isdigit() and len(name) == 6:
            return f"{name}.KS"
        
        # 2. If it's already a ticker format
        if "." in name or (name.isupper() and 1 <= len(name) <= 5):
            return name

        # 3. Detect Korean characters
        is_korean = bool(re.search('[가-힣]', name))

        # 4. Use yfinance search
        try:
            search = yf.Search(name, max_results=5)
            if search.quotes:
                if is_korean:
                    for quote in search.quotes:
                        if quote['symbol'].endswith(('.KS', '.KQ')):
                            return quote['symbol']
                return search.quotes[0]['symbol']
        except Exception:
            pass

        # 5. AI Fallback (If API key provided)
        if api_key and len(name) > 1:
            try:
                genai.configure(api_key=api_key)
                # Use a fast model for this
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Find the stock ticker for company '{name}'. Respond ONLY with the ticker symbol (e.g. 005930.KS or AAPL). If it's a Korean company, ensure it ends with .KS or .KQ."
                response = model.generate_content(prompt)
                ticker = response.text.strip()
                if ticker and len(ticker) <= 10:
                    return ticker
            except Exception:
                pass
            
        return name

    def fetch_data(self, ticker, period="1y"):
        """Fetches historical price data using yfinance, patched with Naver for KR stocks."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            # Patch with Naver Real-time/Latest data for Korean stocks
            if ticker.endswith(('.KS', '.KQ')):
                try:
                    naver_data = self._fetch_naver_price(ticker)
                    if naver_data:
                        # Prepare Naver data row
                        
                        tz = pytz.timezone('Asia/Seoul')
                        now = datetime.now(tz)
                        # Normalize to midnight for daily bars usually, implies 'today'
                        # But if we want to update the last bar which might be today:
                        today_ts = pd.Timestamp(now.date(), tz='Asia/Seoul')
                        
                        # Convert data to floats
                        close = float(naver_data['Close'])
                        open_p = float(naver_data['Open'])
                        high = float(naver_data['High'])
                        low = float(naver_data['Low'])
                        vol = int(naver_data['Volume'])
                        
                        # Check last index
                        if not df.empty:
                            last_date = df.index[-1].normalize() # normalize removes time component
                            today_date = today_ts.normalize()
                            
                            if last_date == today_date:
                                # Update last row
                                df.iloc[-1, df.columns.get_loc('Close')] = close
                                df.iloc[-1, df.columns.get_loc('Open')] = open_p
                                df.iloc[-1, df.columns.get_loc('High')] = high
                                df.iloc[-1, df.columns.get_loc('Low')] = low
                                df.iloc[-1, df.columns.get_loc('Volume')] = vol
                            elif last_date < today_date:
                                # Append new row
                                new_row = pd.DataFrame([{
                                    'Open': open_p, 
                                    'High': high, 
                                    'Low': low, 
                                    'Close': close, 
                                    'Volume': vol,
                                    'Dividends': 0.0,
                                    'Stock Splits': 0.0
                                }], index=[today_ts])
                                df = pd.concat([df, new_row])
                        else:
                             # If empty, create new
                            df = pd.DataFrame([{
                                'Open': open_p, 
                                'High': high, 
                                'Low': low, 
                                'Close': close, 
                                'Volume': vol,
                                'Dividends': 0.0,
                                'Stock Splits': 0.0
                            }], index=[today_ts])

                except Exception as e:
                    print(f"Naver patch failed: {e}")
                    # Continue with yfinance data
                    pass

            if df.empty:
                return None, f"No data found for {ticker}"
            return df, None
        except Exception as e:
            return None, str(e)

    def calculate_indicators(self, df):
        """Calculates RSI, MACD, and Bollinger Bands."""
        if len(df) < 30: # Need enough data for indicators
            return df

        # RSI
        rsi_20 = RSIIndicator(close=df['Close'], window=20)
        df['RSI'] = rsi_20.rsi()

        # MACD
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()

        # Bollinger Bands
        bb = BollingerBands(close=df['Close'])
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Mid'] = bb.bollinger_mavg()

        return df

    def fetch_news(self, ticker):
        """Fetches latest news for the ticker and flattens the structure."""
        # Check if it's a Korean stock
        if ticker.endswith(('.KS', '.KQ')):
            return self._fetch_naver_news(ticker)

        try:
            stock = yf.Ticker(ticker)
            raw_news = stock.news
            
            if not raw_news:
                # Fallback: Search news using ticker name if the direct attribute is empty
                try:
                    search = yf.Search(ticker, max_results=5)
                    raw_news = search.news
                except:
                    pass

            processed_news = []
            for item in raw_news[:5]:
                content = item.get('content', item)
                title = content.get('title') or content.get('heading') or item.get('title', 'No Title')
                link = content.get('link') or content.get('url') or item.get('link', '#')
                
                if title != 'No Title':
                    processed_news.append({
                        'title': title,
                        'link': link
                    })
            
            return processed_news
        except Exception as e:
            return []

    def _fetch_naver_price(self, ticker):
        """Fetches OHLCV from Naver Finance."""
        try:
            code = ticker.replace('.KS', '').replace('.KQ', '')
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            dl = soup.select_one('dl.blind')
            if not dl:
                return None
                
            text = dl.get_text()
            
            def extract_value(key, text):
                pattern = rf"{key}\s+([\d,]+)"
                match = re.search(pattern, text)
                if match:
                    return match.group(1).replace(',', '')
                return None
                
            data = {}
            data['Close'] = extract_value("현재가", text)
            data['Open'] = extract_value("시가", text)
            data['High'] = extract_value("고가", text)
            data['Low'] = extract_value("저가", text)
            data['Volume'] = extract_value("거래량", text)
            
            if all(k in data and data[k] for k in ['Close', 'Open', 'High', 'Low', 'Volume']):
                return data
            return None
        except Exception:
            return None

    def _fetch_naver_news(self, ticker):
        """Fetches news from Naver Finance for Korean stocks."""
        code = ticker.replace('.KS', '').replace('.KQ', '')
        url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'https://finance.naver.com/item/news.naver?code={code}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = soup.select('td.title a')
            
            news_items = []
            for title in titles:
                news_title = title.get_text(strip=True)
                link = title['href']
                if not link.startswith('http'):
                    link = f"https://finance.naver.com{link}"
                
                news_items.append({
                    'title': news_title,
                    'link': link
                })
                if len(news_items) >= 5:
                    break
            
            return news_items
        except Exception as e:
            print(f"Error fetching Naver news: {e}")
            return []

    def generate_ai_analysis(self, ticker, price_info, technicals, news, api_key, avg_purchase_price=None):
        """Generates AI strategy using Google Gemini."""
        if not api_key:
            return "API Key is required for AI analysis."

        try:
            genai.configure(api_key=api_key)
            
            # Dynamically find an available model
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                model_name = None
                for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                    if preferred in available_models:
                        model_name = preferred
                        break
                
                if not model_name and available_models:
                    model_name = available_models[0]
                
                if not model_name:
                    return "사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키 권한을 확인해 주세요."
                
                model = genai.GenerativeModel(model_name)
            except Exception as e:
                return f"Model Discovery Error: {str(e)}. (Hint: Is your API key correct?)"

            purchase_context = f"평균 매수 가격: {avg_purchase_price}" if avg_purchase_price else "매수 전 상태 (신규 진입 고려)"
            
            prompt = f"""
            Analyze the following stock: {ticker}
            Current Price Info: {price_info}
            Investment Context: {purchase_context}
            Technical Indicators: {technicals}
            Latest News Summaries: {news}
            
            Based on this information, provide:
            1. Short-term trading strategy (1-4 weeks) including a specific **Target Price**.
            2. Long-term trading strategy (6 months+) including a specific **Target Price**.
            3. Overall recommendation (Buy/Hold/Sell/Add/Trim) with reasoning, CONSIDERING the investor's current purchase price.
               - If the current price is higher than the purchase price, suggest profit-taking levels.
               - If lower, suggest stop-loss or averaging down strategies.
            
            Respond in Korean. Ensure the "Target Price" is clearly visible for each strategy.
            """
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Analysis Error: {str(e)}"

# Example usage/test
if __name__ == "__main__":
    analyzer = StockAnalyzer()
    df, err = analyzer.fetch_data("AAPL")
    if df is not None:
        df = analyzer.calculate_indicators(df)
        print(df.tail())
