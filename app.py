import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

def show_closeprice_linechart(data):
    st.subheader("Closing price")
    ma20 = data["Close"].rolling(20).mean()
    st.line_chart(data[["Close"]].assign(MA20=ma20))

def cumulative_returns(data):
    st.subheader("Cumulative Return %")
    returns = data["Close"].pct_change().dropna()
    cumulative = ((1 + returns).cumprod() - 1) * 100
    st.line_chart(cumulative)

def bar_chart(data):
    st.subheader("Volume")
    st.bar_chart(data["Volume"],use_container_width=True)

def candle_sticks(data):
    st.subheader("Closing prices in a candlestick")
    fig = go.Figure(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    ))
    st.plotly_chart(fig, use_container_width=True)

def compare_stocks(period):
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


def main():
    

    dates = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    

    ticker = st.text_input("Enter stock ticker:", value="AAPL")
    periods_user = st.selectbox("Enter the period", dates, index=2)

    if st.button("Show Chart"):
        result = get_data(ticker, periods_user)
        if result is not None:
            data, stock = result
            st.session_state["data"] = data
            st.session_state["stock"] = stock
            st.session_state["period"] = periods_user

    if "data" in st.session_state:
        metric_rows(st.session_state["data"], periods_user)
        fundementals(st.session_state["stock"])
        show_closeprice_linechart(st.session_state["data"])
        cumulative_returns(st.session_state["data"])
        bar_chart(st.session_state["data"])
        candle_sticks(st.session_state["data"])
        compare_stocks(st.session_state["period"])
        csv_file(st.session_state["data"], ticker)

if __name__ == "__main__":
    main()
