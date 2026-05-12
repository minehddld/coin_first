import streamlit as st
import pyupbit
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="실시간 암호화폐 대시보드",
    layout="wide"
)

# 자동 새로고침 (5초)
st_autorefresh(interval=5000, key="refresh")

# -----------------------------
# 제목
# -----------------------------
st.title("📈 실시간 암호화폐 데이터 분석 대시보드")

st.markdown("""
업비트 API를 활용한 실시간 암호화폐 시세 분석 시스템
""")

# -----------------------------
# 코인 선택
# -----------------------------
coins = {
    "비트코인": "KRW-BTC",
    "이더리움": "KRW-ETH",
    "리플": "KRW-XRP",
    "솔라나": "KRW-SOL",
    "도지코인": "KRW-DOGE"
}

selected_coin = st.sidebar.selectbox(
    "코인 선택",
    list(coins.keys())
)

ticker = coins[selected_coin]

# -----------------------------
# 현재 가격
# -----------------------------
current_price = pyupbit.get_current_price(ticker)

st.metric(
    label=f"{selected_coin} 현재가",
    value=f"{current_price:,.0f} 원"
)

# -----------------------------
# 데이터 가져오기
# -----------------------------
df = pyupbit.get_ohlcv(
    ticker=ticker,
    interval="minute1",
    count=100
)

# -----------------------------
# 이동평균선
# -----------------------------
df['MA5'] = df['close'].rolling(5).mean()
df['MA20'] = df['close'].rolling(20).mean()

# -----------------------------
# RSI 계산
# -----------------------------
rsi = RSIIndicator(close=df['close'], window=14)
df['RSI'] = rsi.rsi()

# -----------------------------
# 캔들 차트
# -----------------------------
st.subheader("📊 캔들 차트")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='캔들차트'
    )
)

# 이동평균선 추가
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['MA5'],
        mode='lines',
        name='MA5'
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['MA20'],
        mode='lines',
        name='MA20'
    )
)

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 거래량 차트
# -----------------------------
st.subheader("📦 거래량")

volume_fig = go.Figure()

volume_fig.add_trace(
    go.Bar(
        x=df.index,
        y=df['volume'],
        name='거래량'
    )
)

volume_fig.update_layout(height=300)

st.plotly_chart(volume_fig, use_container_width=True)

# -----------------------------
# RSI 차트
# -----------------------------
st.subheader("📉 RSI 지표")

rsi_fig = go.Figure()

rsi_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['RSI'],
        mode='lines',
        name='RSI'
    )
)

# 기준선
rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
rsi_fig.add_hline(y=30, line_dash="dash", line_color="blue")

rsi_fig.update_layout(height=300)

st.plotly_chart(rsi_fig, use_container_width=True)

# -----------------------------
# 데이터 테이블
# -----------------------------
st.subheader("📄 최근 데이터")

st.dataframe(df.tail())

# -----------------------------
# 설명
# -----------------------------
st.markdown("""
### 📌 지표 설명

- **MA5** : 5분 이동평균선
- **MA20** : 20분 이동평균선
- **RSI**
  - 70 이상 : 과매수
  - 30 이하 : 과매도
""")