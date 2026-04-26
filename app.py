import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="NSE Sector Dashboard", layout="wide")
st.title("📊 NSE Sectoral Indices Dashboard")

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

# -------------------------------
# NSE SESSION SETUP
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
# FETCH ALL INDICES
# -------------------------------
def fetch_indices():
    url = "https://www.nseindia.com/api/allIndices"
    try:
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
    except:
        # retry if blocked
        session.get("https://www.nseindia.com", headers=headers)
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()

    return pd.DataFrame(data["data"])

df = fetch_indices()

# -------------------------------
# EXACT SECTORAL INDICES LIST
# -------------------------------
SECTOR_INDICES = [
    "NIFTY AUTO",
    "NIFTY IT",
    "NIFTY PSU BANK",
    "NIFTY FINANCIAL SERVICES",
    "NIFTY PHARMA",
    "NIFTY FMCG",
    "NIFTY METAL",
    "NIFTY REALTY",
    "NIFTY MEDIA",
    "NIFTY ENERGY",
    "NIFTY PRIVATE BANK",
    "NIFTY INFRASTRUCTURE",
    "NIFTY COMMODITIES",
    "NIFTY CONSUMPTION",
    "NIFTY PSE",
    "NIFTY SERVICES SECTOR",
    "NIFTY FIN SERVICE 25/50",
    "NIFTY CONSUMER DURABLES",
    "NIFTY HEALTHCARE INDEX",
    "NIFTY OIL & GAS",
    "NIFTY INDIA MANUFACTURING",
    "NIFTY INDIA DEFENCE"
]

# -------------------------------
# FILTER ONLY REQUIRED INDICES
# -------------------------------
sector_df = df[df["index"].isin(SECTOR_INDICES)]

# Keep only needed columns
sector_df = sector_df[["index", "last", "percentChange"]]

# Maintain your order
sector_df["index"] = pd.Categorical(
    sector_df["index"],
    categories=SECTOR_INDICES,
    ordered=True
)
sector_df = sector_df.sort_values("index")

# -------------------------------
# HEATMAP STYLE DISPLAY
# -------------------------------
st.subheader("📦 Sector Heatmap")

def get_color(change):
    if change > 0:
        intensity = min(abs(change) / 2, 1)
        return f"rgba(0, 200, 0, {intensity})"
    else:
        intensity = min(abs(change) / 2, 1)
        return f"rgba(200, 0, 0, {intensity})"

cols = st.columns(4)

for i, row in sector_df.iterrows():
    col = cols[i % 4]
    color = get_color(row["percentChange"])

    col.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:15px;
            margin:10px;
            border-radius:10px;
            text-align:center;
            color:white;
            font-weight:bold;
        ">
            {row['index']}<br>
            {row['last']}<br>
            {row['percentChange']:.2f}%
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# TABLE VIEW (OPTIONAL)
# -------------------------------
st.subheader("📋 Sector Data Table")
st.dataframe(sector_df)
