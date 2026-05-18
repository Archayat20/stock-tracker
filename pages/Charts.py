import streamlit as st
from utils import (
    get_data,
    metric_rows,
    fundementals,
    show_closeprice_linechart,
    cumulative_returns,
    bar_chart,
    candle_sticks,
    csv_file,
)

st.markdown("""<style>.block-container {
        max-width: 80%;
        padding-left: 5%;
        padding-right: 5%;
    }</style>""", unsafe_allow_html=True)

dates = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
st.title("📊 Charts")

ticker = st.text_input("Enter stock ticker:", value="AAPL")
periods_user = st.selectbox("Enter the period", dates, index=2)

if st.button("Show Chart"):
    result = get_data(ticker, periods_user)
    if result is not None:
        data, stock = result
        st.session_state["chart_data"]   = data
        st.session_state["chart_stock"]  = stock
        st.session_state["chart_period"] = periods_user
        st.session_state["chart_ticker"] = ticker

if "chart_data" in st.session_state:
    data   = st.session_state["chart_data"]
    stock  = st.session_state["chart_stock"]
    period = st.session_state["chart_period"]
    ticker = st.session_state["chart_ticker"]

    metric_rows(data, period)
    fundementals(stock)
    show_closeprice_linechart(data)
    cumulative_returns(data)
    bar_chart(data)
    candle_sticks(data)

    # compare section
    st.subheader("Compare Stocks")
    tickers = st.multiselect("Select tickers to compare", ["AAPL", "MSFT", "GOOG", "TSLA"], default=["AAPL"])
    if tickers:
        cols = st.columns(len(tickers))
        for t, col in zip(tickers, cols):
            with col:
                st.write(f"**{t}**")
                result = get_data(t, period)
                if result is not None:
                    data, _ = result
                    st.line_chart(data["Close"])

    csv_file(st.session_state["chart_data"], ticker)
