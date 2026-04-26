import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="NSE Heatmap", layout="wide")

st.title("📊 NSE Heatmap Dashboard")

# Auto refresh every 5 sec
st_autorefresh(interval=5000, key="refresh")

# -------------------------------
# SESSION SETUP (IMPORTANT)
# -------------------------------
@st.cache_resource
def get_session():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    session.get("https://www.nseindia.com", headers=headers)
    return session, headers

session, headers = get_session()

# -------------------------------
# FETCH FUNCTION
# -------------------------------
def fetch_data(index_name):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name}"
    try:
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
        return pd.DataFrame(data["data"])
    except:
        # Retry once if blocked
        session.get("https://www.nseindia.com", headers=headers)
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
        return pd.DataFrame(data["data"])

# -------------------------------
# INDEX SELECTOR
# -------------------------------
indices = [
    "NIFTY 50",
    "NIFTY BANK",
    "NIFTY IT",
    "NIFTY FMCG",
    "NIFTY AUTO",
    "NIFTY PHARMA",
    "NIFTY METAL",
    "NIFTY ENERGY",
    "NIFTY PSU BANK",
    "NIFTY PRIVATE BANK"
]

index = st.selectbox("Select Index", indices)

# -------------------------------
# LOAD DATA
# -------------------------------
df = fetch_data(index)

# Clean required columns
df = df[["symbol", "lastPrice", "pChange"]]

# -------------------------------
# INDEX STRENGTH
# -------------------------------
avg_change = df["pChange"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Index", index)
col2.metric("Avg Change", f"{avg_change:.2f}%")
col3.metric("Stocks", len(df))

# -------------------------------
# TOP MOVERS
# -------------------------------
gainers = df.sort_values("pChange", ascending=False).head(5)
losers = df.sort_values("pChange").head(5)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top Gainers")
    st.dataframe(gainers)

with col2:
    st.subheader("🔻 Top Losers")
    st.dataframe(losers)

# -------------------------------
# HEATMAP GRID (CUSTOM)
# -------------------------------
st.subheader("📦 Heatmap View")

def get_color(change):
    if change > 0:
        intensity = min(abs(change) / 3, 1)
        return f"rgba(0, 200, 0, {intensity})"
    else:
        intensity = min(abs(change) / 3, 1)
        return f"rgba(200, 0, 0, {intensity})"

# Create grid
cols = st.columns(6)

for i, row in df.iterrows():
    col = cols[i % 6]
    color = get_color(row["pChange"])

    col.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:10px;
            margin:5px;
            border-radius:8px;
            text-align:center;
            color:white;
            font-weight:bold;
        ">
            {row['symbol']}<br>
            ₹{row['lastPrice']}<br>
            {row['pChange']:.2f}%
        </div>
        """,
        unsafe_allow_html=True
    )
