import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analyzer import StockAnalyzer

# --- Page Config ---
st.set_page_config(
    page_title="AI 한국 / 미국 주식 분석기",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced CSS: High-Visibility Light Theme ---
st.markdown("""
    <style>
    /* Global White Theme */
    .stApp {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
    
    /* Enforce Dark Text */
    h1, h2, h3, h4, h5, h6, p, label, div, span, li {
        color: #1f2937 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #1f2937 !important;
    }

    /* Vibrant Buttons */
    .stButton>button {
        border-radius: 8px;
        height: 3.2em;
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
    }
    .stButton>button:hover {
        background-color: #2563eb !important;
        transform: translateY(-1px);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-weight: 800 !important;
    }
    
    /* Containers */
    .legal-container {
        background-color: #f8fafc;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        line-height: 2.0;
        text-align: justify;
    }
    .legal-container h3 { color: #2563eb !important; margin-top: 30px; margin-bottom: 20px; font-size: 1.4em; }
    .legal-container p { margin-bottom: 15px; }
    .legal-container ul { margin-left: 20px; margin-bottom: 20px; }
    .legal-container li { margin-bottom: 10px; }
    
    .blue-bold { color: #2563eb; font-weight: bold; }
    .red-bold { color: #ef4444; font-weight: bold; }
    
    .disclaimer-box {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 25px;
        margin-top: 30px;
        border-radius: 8px;
    }
    
    .ad-wrapper {
        margin: 40px auto;
        padding: 20px;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background-color: #f8fafc;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Localization Dictionary ---
def get_content(lang):
    contents = {
        "English": {
            "nav_home": "Home / Analyzer",
            "nav_about": "Service Info",
            "nav_privacy": "Privacy Policy",
            "nav_terms": "Terms of Service",
            "nav_contact": "Contact",
            "title": "📈 Pro AI Stock Analyzer",
            "subtitle": "Professional KR & US Market Technical Analysis & AI Reports",
            "input_label": "Ticker or Company Name",
            "input_placeholder": "e.g., AAPL, 005930",
            "btn_analyze": "🚀 RUN AI ANALYSIS",
            "purchase_price": "Avg. Purchase Price",
            "ad_label": "ADVERTISEMENT",
            "metric_price": "Last Close",
            "metric_rsi": "RSI (20)",
            "metric_macd": "MACD",
            "metric_bb": "BB Mid",
            "chart_price_title": "Price Trend & Bollinger Bands",
            "chart_rsi_title": "RSI Momentum Indicator",
            "chart_macd_title": "MACD Trend Analysis",
            "legend_price": "Price",
            "legend_upper": "Upper Band",
            "legend_lower": "Lower Band",
            "legend_mid": "MA (20)",
            "legend_macd": "MACD Line",
            "legend_signal": "Signal Line",
            "latest_news": "Crucial Market News",
            "ai_report": "🤖 Institutional AI Strategy Report",
            "analyzing": "Synthesizing Data",
            "features_title": "#### 📈 Key Features & Methodology",
            "features_list": """
            - **Comprehensive Technical Analysis**: Real-time RSI, MACD, and Bollinger Bands.
            - **Real-Time News Aggregation**: Latest financial news from Yahoo Finance and Naver Finance.
            - **AI-Powered Insights**: Gemini Pro model synthesizes data for strategy reports.
            - **Global Market Support**: Support for KOSPI/KOSDAQ (Korea) and NYSE/NASDAQ (USA) stocks.
            """,
            "about_long": """
            <p>Our application is designed to bridge the data gap for individual investors by providing sophisticated financial analysis tools. We combine quantitative data with qualitative insights to deliver a <b>comprehensive view</b> of the market.</p>
            <h3>Core Analysis Methodology</h3>
            <ul>
                <li>Our system performs a <span class="blue-bold">Comprehensive Technical Analysis</span> by calculating real-time indicators such as RSI, MACD, and Bollinger Bands to help you understand market momentum and volatility.</li>
                <li>We integrate <span class="blue-bold">Real-Time News Aggregation</span> from reliable global sources like Yahoo Finance and Naver Finance, ensuring you have the necessary context behind every price movement.</li>
                <li>Utilizing the Gemini Pro model, our <span class="blue-bold">AI-Powered Insights</span> engine synthesizes technical data and news sentiment to generate professional strategy reports tailored to your portfolio.</li>
                <li>We offer <span class="blue-bold">Global Market Support</span>, allowing you to seamlessly analyze both South Korean (KOSPI/KOSDAQ) and United States (NYSE/NASDAQ) stocks in one place.</li>
            </ul>
            """,
            "how_to_title": "#### 💡 How to Use",
            "how_to_list": """
            1. **Configuration**: Enter your Gemini API Key in the sidebar.
            2. **Search**: Enter a stock ticker symbol (e.g., 'AAPL' or '005930').
            3. **Entry Price**: Enter your purchase price for personalized analysis.
            4. **Analyze**: Click 'RUN AI ANALYSIS'.
            """,
            "disclaimer_title": "⚠️ INVESTMENT RISK WARNING",
            "disclaimer_text": "The insights provided by Pro AI Stock Analyzer are for informational purposes only and do not constitute financial advice. Trading stocks involves <span class=\"red-bold\">high financial risk</span>, and AI-generated analysis may occasionally misinterpret data. Final responsibility rests with the user.",
            "privacy_long": """
            <h3>1. Personal Data Protection</h3>
            <p>We prioritize your anonymity. Pro Stock Analyzer is built on a "Privacy First" principle, meaning we do <b>not</b> store your API keys, portfolio values, or IP addresses on any server or database.</p>
            <h3>2. Third-Party Integrations</h3>
            <p>To provide high-quality services, we integrate with the following providers:</p>
            <ul>
                <li><b>Google Gemini</b>: Used exclusively for real-time AI processing of stock data.</li>
                <li><b>Yahoo Finance & Naver</b>: Utilized for fetching live market prices and news feeds.</li>
                <li><b>Google AdSense</b>: Employs cookies to serve personalized advertisements to keep this service free.</li>
            </ul>
            <h3>3. Security and Session Management</h3>
            <p>All data processing is session-based. This means your input data is cleared automatically once you close the application tab, ensuring your financial information remains private.</p>
            """,
            "terms_long": """
            <h3>1. Terms of Use</h3>
            By accessing this app, you agree to use the information as a reference only.
            <h3>2. Liability Limitation</h3>
            We are <b>not liable</b> for any financial losses or damages incurred through the use of this software.
            <h3>3. Data Accuracy</h3>
            While we strive for 100% accuracy, we do not guarantee the completeness of the third-party data provided.
            """
        },
        "한국어": {
            "nav_home": "홈 / 분석기",
            "nav_about": "서비스 소개",
            "nav_privacy": "개인정보 처리방침",
            "nav_terms": "이용약관",
            "nav_contact": "연락처",
            "title": "📈 AI 한국 / 미국 주식 분석기",
            "subtitle": "한국 및 미국 주식 기술적 분석 및 AI 전략 리포트",
            "input_label": "종목 티커 또는 영어 이름 입력",
            "input_placeholder": "예: 005930, AAPL",
            "btn_analyze": "🚀 AI 심층 분석 시작",
            "purchase_price": "평균 매수 가격",
            "ad_label": "ADVERTISEMENT",
            "metric_price": "현재가",
            "metric_rsi": "RSI (20)",
            "metric_macd": "MACD",
            "metric_bb": "볼린저 중단",
            "chart_price_title": "주가 흐름 및 볼린저 밴드",
            "chart_rsi_title": "RSI 모멘텀 지표",
            "chart_macd_title": "MACD 추세 분석",
            "legend_price": "현재 주가",
            "legend_upper": "상단 밴드 (저항)",
            "legend_lower": "하단 밴드 (지지)",
            "legend_mid": "20일 이동평균",
            "legend_macd": "MACD선",
            "legend_signal": "시그널선",
            "latest_news": "최신 주요 뉴스",
            "ai_report": "🤖 Meta AI 전문 분석 리포트",
            "analyzing": "데이터 분석 중",
            "features_title": "#### 📈 주요 기능 및 분석 방법",
            "features_list": """
            - **심층 기술 분석**: RSI, MACD, 볼린저 밴드 등 핵심 지표 실시간 계산 및 시각화.
            - **최신 뉴스 통합**: 네이버 및 Yahoo Finance의 뉴스 데이터를 수집하여 변동성 원인 파악.
            - **AI 리포트 생성**: 구글 Gemini Pro를 활용해 정량 데이터와 뉴스 심리를 결합한 분석 제공.
            - **글로벌 통합**: 국내(KOSPI/KOSDAQ) 및 해외(NYSE/NASDAQ) 시장 완벽 지원.
            """,
            "about_long": """
            <p>본 서비스는 개인 투자자들이 복잡한 시장 지표를 쉽게 이해하고 전문가급 분석 데이터를 활용할 수 있도록 설계된 통합 분석 플랫폼입니다. 정량적인 수치와 정성적인 뉴스 데이터를 결합하여 시장의 <span class="blue-bold">입체적인 인사이트</span>를 제공합니다.</p>
            <h3>핵심 분석 프로세스</h3>
            <ul>
                <li>본 서비스는 RSI, MACD, 볼린저 밴드 등 핵심 기술 지표를 실시간으로 계산하고 시각화하여 <span class="blue-bold">심층적인 기술 분석</span> 데이터를 제공합니다.</li>
                <li>네이버 금융 및 Yahoo Finance 등 신뢰할 수 있는 소스로부터 최신 뉴스를 수집하는 <span class="blue-bold">최신 뉴스 통합 엔진</span>을 통해 가격 변동의 배경을 파악할 수 있도록 돕습니다.</li>
                <li>구글의 최신 Gemini Pro 모델을 활용한 <span class="blue-bold">인공지능 리포트 생성</span> 기능은 기술 지표와 뉴스 심리를 결합하여 사용자 맞춤형 투자 전략을 제시합니다.</li>
                <li>국내 시장(KOSPI, KOSDAQ)과 미국 시장(NYSE, NASDAQ)을 모두 지원하는 <span class="blue-bold">글로벌 통합 환경</span>을 통해 종목에 관계없이 일관된 분석을 경험할 수 있습니다.</li>
            </ul>
            """,
            "how_to_title": "#### 💡 스톡 분석기 사용 방법",
            "how_to_list": """
            1. **API 설정**: 왼쪽 사이드바에 **Gemini API Key**를 입력하세요.
            2. **종목 입력**: 분석할 **종목명이나 티커**를 검색창에 입력하세요.
            3. **평단가 입력**: 보유 중이라면 평단가를 입력하여 **수익률 맞춤 전략**을 받으세요.
            4. **분석 실행**: 'AI 분석 시작' 버튼을 눌러 리포트를 생성하세요.
            """,
            "disclaimer_title": "### ⚠️ 법적 면책 조항 및 투자 주의사항",
            "disclaimer_text": "AI 스톡 분석기에서 제공하는 모든 정보는 알고리즘에 의해 자동 생성된 참고용 데이터이며, <span class=\"red-bold\">어떠한 경우에도 금융 조언으로 간주될 수 없습니다.</span> 주식 투자는 원금 손실의 위험이 있으며, 모든 투자 결정과 그 결과에 대한 책임은 <span class=\"blue-bold\">사용자 본인</span>에게 있습니다.",
            "privacy_long": """
            <h3>1. 개인정보 처리 원칙</h3>
            <p>우리는 사용자의 익명성을 최우선으로 생각합니다. AI 스톡 분석기는 "보안 우선" 원칙에 따라 사용자의 API 키, 포트폴리오 정보, 검색 기록 등을 어떠한 서버나 데이터베이스에도 <b>저장하지 않습니다.</b></p>
            <h3>2. 제3자 서비스 데이터 제공</h3>
            <p>고품질의 분석 서비스를 제공하기 위해 다음과 같은 외부 서비스를 활용합니다:</p>
            <ul>
                <li><b>Google Gemini</b>: 주가 및 뉴스 데이터의 실시간 AI 분석을 위해 사용됩니다.</li>
                <li><b>네이버 금융 및 Yahoo Finance</b>: 실시간 시세 및 뉴스 피드를 수집하기 위해 활용됩니다.</li>
                <li><b>Google AdSense</b>: 무료 서비스 유지를 위해 맞춤형 광고 쿠키를 사용하며, 이에 따라 사용자 식별 정보가 활용될 수 있습니다.</li>
            </ul>
            <h3>3. 보안 대책 및 세션 관리</h3>
            <p>모든 데이터 처리는 세션 단위로 이루어집니다. 즉, 사용자가 브라우저 탭을 닫는 즉시 입력된 모든 데이터는 자동으로 파기되어 개인정보 노출 위험을 원천 차단합니다.</p>
            """,
            "terms_long": """
            <h3>1. 이용 조건</h3>
            본 앱의 정보는 단순 참고용이며, 이를 이용한 실제 매매의 책임은 전적으로 이용자에게 있습니다.
            <h3>2. 책임의 제한</h3>
            데이터 오류, 시스템 장애, 혹은 AI의 오답으로 발생한 재무적 손실에 대해 당사는 책임을 지지 않습니다.
            <h3>3. 서비스 이용 제한</h3>
            과도한 트래픽 유발이나 비정상적인 접근은 차단될 수 있습니다.
            """
        }
    }
    return contents[lang]

# --- UI Functions ---
def render_ad(t):
    st.markdown(f'<div class="ad-wrapper"><div style="font-size: 10px; color: #94a3b8;">{t["ad_label"]}</div><div>[ Sponsored Area ]</div></div>', unsafe_allow_html=True)

# --- Pages ---
def show_home():
    t = get_content(st.session_state['lang'])
    st.title(t['title'])
    st.markdown(f"**{t['subtitle']}**")
    
    with st.sidebar:
        st.header("⚙️ Setting")
        api_key = st.text_input("Gemini API Key", type="password")
        st.divider()
        st.caption("Developed by Antigravity")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        symbol = st.text_input(t['input_label'], placeholder=t['input_placeholder'])
        purchase_price = st.number_input(t['purchase_price'], min_value=0.0, format="%.2f")
        analyze_btn = st.button(t['btn_analyze'])

    if symbol and analyze_btn:
        analyzer = StockAnalyzer()
        with st.spinner(f"{t['analyzing']}..."):
            resolved_ticker = analyzer.get_ticker(symbol, api_key=api_key)
            company_name = analyzer.get_company_name(resolved_ticker)
            df, error = analyzer.fetch_data(resolved_ticker)
            
            if not error:
                df = analyzer.calculate_indicators(df)
                latest = df.iloc[-1]
                news = analyzer.fetch_news(resolved_ticker)
                
                st.subheader(f"📊 {company_name} ({resolved_ticker})")
                
                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(t['metric_price'], f"{latest['Close']:,.2f}")
                m2.metric(t['metric_rsi'], f"{latest['RSI']:.2f}")
                m3.metric(t['metric_macd'], f"{latest['MACD']:.2f}")
                m4.metric(t['metric_bb'], f"{latest['BB_Mid']:,.2f}")
                
                # 1. Price + Bollinger Bands (Improved Visibility)
                fig_p = go.Figure()
                fig_p.add_trace(go.Scatter(x=df.index, y=df['Close'], name=t['legend_price'], line=dict(color='#2563eb', width=3)))
                fig_p.add_trace(go.Scatter(x=df.index, y=df['BB_High'], name=t['legend_upper'], line=dict(color='#ef4444', width=1.5)))
                fig_p.add_trace(go.Scatter(x=df.index, y=df['BB_Low'], name=t['legend_lower'], line=dict(color='#10b981', width=1.5)))
                fig_p.add_trace(go.Scatter(x=df.index, y=df['BB_Mid'], name=t['legend_mid'], line=dict(color='rgba(0,0,0,0.2)', width=1)))
                fig_p.update_layout(title=t['chart_price_title'], template="plotly_white", height=450)
                st.plotly_chart(fig_p, use_container_width=True)

                # 2. Indicators
                c1, c2 = st.columns(2)
                with c1:
                    fig_r = go.Figure()
                    fig_r.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#ef4444')))
                    fig_r.add_hline(y=70, line_dash="dash", line_color="red")
                    fig_r.add_hline(y=30, line_dash="dash", line_color="green")
                    fig_r.update_layout(title=t['chart_rsi_title'], template="plotly_white", height=300)
                    st.plotly_chart(fig_r, use_container_width=True)
                with c2:
                    fig_m = go.Figure()
                    fig_m.add_trace(go.Scatter(x=df.index, y=df['MACD'], name=t['legend_macd'], line=dict(color='#3b82f6', width=2)))
                    fig_m.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name=t['legend_signal'], line=dict(color='#f59e0b', width=1.5)))
                    fig_m.update_layout(title=t['chart_macd_title'], template="plotly_white", height=300)
                    st.plotly_chart(fig_m, use_container_width=True)
                
                if news:
                    st.divider()
                    st.subheader(f"📰 {t['latest_news']}")
                    for item in news[:5]:
                        st.markdown(f"• **[{item['title']}]({item['link']})**")
                
                if api_key:
                    st.divider()
                    st.subheader(t['ai_report'])
                    p_info = f"Price: {latest['Close']:.2f}, Volume: {latest['Volume']}"
                    t_info = f"RSI: {latest['RSI']:.2f}, MACD: {latest['MACD']:.2f}, BB-Mid: {latest['BB_Mid']:.2f}"
                    n_info = " | ".join([n['title'] for n in news[:5]])
                    report = analyzer.generate_ai_analysis(resolved_ticker, p_info, t_info, n_info, api_key, 
                                                         avg_purchase_price=purchase_price if purchase_price > 0 else None,
                                                         language=st.session_state['lang'])
                    st.write(report)
    else:
        st.divider()
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(t['features_title'])
            st.markdown(t['features_list'])
        with sc2:
            st.markdown(t['how_to_title'])
            st.markdown(t['how_to_list'])
    
    render_ad(t)
    st.caption(t['disclaimer_title'])

def show_about():
    t = get_content(st.session_state['lang'])
    st.title(t['nav_about'])
    st.markdown(f'<div class="legal-container">{t["about_long"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer-box"><span class="red-bold">{t["disclaimer_title"]}</span><br>{t["disclaimer_text"]}</div>', unsafe_allow_html=True)
    render_ad(t)

def show_privacy():
    t = get_content(st.session_state['lang'])
    st.title(t['nav_privacy'])
    st.markdown(f'<div class="legal-container">{t["privacy_long"]}</div>', unsafe_allow_html=True)
    render_ad(t)

def show_terms():
    t = get_content(st.session_state['lang'])
    st.title(t['nav_terms'])
    st.markdown(f'<div class="legal-container">{t["terms_long"]}</div>', unsafe_allow_html=True)
    render_ad(t)

def show_contact():
    t = get_content(st.session_state['lang'])
    st.title(t['nav_contact'])
    st.markdown(f"📧 **Email**: superhky@hotmail.com")
    render_ad(t)

def main():
    if 'lang' not in st.session_state: st.session_state['lang'] = '한국어'
    with st.sidebar:
        st.session_state['lang'] = st.radio("Language", ["English", "한국어"], index=1, horizontal=True)
    t = get_content(st.session_state['lang'])
    pg = st.navigation([
        st.Page(show_home, title=t['nav_home'], icon="🏠"),
        st.Page(show_about, title=t['nav_about'], icon="ℹ️"),
        st.Page(show_privacy, title=t['nav_privacy'], icon="🔒"),
        st.Page(show_terms, title=t['nav_terms'], icon="📄"),
        st.Page(show_contact, title=t['nav_contact'], icon="📧"),
    ])
    pg.run()

if __name__ == "__main__": main()
