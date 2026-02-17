import requests

def debug_fetch(ticker):
    code = ticker.replace('.KS', '').replace('.KQ', '')
    url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'https://finance.naver.com/item/news.naver?code={code}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'euc-kr' 
        
        with open('debug_naver.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print("Saved debug_naver.html")

    except Exception as e:
        print(f"Error: {e}")

debug_fetch("005930")
