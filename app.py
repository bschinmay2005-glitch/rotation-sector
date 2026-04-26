import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="NSE Sector Dashboard", layout="wide")
st.title("📊 NSE Sector Performance")

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

# -------------------------------
# SESSION SETUP
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
def fetch_sector_data():
    url = "https://www.nseindia.com/api/allIndices"

    try:
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
    except:
        # Retry if blocked
        session.get("https://www.nseindia.com", headers=headers)
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()

    df = pd.DataFrame(data["data"])
    return df

# -------------------------------
# FILTER SECTOR INDICES ONLY
# -------------------------------
df = fetch_sector_data()

sector_keywords = [
    "BANK", "IT", "FMCG", "AUTO", "PHARMA",
    "METAL", "ENERGY", "REALTY", "MEDIA",
    "FINANCIAL", "PSU"
]

sector_df = df[df["index"].str.contains("|".join(sector_keywords), case=False)]

# Keep only needed columns
sector_df = sector_df[["index", "last", "percentChange"]]

# -------------------------------
# SORT (optional)
# -------------------------------
sector_df = sector_df.sort_values("percentChange", ascending=False)

# -------------------------------
# HEATMAP STYLE GRID
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
# TABLE VIEW (optional)
# -------------------------------
st.subheader("📋 Sector Data Table")
st.dataframe(sector_df)
