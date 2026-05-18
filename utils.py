
import streamlit as st
import yfinance as yf
 
 
def get_data(ticker, period):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    if data.empty:
        st.error(f"❌ Invalid ticker: {ticker}")
        return None
    else:
        return data, stock
 
def metric_rows(data, periods_user):
    st.subheader("DATA")
    colm1,colm2,colm3,colm4,colm5=st.columns(5)
    latest_close=data["Close"].iloc[-1]
    prev=data["Close"].iloc[-2]
    Period_high = data["Close"].max()
    Period_low=data["Close"].min()
    volume=data["Volume"].iloc[-1]
    percentage_change=data["Close"].pct_change()
    colm1.metric("Latest Close", f"${latest_close:.2f}", f"{latest_close-prev:+.2f}")
    colm2.metric(f"{periods_user} High", f"${Period_high:.2f}")
    colm3.metric(f"{periods_user} Low", f"${Period_low:.2f}", f"Range: ${Period_high - Period_low:.2f}")
    colm4.metric("Volume", f"{volume:,.0f}")
    colm5.metric("Daily Change %", f"{percentage_change.iloc[-1]*100:.2f}%")
 
def fundementals(stock):
    try:
        info = stock.info
        st.subheader("Company Fundamentals")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap",    f"${info.get('marketCap', 0)/1e9:.2f}B")
        col2.metric("P/E Ratio",     f"{info.get('trailingPE', 'N/A')}")
        col3.metric("Revenue",       f"${info.get('totalRevenue', 0)/1e9:.2f}B")
        col4.metric("Profit Margin", f"{info.get('profitMargins', 0)*100:.2f}%")
    except Exception:
        st.warning("⚠️ Fundamentals unavailable right now — Yahoo Finance rate limit reached. Try again in a moment.")
 
def csv_file(data, ticker):
    csv = data.to_csv()
    st.download_button(
        "Download csv file",
        csv,
        f"{ticker}.csv",
        "text/csv"
    )
 
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
    import plotly.graph_objects as go
    fig = go.Figure(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    ))
    st.plotly_chart(fig, use_container_width=True)
