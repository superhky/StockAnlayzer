import streamlit as st

# Updated to fix news display issue (Feb 25, 2026)
# Page config (MUST be the first Streamlit command)
st.set_page_config(page_title="Pro Stock Analyzer", layout="wide", initial_sidebar_state="expanded")

# Google AdSense Verification (Auto Ads)
st.markdown("""
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8764053427630602" crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

import pandas as pd
import plotly.graph_objects as go
from analyzer import StockAnalyzer

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        border-radius: 5px;
        height: 2.5em;
        background-color: #262730;
        color: white;
        border: 1px solid #4dabf7;
    }
    .stButton>button:hover {
        background-color: #4dabf7;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    .metric-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 AI Stock Analyzer")

# Language Selection
with st.sidebar:
    lang = st.radio("Language / 언어", ["English", "한국어"], index=1, horizontal=True)
    st.divider()

# Translation Dictionary
texts = {
    "English": {
        "subtitle": "Technical Analysis & AI Strategy Report for KR & US Stocks",
        "settings": "Settings",
        "api_key_help": "Get your key from Google AI Studio",
        "api_key_info": "Without an API key, only technical analysis will be performed.",
        "dev_by": "Developed by Antigravity",
        "input_label": "Stock Ticker or Company Name (e.g. 005930, AAPL, Tesla)",
        "input_placeholder": "e.g. AAPL",
        "help_caption": "💡 **Help**: For Korean stocks, enter the **6-digit ticker**. For US stocks, **ticker or company name** is recognized.",
        "purchase_price": "Avg Purchase Price (Unit: KRW or USD)",
        "purchase_price_help": "Enter if you hold the stock. Leave at 0 for new entry.",
        "analyze_btn": "Start Analysis",
        "analyzing": "Analyzing",
        "error": "Error occurred",
        "current_price": "Current Price",
        "rsi": "RSI (20)",
        "macd": "MACD",
        "bb_mid": "BB Mid",
        "overbought": "Overbought",
        "oversold": "Oversold",
        "latest_news": "Latest Major News",
        "news_help": "※ Click title or button on the right to read full article.",
        "view_article": "View Article",
        "all_news_naver": "View All News on Naver Finance",
        "provided_by": "Provided by",
        "ai_report": "🤖 Meta AI Analysis Report",
        "ai_warning": "Enter Gemini API Key in the sidebar to see AI analysis.",
        "start_info": "Enter a stock ticker and press 'Start Analysis'.",
        "features_title": "📈 Key Features",
        "features_list": """
        - **Technical Analysis**: Real-time calculation of RSI, MACD, Bollinger Bands, etc.
        - **Latest News Integration**: Check major news for each stock at a glance.
        - **AI Report**: Custom investment strategy based on news and technical indicators.
        """,
        "how_to_title": "💡 How to Use",
        "how_to_list": """
        1. Enter **Gemini API Key** in the sidebar (Optional).
        2. Enter the **Stock Ticker or Company Name**.
        3. Press **'Start Analysis'** to see the report.
        """,
        "legal": "The information provided is for reference only. Final investment responsibility lies with the user.",
        "privacy": "Privacy Policy",
        "terms": "Terms of Use"
    },
    "한국어": {
        "subtitle": "한국 및 미국 주식 기술적 분석 및 AI 전략 리포트",
        "settings": "설정",
        "api_key_help": "Google AI Studio에서 키를 발급받으세요",
        "api_key_info": "API 키가 없으면 기술 분석만 수행됩니다.",
        "dev_by": "Developed by Antigravity",
        "input_label": "종목 티커 또는 영어 이름 (예: 005930, AAPL, Tesla)",
        "input_placeholder": "예: 005930",
        "help_caption": "💡 **도움말**: 한국 주식은 **6자리 숫자 티커**를 입력해 주세요. 미국 주식은 **티커 또는 영어 기업명** 인식이 가능합니다.",
        "purchase_price": "평균 매수 가격 (단위: 원 또는 달러)",
        "purchase_price_help": "보유 중인 경우 입력하세요. 신규 진입이라면 0으로 두세요.",
        "analyze_btn": "분석 시작",
        "analyzing": "분석 중",
        "error": "오류 발생",
        "current_price": "현재가",
        "rsi": "RSI (20)",
        "macd": "MACD",
        "bb_mid": "볼린저 중단",
        "overbought": "과매수",
        "oversold": "과매도",
        "latest_news": "최신 주요 뉴스",
        "news_help": "※ 제목을 클릭하거나 우측 버튼을 눌러 전체 기사를 확인하세요.",
        "view_article": "기사 보기",
        "all_news_naver": "네이버 금융에서 전체 뉴스 보기",
        "provided_by": "제공",
        "ai_report": "🤖 Meta AI 분석 리포트",
        "ai_warning": "AI 분석을 보려면 사이드바에 Gemini API Key를 입력하세요.",
        "start_info": "종목 티커를 입력하고 '분석 시작' 버튼을 누르세요.",
        "features_title": "#### 📈 주요 기능",
        "features_list": """
        - **기술적 지표 분석**: RSI, MACD, 볼린저 밴드 등 핵심 지표 실시간 계산
        - **최신 뉴스 통합**: 종목별 주요 뉴스를 한눈에 확인
        - **인공지능 리포트**: 종목별 주요 뉴스와 기술적 지표 분석을 바탕으로 맞춤형 투자 전략 제안
        """,
        "how_to_title": "#### 💡 사용 방법",
        "how_to_list": """
        1. 왼쪽 사이드바에 **Gemini API Key**를 입력합니다 (선택 사항).
        2. 분석하고 싶은 **종목 티커 또는 영어 이름**을 입력합니다.
        3. '분석 시작' 버튼을 눌러 결과 보고서를 확인합니다.
        """,
        "legal": "본 서비스에서 제공하는 정보는 투자 참고용이며, 투자에 대한 최종 책임은 본인에게 있습니다.",
        "privacy": "개인정보 처리방침",
        "terms": "이용 약관"
    }
}

t = texts[lang]

st.markdown(f"### {t['subtitle']}")

# Sidebar
with st.sidebar:
    st.header(t['settings'])
    api_key = st.text_input("Gemini API Key", type="password", help=t['api_key_help'])
    st.info(t['api_key_info'])
    st.divider()
    st.markdown(t['dev_by'])

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    symbol = st.text_input(t['input_label'], placeholder=t['input_placeholder'])
    st.caption(t['help_caption'])
    purchase_price = st.number_input(t['purchase_price'], min_value=0.0, value=0.0, format="%.2f", help=t['purchase_price_help'])

if symbol:
    # Resolve symbol
    analyzer = StockAnalyzer()
    
    if st.button(t['analyze_btn']):
        # Show a resolving message if it's likely a name
        with st.spinner(f"{t['analyzing']} '{symbol}'..."):
            resolved_ticker = analyzer.get_ticker(symbol, api_key=api_key)
            company_name = analyzer.get_company_name(resolved_ticker)
            st.session_state['resolved_ticker'] = resolved_ticker
            st.session_state['company_name'] = company_name
            
            # 1. Fetch Data
            df, error = analyzer.fetch_data(resolved_ticker)
            
            if error:
                st.error(f"{t['error']}: {error}")
            else:
                # 2. Indicators
                df = analyzer.calculate_indicators(df)
                latest = df.iloc[-1]
                news = analyzer.fetch_news(resolved_ticker)
                
                # Header with Company Name
                st.subheader(f"📈 {company_name} ({resolved_ticker})")
                
                # Metrics Display
                st.divider()
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric(t['current_price'], f"{latest['Close']:,.2f}")
                m_col2.metric(t['rsi'], f"{latest['RSI']:.2f}")
                m_col3.metric(t['macd'], f"{latest['MACD']:.2f}")
                m_col4.metric(t['bb_mid'], f"{latest['BB_Mid']:,.2f}")
                
                # Charts
                # 1. Price + Bollinger Bands
                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#007bff', width=2)))
                fig_price.add_trace(go.Scatter(x=df.index, y=df['BB_High'], name='BB Upper', line=dict(color='rgba(255, 165, 0, 0.6)', width=1, dash='dot')))
                fig_price.add_trace(go.Scatter(x=df.index, y=df['BB_Low'], name='BB Lower', line=dict(color='rgba(255, 165, 0, 0.6)', width=1, dash='dot')))
                fig_price.add_trace(go.Scatter(x=df.index, y=df['BB_Mid'], name='BB Mid', line=dict(color='rgba(255, 255, 255, 0.3)', width=1)))
                fig_price.update_layout(title=f"{company_name} ({resolved_ticker}) Price & Bollinger Bands", template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_price, use_container_width=True)

                c_col1, c_col2 = st.columns(2)
                
                with c_col1:
                    # 2. RSI
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#ff6b6b')))
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text=t['overbought'])
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text=t['oversold'])
                    fig_rsi.update_layout(title=t['rsi'], template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_rsi, use_container_width=True)

                with c_col2:
                    # 3. MACD
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_Diff'], name='Histogram', marker_color='gray'))
                    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#4dabf7')))
                    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='#fab005')))
                    fig_macd.update_layout(title=t['macd'], template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_macd, use_container_width=True)
                
                # 4. Latest News Section
                if news:
                    st.divider()
                    st.subheader(f"📰 {t['latest_news']}")
                    st.markdown(f'<p style="font-size: 0.8em; color: gray;">{t["news_help"]}</p>', unsafe_allow_html=True)
                    for i, item in enumerate(news):
                        title = item.get('title', 'News')
                        link = item.get('link')
                        if link:
                            # Using columns to separate title (content) and button (action)
                            n_col1, n_col2 = st.columns([0.8, 0.2])
                            with n_col1:
                                st.markdown(f"**{i+1}. {title}**")
                            with n_col2:
                                st.link_button(t['view_article'], link, use_container_width=True)
                        else:
                            st.write(f"• {title}")
                    
                    # Source attribution
                    if not resolved_ticker.endswith(('.KS', '.KQ')):
                        st.caption(f"{t['provided_by']}: Yahoo Finance / Google News")
                    else:
                        code = resolved_ticker.replace('.KS', '').replace('.KQ', '')
                        st.markdown(f"[🔗 {t['all_news_naver']}](https://finance.naver.com/item/news.naver?code={code})")
                        st.caption(f"{t['provided_by']}: 네이버 금융")
                
                # 5. AI Analysis
                if api_key:
                    price_info = f"Latest Close: {latest['Close']:.2f}, Volume: {latest['Volume']}"
                    technicals = f"RSI: {latest['RSI']:.2f}, MACD: {latest['MACD']:.2f}, BB High: {latest['BB_High']:.2f}, BB Low: {latest['BB_Low']:.2f}"
                    news_summary = "\n".join([n['title'] for n in news])
                    
                    ai_report = analyzer.generate_ai_analysis(
                        resolved_ticker, 
                        price_info, 
                        technicals, 
                        news_summary, 
                        api_key,
                        avg_purchase_price=purchase_price if purchase_price > 0 else None,
                        language=lang
                    )
                    
                    st.markdown(f"### {t['ai_report']}")
                    st.write(ai_report)
                else:
                    st.warning(t['ai_warning'])

else:
    st.info(t['start_info'])
    
    # Information Section for AdSense (Add more text content)
    st.divider()
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown(t['features_title'])
        st.markdown(t['features_list'])
    with col_info2:
        st.markdown(t['how_to_title'])
        st.markdown(t['how_to_list'])

# Footer & Legal (Crucial for AdSense approval)
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
with footer_col1:
    st.caption(f"© 2024 Pro Stock AI Analyzer. All rights reserved.")
    st.caption(t['legal'])
with footer_col2:
    st.markdown(f"[{t['privacy']}](#)")
with footer_col3:
    st.markdown(f"[{t['terms']}](#)")

