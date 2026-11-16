"""An app an AI wrote from the same spec. It runs, it looks right. Is it?

Notebook 2, extension: test it with the numbers you know and find the line that is wrong.
"""

import altair as alt
import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/FH-Prevail/ailab/main/data/shipments_2025_clean.csv"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@st.cache_data
def load():
    return pd.read_csv(DATA_URL)


data = load()
st.title("Carrier Scorecard")

with st.sidebar:
    country = st.selectbox("Destination country", ["All countries", "AT", "DE", "CZ", "HU", "IT", "SI"])
    service = st.radio("Service", ["All services", "Standard", "Express"])
    first, last = st.select_slider("Months", options=list(range(1, 13)), value=(1, 12))

df = data[data["month"].between(first, last)]
if country != "All countries":
    df = df[df["country"] == country]
if service != "All services":
    df = df[df["service"] == service]

if df.empty:
    st.warning("No shipments for this selection.")
    st.stop()

# One row per carrier with the KPIs
df = df.assign(on_time=df["on_time"].fillna(0))     # fill the gaps so the average works
table = df.groupby("carrier").agg(
    shipments=("shipment_id", "count"),
    known=("on_time", "count"),
    on_time=("on_time", "mean"),
    transit=("transit_days", "mean"),
    cost=("cost_eur", "mean"),
    damaged=("damaged", "mean"),
)
table["on_time"] = (table["on_time"] * 100).round(1)
table["damaged"] = (table["damaged"] * 100).round(1)
table = table.round({"transit": 2, "cost": 2}).sort_values("on_time", ascending=False)
table.columns = ["Shipments", "Known result", "On time %", "Transit days", "Cost per shipment €", "Damaged %"]

best = table[table["Known result"] >= 30]
if len(best):
    st.success(f"Most often on time: {best.index[0]} ({best['On time %'].iloc[0]} %)")
st.dataframe(table)
missing = sorted(set(data["carrier"]) - set(table.index))
if missing:
    st.caption("No shipments in this selection: " + ", ".join(missing))
st.altair_chart(alt.Chart(table.reset_index()).mark_bar().encode(x="On time %:Q", y=alt.Y("carrier:N", sort="-x")))
