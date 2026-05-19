import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

DARK = dict(paper_bgcolor="#262730", plot_bgcolor="#1e1e2e", font_color="#ffffff")

def get_data(ticker, period):
    stock = yf.Ticker(ticker)
    data  = stock.history(period=period)
    if data.empty:
        st.error(f"❌ Invalid ticker: {ticker}")
        return None
    return data, stock

def price_summary(data, period):
    latest_close = data["Close"].iloc[-1]
    prev         = data["Close"].iloc[-2]
    daily_pct    = data["Close"].pct_change().iloc[-1] * 100

    st.markdown("#### 🟡 Price Summary")
    c1, c2 = st.columns(2)
    c1.metric("Latest Close",   f"${latest_close:.2f}", f"{latest_close - prev:+.2f}")
    c2.metric("Daily Change %", f"{daily_pct:.2f}%")
    c3, c4 = st.columns(2)
    c3.metric(f"{period} High", f"${data['Close'].max():.2f}")
    c4.metric(f"{period} Low",  f"${data['Close'].min():.2f}")
    st.metric("Volume",         f"{data['Volume'].iloc[-1]:,.0f}")

def price_context(data):
    changes   = data["Close"].diff()
    direction = "Up" if changes.iloc[-1] > 0 else "Down"
    streak    = 1
    for i in range(-2, -len(changes), -1):
        if (changes.iloc[i] > 0) == (changes.iloc[-1] > 0):
            streak += 1
        else:
            break

    st.markdown("#### 🔴 Price Context")
    st.metric("Price Streak", f"{streak} day{'s' if streak > 1 else ''}", direction)

def volume_section(data):
    st.markdown("#### 🟠 Volume")
    st.metric("Latest Volume", f"{data['Volume'].iloc[-1]:,.0f}")

def trend_section(data):
    ma50  = data["Close"].rolling(50).mean().iloc[-1]
    ma20  = data["Close"].rolling(20).mean().iloc[-1]
    price = data["Close"].iloc[-1]

    # OBV — adds volume on up days, subtracts on down days
    obv       = (data["Volume"] * data["Close"].diff().apply(lambda x: 1 if x > 0 else -1)).cumsum()
    obv_trend = "Buying Pressure" if obv.iloc[-1] > obv.iloc[-5] else "Selling Pressure"

    st.markdown("#### 📈 Trend")
    c1, c2 = st.columns(2)
    c1.metric("MA50", f"${ma50:.2f}", "Above" if price > ma50 else "Below")
    c2.metric("MA20", f"${ma20:.2f}", "Above" if price > ma20 else "Below")
    st.metric("OBV Trend", obv_trend, obv_trend,delta_color="normal" if obv_trend == "Buying Pressure" else "inverse")


def fundementals(stock):
    info = stock.info
    st.markdown("#### 🏢 Fundamentals")
    c1, c2 = st.columns(2)
    c1.metric("Market Cap",    f"${info.get('marketCap', 0) / 1e9:.1f}B")
    c2.metric("P/E Ratio",     f"{info.get('trailingPE', 'N/A')}")
    c3, c4 = st.columns(2)
    c3.metric("Revenue",       f"${info.get('totalRevenue', 0) / 1e9:.1f}B")
    c4.metric("Profit Margin", f"{info.get('profitMargins', 0) * 100:.1f}%")

def show_closeprice_linechart(data,ticker):
    st.markdown(f"#### Close Price + MA20 for {ticker}")
    ma20 = data["Close"].rolling(20).mean()
    fig  = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"],
        name="Close", line=dict(color="#ef4444", width=2)))
    fig.add_trace(go.Scatter(x=data.index, y=ma20,
        name="MA20", line=dict(color="#3b82f6", width=1.5, dash="dot")))
    fig.update_layout(**DARK, height=280, margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(gridcolor="#2d3139")
    fig.update_yaxes(gridcolor="#2d3139")
    st.plotly_chart(fig, use_container_width=True)

def cumulative_returns(data):
    st.markdown("#### Cumulative Return %")
    cum = ((1 + data["Close"].pct_change().dropna()).cumprod() - 1) * 100
    fig = go.Figure(go.Scatter(x=cum.index, y=cum,
        fill="tozeroy", line=dict(color="#22c55e", width=2)))
    fig.update_layout(**DARK, height=200, margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(gridcolor="#2d3139")
    fig.update_yaxes(gridcolor="#2d3139")
    st.plotly_chart(fig, use_container_width=True)

def bar_chart(data):
    st.markdown("#### Volume")
    colors = ["#22c55e" if c >= o else "#ef4444"
              for c, o in zip(data["Close"], data["Open"])]
    fig = go.Figure(go.Bar(x=data.index, y=data["Volume"],
        marker_color=colors, opacity=0.7))
    fig.update_layout(**DARK, height=200, margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(gridcolor="#2d3139")
    fig.update_yaxes(gridcolor="#2d3139")
    st.plotly_chart(fig, use_container_width=True)

def candle_sticks(data):
    st.markdown("#### Candlestick Chart")
    fig = go.Figure(go.Candlestick(
        x=data.index,
        open=data["Open"], high=data["High"],
        low=data["Low"],   close=data["Close"],
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
    ))
    fig.update_layout(**DARK, height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_rangeslider_visible=False)
    fig.update_xaxes(gridcolor="#2d3139")
    fig.update_yaxes(gridcolor="#2d3139")
    st.plotly_chart(fig, use_container_width=True)

def csv_file(data, ticker):
    st.download_button("⬇️ Download CSV", data.to_csv(),
                       f"{ticker}.csv", "text/csv")
