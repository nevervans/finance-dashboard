import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Portfolio Analyzer", layout="wide")
st.title("📊 Personal Portfolio Health Check")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_cols = {"Ticker", "Weight", "Sector", "BuyPrice", "CurrentPrice"}
        if not required_cols.issubset(df.columns):
            st.error(f"Missing required columns. Required: {required_cols}")
            st.stop()

        # --- Basic Calculations ---
        df["Return"] = (df["CurrentPrice"] - df["BuyPrice"]) / df["BuyPrice"]
        df["Weighted Return"] = df["Return"] * df["Weight"]
        portfolio_return = df["Weighted Return"].sum()
        volatility = df["Return"].std()
        risk_free_rate = 0.06
        sharpe = (portfolio_return - risk_free_rate) / volatility if volatility else None

        # Diversification Score (Herfindahl Index)
        df["WeightSquared"] = df["Weight"] ** 2
        diversification_score = df["WeightSquared"].sum()

        # --- Risk Diagnostics ---
        flags = []
        if df.groupby("Sector")["Weight"].sum().max() > 0.4:
            flags.append("⚠️ High sector concentration risk.")
        if (df["Return"] < 0).any():
            flags.append("⚠️ Loss-making stock present.")
        if "MarketCap" in df.columns and (df["MarketCap"] > 1000000).sum() / len(df) > 0.5:
            flags.append("⚠️ Heavy large-cap bias.")

        # --- Display Metrics ---
        st.subheader("📈 Portfolio Summary")
        st.write(f"**Portfolio Return:** {portfolio_return:.2%}")
        st.write(f"**Volatility (Std Dev):** {volatility:.2%}")
        st.write(f"**Sharpe Ratio:** {sharpe:.2f}" if sharpe else "Sharpe Ratio: N/A")
        st.write(f"**Diversification Score (HHI):** {diversification_score:.3f}")

        # --- Risk Warnings ---
        if flags:
            st.subheader("🚨 Risk Diagnostics")
            for flag in flags:
                st.warning(flag)
        else:
            st.success("No major risks detected.")

        # --- Charts ---
        st.subheader("📊 Sector Allocation")
        sector_alloc = df.groupby("Sector")["Weight"].sum()
        fig1, ax1 = plt.subplots()
        sector_alloc.plot.pie(autopct='%1.1f%%', ax=ax1)
        ax1.set_ylabel("")
        st.pyplot(fig1)

        st.subheader("📉 Individual Stock Returns")
        fig2, ax2 = plt.subplots()
        df.set_index("Ticker")["Return"].plot.bar(color='skyblue', ax=ax2)
        ax2.set_ylabel("Return (%)")
        st.pyplot(fig2)

        # --- Export Summary ---
        export_df = df[["Ticker", "Sector", "Return", "Weighted Return"]].copy()
        export_df["Return"] = export_df["Return"].apply(lambda x: f"{x:.2%}")
        export_df["Weighted Return"] = export_df["Weighted Return"].apply(lambda x: f"{x:.2%}")
        st.download_button("📥 Download Portfolio Summary", export_df.to_csv(index=False), "portfolio_summary.csv", "text/csv")

    except Exception as e:
        st.error(f"Something went wrong: {e}")

