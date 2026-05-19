import streamlit as st
from utils import (
    get_data,
    price_summary,        # ← add
    price_context,        # ← add
    volume_section,       # ← add
    trend_section,        # ← add
    fundementals,
    show_closeprice_linechart,
    cumulative_returns,
    bar_chart,
    candle_sticks,
    csv_file,
)

st.set_page_config(page_title="Trading Dashboard", layout="wide")

# only keeps padding fix, everything else handled by config.toml
st.markdown("""
<style>
  .block-container { padding: 1.5rem 2rem; max-width: 100%; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Stock Dashboard")
st.caption("Powered by Yahoo Finance")
st.divider()

dates = ["5d","1mo","3mo","6mo","1y","2y","5y","ytd","max"]
c1, c2, _ = st.columns([1, 1, 4])
with c1:
    ticker = st.text_input("Ticker", value="AAPL")
with c2:
    period = st.selectbox("Period", dates, index=2)

if st.button("Show Chart", type="primary"):
    result = get_data(ticker, period)
    if result:
        data, stock = result
        st.session_state["chart_data"]   = data
        st.session_state["chart_stock"]  = stock
        st.session_state["chart_period"] = period
        st.session_state["chart_ticker"] = ticker

if "chart_data" in st.session_state:
    data   = st.session_state["chart_data"]
    stock  = st.session_state["chart_stock"]
    period = st.session_state["chart_period"]
    ticker = st.session_state["chart_ticker"]

    left, center, right = st.columns([1.2, 2.5, 1.2])

    with left:
        price_summary(data, period)
        st.divider()
        trend_section(data)

    with center:
        show_closeprice_linechart(data)
        cumulative_returns(data)
        bar_chart(data)
        candle_sticks(data)

    with right:
        price_context(data)
        st.divider()
        volume_section(data)
        st.divider()
        fundementals(stock)
        st.divider()
        csv_file(data, ticker)
