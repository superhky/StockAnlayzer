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
                prompt = f"Find the stock ticker for company '{name}'. Respond ONLY with the ticker symbol (e.g. 005930.KS or AAPL)."
                
                # Intelligent model discovery
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                except:
                    available_models = ['models/gemini-1.5-flash', 'models/gemini-pro']
                
                # Try discovery-based models first, prioritizing flash
                priority_list = [am for am in available_models if '1.5-flash' in am] + \
                                [am for am in available_models if 'pro' in am] + \
                                available_models
                
                for model_name in priority_list:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        ticker = response.text.strip()
                        if ticker and len(ticker) <= 15: return ticker
                        break
                    except:
                        continue
            except: pass
        return name

    def get_company_name(self, ticker):
        """Returns the company name for a given ticker."""
        if ticker.endswith(('.KS', '.KQ')):
            try:
                code = ticker.replace('.KS', '').replace('.KQ', '')
                url = f"https://finance.naver.com/item/main.naver?code={code}"
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                # Naver Finance has the company name in the 'wrap_company' div or meta tags
                name_tag = soup.select_one('.wrap_company h2 a')
                if name_tag:
                    return name_tag.get_text(strip=True)
            except: pass
        
        try:
            stock = yf.Ticker(ticker)
            # Try to get shortName or longName from yfinance
            info = stock.info
            return info.get('shortName') or info.get('longName') or ticker
        except:
            return ticker

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
        """미국 주식 뉴스는 직접 링크를 제공하는 Yahoo Finance를 우선 사용하고, 한국 주식은 네이버를 사용합니다."""
        if ticker.endswith(('.KS', '.KQ')):
            return self._fetch_naver_news(ticker)
        
        # 1. Yahoo Finance (Primary for US - Direct links)
        try:
            stock = yf.Ticker(ticker)
            raw_news = stock.news
            processed_news = []
            for item in (raw_news or []):
                # Handle different yfinance news structures
                content = item.get('content', {})
                title = item.get('title') or content.get('title')
                
                # Try multiple possible link locations
                link = item.get('link') or item.get('url')
                if not link:
                    link = content.get('canonicalUrl', {}).get('url')
                if not link:
                    link = content.get('clickThroughUrl', {}).get('url')
                
                if title and link:
                    title = title.replace('[', '(').replace(']', ')').strip()
                    processed_news.append({'title': title, 'link': link})
                
                if len(processed_news) >= 5:
                    break
            
            if processed_news:
                return processed_news
        except Exception as e:
            print(f"Yahoo Finance news error: {e}")

        # 2. Google News RSS (Fallback)
        try:
            clean_ticker = ticker.split('.')[0]
            search_query = f"{clean_ticker} stock"
            url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, 'xml')
            items = soup.find_all('item')
            processed_news = []
            
            for item in items[:5]:
                title = item.title.text if item.title else '주요 뉴스'
                link = item.link.text if item.link else None
                if title and link:
                    title = title.replace('[', '(').replace(']', ')').strip()
                    processed_news.append({'title': title, 'link': link})
            return processed_news
        except Exception as e:
            print(f"Google News error: {e}")
            return []

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'https://finance.naver.com/item/news.naver?code={code}'
        }
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

    def generate_ai_analysis(self, ticker, price_info, technicals, news, api_key, avg_purchase_price=None, language='Korean'):
        if not api_key: return "API Key is required."
        try:
            genai.configure(api_key=api_key)
            
            purchase_context = f"The user's average purchase price is {avg_purchase_price}." if avg_purchase_price else "The user does not currently hold this stock."
            
            prompt = f"""
            You are a professional stock analyst. Analyze the stock '{ticker}' based on the provided data and provide a structured report in {language}.

            [Data Provided]
            - Price Info: {price_info}
            - Technical Indicators: {technicals}
            - Latest News: {news}
            - Context: {purchase_context}

            [Report Requirements]
            1. **Technical Analysis Summary**: Briefly interpret the RSI, MACD, and Bollinger Bands.
            2. **News Sentiment Analysis**: Summarize the impact of recent news on the stock's future.
            3. **Short-term Strategy (1-4 weeks)**: Provide a specific action plan (Buy/Hold/Sell) with target price and stop-loss.
            4. **Long-term Strategy (6 months+)**: Provide a fundamental outlook and growth potential.
            5. **Final Investment Conclusion**: A concise summary including risk factors.

            Ensure the tone is professional, objective, and data-driven.
            """
            
            # 1. Try to discover available models for this specific API key
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
            except Exception as list_err:
                # If listing fails, fall back to a safer hardcoded list
                available_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
            
            # 2. Prioritize best models
            # We look for 1.5-flash, then 1.5-pro, then any gemini model
            priority_list = []
            for target in ['1.5-flash', '1.5-pro', 'gemini-pro', '1.0-pro']:
                for am in available_models:
                    if target in am:
                        priority_list.append(am)
                        break
            
            # Add remaining models just in case
            for am in available_models:
                if am not in priority_list:
                    priority_list.append(am)

            # 3. Try to generate content with the best available model
            last_error = "No models found"
            for model_name in priority_list:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as e:
                    last_error = str(e)
                    continue # Try next available model
            
            return f"AI Analysis Error: Could not find or access a compatible Gemini model. (Last Error: {last_error}). Please ensure your API key has 'Generative Language API' enabled in Google Cloud Console."
        except Exception as e:
            return f"AI Config Error: {str(e)}"

if __name__ == "__main__":
    analyzer = StockAnalyzer()
    print(analyzer.fetch_news("AAPL"))
