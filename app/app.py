"""Carrier Scorecard: which carrier keeps its promise, by country and service?

The reference app for hands-on 2 of the AI Lab session. It reads the cleaned
shipments table (the metric contract is already applied there), so every KPI is a
plain average:

    on-time rate   = average of on_time       (1 on time, 0 late or lost, empty = not known yet)
    transit days   = average of transit_days  (empty unless delivered)
    cost/shipment  = average of cost_eur
    damage rate    = average of damaged       (empty unless delivered)

Run it in the browser: paste this file into https://edit.share.stlite.net
Run it on your computer: pip install streamlit pandas altair, then streamlit run app.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/FH-Prevail/ailab/main/data/shipments_2025_clean.csv"
LOCAL_FILE = Path(__file__).resolve().parent.parent / "data" / "shipments_2025_clean.csv"
MIN_RESOLVED = 30   # fewer resolved shipments than this: too few to recommend a carrier

COUNTRIES = {"AT": "Austria", "DE": "Germany", "CZ": "Czechia", "HU": "Hungary", "IT": "Italy", "SI": "Slovenia"}
COLORS = {"Biber Freight": "#0B5CAD", "Falke Transport": "#E66A1F", "Gams Cargo": "#1B9E5A",
          "Luchs Logistik": "#D04F95"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@st.cache_data
def load_data() -> pd.DataFrame:
    """The cleaned table: from the course repository, or from the data folder if it is next to the app."""
    source = LOCAL_FILE if LOCAL_FILE.exists() else DATA_URL
    return pd.read_csv(source, parse_dates=["ship_date", "promised_date", "delivered_date"])


def scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """One row per carrier with the five KPIs of the metric contract."""
    table = df.groupby("carrier").agg(
        shipments=("shipment_id", "count"),
        resolved=("on_time", "count"),                 # count() skips empty cells: the 'not known yet' ones
        on_time_pct=("on_time", "mean"),
        transit_days=("transit_days", "mean"),
        cost_eur=("cost_eur", "mean"),
        damage_pct=("damaged", "mean"),
    )
    table["on_time_pct"] = (table["on_time_pct"] * 100).round(1)
    table["damage_pct"] = (table["damage_pct"] * 100).round(1)
    table["transit_days"] = table["transit_days"].round(2)
    table["cost_eur"] = table["cost_eur"].round(2)
    return table.sort_values("on_time_pct", ascending=False)


st.set_page_config(page_title="Carrier Scorecard", layout="wide")
st.title("Carrier Scorecard")
st.caption("Shipments of 2025, cleaned with the metric contract. Pick a country and a service on the left.")

data = load_data()

# ---------------------------------------------------------------- the filters
with st.sidebar:
    st.header("Your selection")
    country = st.selectbox("Destination country", ["All countries"] + list(COUNTRIES),
                           format_func=lambda c: COUNTRIES.get(c, c))
    service = st.radio("Service", ["All services", "Standard", "Express"])
    first, last = st.select_slider("Months", options=list(range(1, 13)), value=(1, 12),
                                   format_func=lambda m: MONTHS[m - 1])

selection = data[data["month"].between(first, last)]
if country != "All countries":
    selection = selection[selection["country"] == country]
if service != "All services":
    selection = selection[selection["service"] == service]

where = COUNTRIES.get(country, "All countries")
months = MONTHS[first - 1] if first == last else f"{MONTHS[first - 1]} to {MONTHS[last - 1]}"
st.subheader(f"{where}, {service.lower()}, {months}")

# ---------------------------------------------------------------- the answer
if selection.empty:
    st.warning("No shipments for this selection.")
    st.stop()

table = scorecard(selection)
eligible = table[table["resolved"] >= MIN_RESOLVED]
if eligible.empty:
    st.info(f"Too few shipments to recommend a carrier: none has {MIN_RESOLVED} or more with a known result.")
else:
    top = eligible.index[0]
    st.success(f"Most often on time: **{top}**, {eligible.loc[top, 'on_time_pct']:.1f} % "
               f"of {int(eligible.loc[top, 'resolved'])} shipments with a known result.")

shown = table.rename(columns={
    "shipments": "Shipments", "resolved": "Known result", "on_time_pct": "On time %",
    "transit_days": "Transit days", "cost_eur": "Cost per shipment €", "damage_pct": "Damaged %"})
shown.index.name = "Carrier"
st.dataframe(shown, width="stretch")

missing = [carrier for carrier in COLORS if carrier not in table.index]
if missing:
    st.caption(f"No shipments in this selection: {', '.join(missing)}.")
not_known = int(table["shipments"].sum() - table["resolved"].sum())
if not_known:
    st.caption(f"{not_known} shipments were still on their way at the end of the export with the promised "
               "date ahead; they are left out of the on-time rate.")

left, right = st.columns(2)
with left:
    st.markdown("**On time %**")
    bars = alt.Chart(table.reset_index()).mark_bar().encode(
        x=alt.X("on_time_pct:Q", title="On time %", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("carrier:N", title=None, sort="-x"),
        color=alt.Color("carrier:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values())),
                        legend=None),
        tooltip=["carrier", "on_time_pct", "resolved"],
    )
    st.altair_chart(bars, width="stretch")
with right:
    st.markdown("**On time % by month**")
    monthly = (selection.dropna(subset=["on_time"]).groupby(["month", "carrier"])["on_time"].mean() * 100)
    monthly = monthly.round(1).reset_index(name="on_time_pct")
    monthly["month_name"] = [MONTHS[m - 1] for m in monthly["month"]]
    lines = alt.Chart(monthly).mark_line(point=True).encode(
        x=alt.X("month_name:O", title=None, sort=MONTHS),
        y=alt.Y("on_time_pct:Q", title="On time %", scale=alt.Scale(zero=False)),
        color=alt.Color("carrier:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values())),
                        title=None),
        tooltip=["carrier", "month_name", "on_time_pct"],
    )
    st.altair_chart(lines, width="stretch")

with st.expander("How the numbers are made"):
    st.markdown(
        "- One row per shipment; carrier names cleaned; Wels weights from September converted from grams.\n"
        "- **On time**: delivered on or before the promised date. Lost counts as late. Still on its way with "
        "the promised date passed counts as late. Still on its way with the promised date ahead is not known "
        "yet and left out.\n"
        "- **Transit days**: calendar days from shipping to delivery, delivered shipments only.\n"
        "- **Damaged %**: damaged shipments among delivered ones. **Cost**: average cost per shipment.\n"
        f"- A carrier is recommended only with at least {MIN_RESOLVED} shipments with a known result.\n"
        "- These are observations from 2025, a starting point for the 2027 contracts, not proof."
    )
