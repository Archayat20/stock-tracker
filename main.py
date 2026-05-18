import streamlit as st
from utils import get_data, metric_rows, fundementals

st.markdown("""<style>.block-container {
        max-width: 80%;
        padding-left: 5%;
        padding-right: 5%;
    }</style>""", unsafe_allow_html=True)


st.title("📈 Stock Price Tracker")
st.markdown("""
---
### About this project
 
Hi, I'm **Archayan**, an 18-year-old CS student with a strong interest in AI and data.
I built this app from scratch using **Python** and **Streamlit** to explore how real-world
financial data can be fetched, processed, and visualised in a clean, interactive way.
 
**What this app does:**
- 📊 Pulls live stock data using the **yfinance** API
- 📈 Displays closing prices, candlestick charts, volume bars, and cumulative returns
- 💼 Tracks a personal portfolio and calculates total value based on shares owned
- ⚖️ Compares multiple stocks side by side with correlation scores and best/worst day tables
- 📰 Fetches live news headlines per ticker with date filtering and links to full articles
 
**Skills & tools used:**
- **Python** — core logic, data processing, and API calls
- **Streamlit** — building and deploying the interactive web app
- **yfinance** — fetching real-time and historical market data
- **Plotly** — interactive candlestick charts
- **Pandas** — data manipulation and analysis
- **Multi-page architecture** — structured the app with a `pages/` folder and shared `utils.py` to avoid repeated code
- **Session state** — persisting data across pages without re-fetching
- **API handling** — parsing nested JSON responses and handling missing or broken data gracefully
 
**What I learned:**
Building this taught me how to structure a real project, not just write scripts.
I learned how to separate concerns, reuse code properly, handle real-world messy data,
and think about the user experience — not just whether the code runs.
 
---
""")
 
st.caption("Use the sidebar to navigate between pages.")