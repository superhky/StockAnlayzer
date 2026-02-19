import streamlit as st

# Page config (MUST be the first Streamlit command)
st.set_page_config(page_title="Pro Stock Analyzer", layout="wide", initial_sidebar_state="expanded")

# Google AdSense Verification & Auto Ads
st.markdown("""
    <div style="display:none">
    <meta name="google-adsense-account" content="ca-pub-8764053427630602">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8764053427630602"
     crossorigin="anonymous"></script>
    </div>
    """, unsafe_allow_html=True)

import pandas as pd

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
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

st.title("🚀 Pro Stock AI Analyzer")
st.markdown("### 한국 및 미국 주식 기술적 분석 및 AI 전략 리포트")

# Sidebar
with st.sidebar:
    st.header("Settings")
    # AdSense verification hidden for users but visible to crawlers
    st.markdown('<div style="display:none">google.com, pub-8764053427630602, DIRECT, f08c47fec0942fa0</div>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", help="Get your key from Google AI Studio")
    st.info("API 키가 없으면 기술 분석만 수행됩니다.")
    st.divider()
    st.markdown("Developed by Antigravity")

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    symbol = st.text_input("종목 이름 또는 티커 (예: 삼성전자, AAPL, 005930)", placeholder="삼성전자")
    purchase_price = st.number_input("평균 매수 가격 (단위: 원 또는 달러)", min_value=0.0, value=0.0, format="%.2f", help="보유 중인 경우 입력하세요. 신규 진입이라면 0으로 두세요.")

if symbol:
    # Resolve symbol
    analyzer = StockAnalyzer()
    
    if st.button("분석 시작"):
        # Show a resolving message if it's likely a name
        with st.spinner(f"'{symbol}' 티커 확인 및 분석 중..."):
            resolved_ticker = analyzer.get_ticker(symbol, api_key=api_key)
            st.session_state['resolved_ticker'] = resolved_ticker
            
            # 1. Fetch Data
            df, error = analyzer.fetch_data(resolved_ticker)
            
            if error:
                st.error(f"오류 발생: {error}")
            else:
                # 2. Indicators
                df = analyzer.calculate_indicators(df)
                latest = df.iloc[-1]
                
                # Metrics Display
                st.divider()
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("현재가", f"{latest['Close']:,.2f}")
                m_col2.metric("RSI (20)", f"{latest['RSI']:.2f}")
                m_col3.metric("MACD", f"{latest['MACD']:.2f}")
                m_col4.metric("볼린저 중단", f"{latest['BB_Mid']:,.2f}")
                
                # Charts
                # 1. Price + Bollinger Bands
                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#007bff', width=2)))
                fig_price.add_trace(go.Scatter(x=df.index, y=df['BB_High'], name='BB Upper', line=dict(color='rgba(255, 165, 0, 0.6)', width=1, dash='dot')))
                fig_price.add_trace(go.Scatter(x=df.index, y=df['BB_Low'], name='BB Lower', line=dict(color='rgba(255, 165, 0, 0.6)', width=1, dash='dot')))
                fig_price.add_trace(go.Scatter(x=df.index, y=df['BB_Mid'], name='BB Mid', line=dict(color='rgba(255, 255, 255, 0.3)', width=1)))
                fig_price.update_layout(title=f"{resolved_ticker} Price & Bollinger Bands", template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_price, use_container_width=True)

                c_col1, c_col2 = st.columns(2)
                
                with c_col1:
                    # 2. RSI
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#ff6b6b')))
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                    fig_rsi.update_layout(title="RSI (20)", template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_rsi, use_container_width=True)

                with c_col2:
                    # 3. MACD
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_Diff'], name='Histogram', marker_color='gray'))
                    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#4dabf7')))
                    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='#fab005')))
                    fig_macd.update_layout(title="MACD", template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_macd, use_container_width=True)
                
                # 3. News
                news = analyzer.fetch_news(resolved_ticker)
                with st.expander("최신 관련 뉴스"):
                    for item in news:
                        title = item.get('title', '제목 없음')
                        link = item.get('link', '#')
                        st.markdown(f"- [{title}]({link})")
                
                # 4. AI Analysis
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
                        avg_purchase_price=purchase_price if purchase_price > 0 else None
                    )
                    
                    st.markdown("### 🤖 Meta AI 분석 리포트")
                    st.write(ai_report)
                else:
                    st.warning("AI 분석을 보려면 사이드바에 Gemini API Key를 입력하세요.")

else:
    st.info("종목 이름이나 티커를 입력하고 '분석 시작' 버튼을 누르세요.")
