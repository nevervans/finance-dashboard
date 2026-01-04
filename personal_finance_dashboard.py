import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

st.title("📊 Personal Portfolio Dashboard")

st.write(
    "Upload your portfolio CSV to view live valuation, allocation, and returns."
)

# Upload CSV
uploaded_file = st.file_uploader(
    "Upload Portfolio CSV", type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = {"Ticker", "Quantity", "Avg_Price"}
    if not required_cols.issubset(df.columns):
        st.error("CSV must contain: Ticker, Quantity, Avg_Price")
        st.stop()

    tickers = df["Ticker"].tolist()

    # Fetch live prices
    data = yf.download(tickers, period="1d", group_by="ticker", auto_adjust=True)

    live_prices = []
    for ticker in tickers:
        try:
            price = data[ticker]["Close"].iloc[-1]
        except:
            price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        live_prices.append(price)

    df["Current_Price"] = live_prices
    df["Investment"] = df["Quantity"] * df["Avg_Price"]
    df["Current_Value"] = df["Quantity"] * df["Current_Price"]
    df["P&L"] = df["Current_Value"] - df["Investment"]
    df["Return_%"] = (df["P&L"] / df["Investment"]) * 100

    total_value = df["Current_Value"].sum()
    total_invested = df["Investment"].sum()
    total_pnl = total_value - total_invested

    # ---- Metrics ----
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invested", f"₹{total_invested:,.0f}")
    col2.metric("Current Value", f"₹{total_value:,.0f}")
    col3.metric("Total P&L", f"₹{total_pnl:,.0f}")

    st.divider()

    # ---- Allocation Pie ----
    st.subheader("📈 Portfolio Allocation")

    fig = px.pie(
        df,
        names="Ticker",
        values="Current_Value",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Table ----
    st.subheader("📋 Portfolio Details")
    st.dataframe(
        df.style.format({
            "Avg_Price": "₹{:.2f}",
            "Current_Price": "₹{:.2f}",
            "Investment": "₹{:.0f}",
            "Current_Value": "₹{:.0f}",
            "P&L": "₹{:.0f}",
            "Return_%": "{:.2f}%"
        })
    )

else:
    st.info("👆 Upload a portfolio CSV to begin")


