import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# -----------------------------
# NSE FETCH
# -----------------------------
def fetch_nse():
    url = "https://www.nseindia.com/api/allIndices"
    headers = {"User-Agent": "Mozilla/5.0"}

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    res = session.get(url, headers=headers)
    data = res.json()["data"]

    df = pd.DataFrame(data)
    return df[["index", "last"]]


# -----------------------------
# CONFIG
# -----------------------------
sectors = [
    "NIFTY AUTO","NIFTY IT","NIFTY PSU BANK","NIFTY FIN SERVICE",
    "NIFTY PHARMA","NIFTY FMCG","NIFTY METAL","NIFTY REALTY",
    "NIFTY MEDIA","NIFTY ENERGY","NIFTY PVT BANK","NIFTY INFRA",
    "NIFTY COMMODITIES","NIFTY CONSUMPTION","NIFTY PSE",
    "NIFTY SERVICES","NIFTY FINSRV25/50","NIFTY CONSUMER DURABLES",
    "NIFTY HEALTHCARE","NIFTY OIL & GAS","NIFTY INDIA MFG",
    "NIFTY INDIA DEFENCE","NIFTY 50"
]

# -----------------------------
# SESSION STORAGE
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame()

st.title("📊 Proper Sector RRG (Fixed)")

data = fetch_nse()
data = data[data["index"].isin(sectors)]

data["time"] = datetime.now()

st.session_state.history = pd.concat(
    [st.session_state.history, data],
    ignore_index=True
)

hist = st.session_state.history

# -----------------------------
# WAIT FOR ENOUGH DATA
# -----------------------------
if len(hist) < 30:
    st.warning("Collecting data... wait ~2–3 minutes for proper RRG")
    st.stop()

# -----------------------------
# PIVOT TABLE
# -----------------------------
pivot = hist.pivot_table(
    index="time",
    columns="index",
    values="last"
)

pivot = pivot.dropna()

# -----------------------------
# BENCHMARK (NIFTY 50)
# -----------------------------
if "NIFTY 50" not in pivot.columns:
    st.error("NIFTY 50 not found in data")
    st.stop()

benchmark = pivot["NIFTY 50"]

# -----------------------------
# RRG CALCULATION
# -----------------------------
rs_data = {}

for col in pivot.columns:
    if col == "NIFTY 50":
        continue

    rs = pivot[col] / benchmark
    rs_smooth = rs.rolling(5).mean()
    rs_momentum = rs_smooth.diff()

    rs_data[col] = pd.DataFrame({
        "rs_ratio": rs_smooth,
        "rs_momentum": rs_momentum
    })

# -----------------------------
# PLOT RRG
# -----------------------------
fig = go.Figure()

for sector, df in rs_data.items():
    df = df.dropna()

    fig.add_trace(go.Scatter(
        x=df["rs_ratio"],
        y=df["rs_momentum"],
        mode="lines+markers",
        name=sector,
        line=dict(width=2)
    ))

# -----------------------------
# QUADRANTS (like real RRG)
# -----------------------------
fig.add_shape(type="rect",
    x0=0.98, x1=1.02, y0=0, y1=1,
    fillcolor="gray", opacity=0.1, line_width=0)

fig.add_shape(type="rect",
    x0=0.98, x1=1.02, y0=-1, y1=0,
    fillcolor="gray", opacity=0.1, line_width=0)

fig.add_shape(type="rect",
    x0=1.02, x1=1.06, y0=0, y1=1,
    fillcolor="green", opacity=0.1, line_width=0)

fig.add_shape(type="rect",
    x0=0.94, x1=0.98, y0=-1, y1=0,
    fillcolor="red", opacity=0.1, line_width=0)

# -----------------------------
# LAYOUT
# -----------------------------
fig.update_layout(
    title="Sector Rotation Graph (RRG Style)",
    xaxis_title="RS Ratio (Relative Strength)",
    yaxis_title="RS Momentum",
    height=700
)

st.plotly_chart(fig, use_container_width=True)
