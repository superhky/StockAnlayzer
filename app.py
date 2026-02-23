import streamlit as st

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

st.title("📈 AI Stock Analyzer")
st.markdown("### 한국 및 미국 주식 기술적 분석 및 AI 전략 리포트")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="Get your key from Google AI Studio")
    st.info("API 키가 없으면 기술 분석만 수행됩니다.")
    st.divider()
    st.markdown("Developed by Antigravity")

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    symbol = st.text_input("종목 티커 또는 영어 이름 (예: 005930, AAPL, Tesla)", placeholder="005930")
    st.caption("💡 **도움말**: 한국 주식은 **6자리 숫자 티커**를 입력해 주세요. 미국 주식은 **티커 또는 영어 기업명** 인식이 가능합니다.")
    purchase_price = st.number_input("평균 매수 가격 (단위: 원 또는 달러)", min_value=0.0, value=0.0, format="%.2f", help="보유 중인 경우 입력하세요. 신규 진입이라면 0으로 두세요.")

if symbol:
    # Resolve symbol
    analyzer = StockAnalyzer()
    
    if st.button("분석 시작"):
        # Show a resolving message if it's likely a name
        with st.spinner(f"'{symbol}' 분석 중..."):
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
                with st.expander("최신 관련 뉴스", expanded=True):
                    if not news:
                        st.info("실시간 뉴스 데이터를 불러오는 중입니다. 잠시 후 다시 시도하거나 아래 버튼을 클릭하세요.")
                        if not resolved_ticker.endswith(('.KS', '.KQ')):
                            st.link_button("🌐 Yahoo Finance에서 직접 뉴스 보기", f"https://finance.yahoo.com/quote/{resolved_ticker}/news", use_container_width=True)
                        else:
                            st.link_button("🌐 네이버 금융에서 직접 뉴스 보기", f"https://finance.naver.com/item/news.naver?code={resolved_ticker.replace('.KS','').replace('.KQ','')}", use_container_width=True)
                    else:
                        for item in news:
                            title = item.get('title', '뉴스 제목 없음')
                            link = item.get('link')
                            if link and str(link).startswith('http'):
                                # Streamlit's link_button opens in a new tab by default
                                st.link_button(f"🔗 {title}", link, use_container_width=True)
                            else:
                                # Show title even if link is missing
                                st.write(f"📄 {title} (링크를 불러올 수 없음)")
                        
                        # Footer link for direct source
                        st.divider()
                        if not resolved_ticker.endswith(('.KS', '.KQ')):
                            st.caption(f"제공: [Yahoo Finance](https://finance.yahoo.com/quote/{resolved_ticker}/news)")
                        else:
                            st.caption(f"제공: [네이버 금융](https://finance.naver.com/item/news.naver?code={resolved_ticker.replace('.KS','').replace('.KQ','')})")
                
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
    st.info("종목 티커를 입력하고 '분석 시작' 버튼을 누르세요.")
    
    # Information Section for AdSense (Add more text content)
    st.divider()
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("#### 📈 주요 기능")
        st.markdown("""
        - **기술적 지표 분석**: RSI, MACD, 볼린저 밴드 등 핵심 지표 실시간 계산
        - **최신 뉴스 통합**: 종목별 주요 뉴스를 한눈에 확인
        - **인공지능 리포트**: 종목별 주요 뉴스와 기술적 지표 분석을 바탕으로 맞춤형 투자 전략 제안
        """)
    with col_info2:
        st.markdown("#### 💡 사용 방법")
        st.markdown("""
        1. 왼쪽 사이드바에 **Gemini API Key**를 입력합니다 (선택 사항).
        2. 분석하고 싶은 **종목 티커 또는 영어 이름**을 입력합니다.
        3. '분석 시작' 버튼을 눌러 결과 보고서를 확인합니다.
        """)

# Footer & Legal (Crucial for AdSense approval)
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
with footer_col1:
    st.caption("© 2024 Pro Stock AI Analyzer. All rights reserved.")
    st.caption("본 서비스에서 제공하는 정보는 투자 참고용이며, 투자에 대한 최종 책임은 본인에게 있습니다.")
with footer_col2:
    st.markdown("[개인정보 처리방침](#)")
with footer_col3:
    st.markdown("[이용 약관](#)")

