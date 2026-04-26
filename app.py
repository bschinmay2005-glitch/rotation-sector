import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------------
# NSE DATA FETCH
# -------------------------------
def get_nse_data():
    url = "https://www.nseindia.com/api/allIndices"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    data = response.json()["data"]

    sector_list = [
        "NIFTY AUTO","NIFTY IT","NIFTY PSU BANK","NIFTY FIN SERVICE",
        "NIFTY PHARMA","NIFTY FMCG","NIFTY METAL","NIFTY REALTY",
        "NIFTY MEDIA","NIFTY ENERGY","NIFTY PVT BANK","NIFTY INFRA",
        "NIFTY COMMODITIES","NIFTY CONSUMPTION","NIFTY PSE",
        "NIFTY SERVICES","NIFTY FINSRV25/50","NIFTY CONSUMER DURABLES",
        "NIFTY HEALTHCARE","NIFTY OIL & GAS","NIFTY INDIA MFG",
        "NIFTY INDIA DEFENCE"
    ]

    df = pd.DataFrame(data)
    df = df[df["index"].isin(sector_list)]

    return df[["index","last","percentChange"]]


# -------------------------------
# STORAGE
# -------------------------------
@st.cache_data(ttl=5)
def fetch_and_store():
    df = get_nse_data()
    df["time"] = datetime.now()
    return df


# -------------------------------
# UI
# -------------------------------
st.title("📊 Sector Heatmap + RRG")

mode = st.radio("Select View", ["Heatmap", "RRG"])

data = fetch_and_store()

# -------------------------------
# HEATMAP
# -------------------------------
if mode == "Heatmap":
    st.subheader("Sector Heatmap")

    fig = px.treemap(
        data,
        path=["index"],
        values="last",
        color="percentChange",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------------
# RRG (Basic)
# -------------------------------
else:
    st.subheader("RRG (Intraday)")

    st.warning("RRG improves as more data is collected")

    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame()

    st.session_state.history = pd.concat(
        [st.session_state.history, data],
        ignore_index=True
    )

    history = st.session_state.history

    if len(history) > 50:
        pivot = history.pivot_table(
            index="time",
            columns="index",
            values="last"
        )

        returns = pivot.pct_change().dropna()

        latest = returns.tail(1).T.reset_index()
        latest.columns = ["sector","momentum"]

        latest["relative"] = latest["momentum"].rank()

        fig = px.scatter(
            latest,
            x="relative",
            y="momentum",
            text="sector"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Collecting data... please wait")
