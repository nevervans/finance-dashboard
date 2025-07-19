import pandas as pd
import requests
import streamlit as st
import openai
from typing import List, Dict

# --- CONFIGURATION ---
ALPHA_VANTAGE_API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

@st.cache_data(ttl=600)
def get_stock_price(ticker: str) -> float:
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    r = requests.get(url).json()
    try:
        return float(r["Global Quote"]["05. price"])
    except:
        return None

@st.cache_data(ttl=1800)
def get_news(ticker: str) -> List[Dict]:
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}&sortBy=publishedAt&pageSize=5"
    r = requests.get(url).json()
    return r.get("articles", [])

def summarize_news(text: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this news in 2 sentences and highlight its potential market impact (magnitude and direction)."},
                {"role": "user", "content": text},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception:
        return "Summary unavailable."

def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    return df

def enrich_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    prices, returns, values, gains = [], [], [], []
    for _, row in df.iterrows():
        price = get_stock_price(row['Ticker']) or 0
        value = price * row['Quantity']
        gain = (price - row['Buy Price']) * row['Quantity']
        returns.append((price - row['Buy Price']) / row['Buy Price'] * 100 if row['Buy Price'] else 0)
        prices.append(price)
        values.append(value)
        gains.append(gain)
    df['Live Price'] = prices
    df['Current Value'] = values
    df['Gain/Loss'] = gains
    df['Return (%)'] = returns
    return df

def main():
    st.title("📈 Personal Finance Dashboard")
    st.write("Upload a CSV with columns: Ticker, Quantity, Buy Price")
    uploaded_file = st.file_uploader("Choose a file", type=["csv"])
    if uploaded_file:
        df = load_csv(uploaded_file)
        df = enrich_portfolio(df)
        st.subheader("📊 Portfolio Overview")
        st.dataframe(df, use_container_width=True)
        st.subheader("📰 News & Impact")
        for ticker in df['Ticker']:
            st.markdown(f"### {ticker}")
            news_items = get_news(ticker)
            if not news_items:
                st.write("No recent news found.")
            for item in news_items:
                st.write(f"**{item['title']}**")
                st.caption(item['publishedAt'][:10])
                st.markdown(f"[Read more]({item['url']})")
                summary = summarize_news(item['title'] + '. ' + item.get("description", ""))
                st.info(summary)

if __name__ == '__main__':
    main()
