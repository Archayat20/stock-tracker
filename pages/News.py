import streamlit as st
import yfinance as yf
import datetime

st.markdown("""<style>.block-container {
        max-width: 80%;
        padding-left: 5%;
        padding-right: 5%;
    }</style>""", unsafe_allow_html=True)



st.title("📰 News")

# 1. user inputs
ticker    = st.text_input("Enter stock ticker:", value="AAPL").upper()
from_date = st.date_input("From", value=datetime.date.today() - datetime.timedelta(days=7))
to_date   = st.date_input("To",   value=datetime.date.today())

if st.button("Get News"):

    # 2. fetch news
    news = yf.Ticker(ticker).news
    # 3. loop through articles, filter by date
    filtered = []
    for article in news:
        content  = article.get("content", {})
        pub      = content.get("pubDate", "")
        try:
            pub_date = datetime.datetime.strptime(pub[:10], "%Y-%m-%d").date()
        except:
            continue
        if from_date <= pub_date <= to_date:
            filtered.append((pub_date, content))

    # 4. display
    st.subheader(f"{len(filtered)} articles for {ticker}")
    for pub_date, content in sorted(filtered, key=lambda x: x[0], reverse=True):
        title  = content.get("title", "No title")
        link   = content.get("canonicalUrl", {}).get("url", "#")
        source = content.get("provider",     {}).get("displayName", "Unknown")
        st.markdown(f"### [{title}]({link})")
        st.caption(f"📅 {pub_date} · 📰 {source}")
        st.divider()