"""Carrier comparison for dispatchers: which carrier keeps its delivery promise most often, and at what cost."""
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Carrier comparison 2025", layout="wide")


@st.cache_data
def load_data():
    # Load the 2025 shipments (read once, then kept in cache)
    data = pd.read_csv("https://raw.githubusercontent.com/FH-Prevail/ailab/main/data/shipments_2025_clean.csv")
    # Make sure the numeric columns are numbers; empty cells stay empty (NaN), never 0
    for col in ["month", "on_time", "damaged", "cost_eur", "transit_days"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


data = load_data()

# Sidebar inputs
st.sidebar.header("Filters")
country = st.sidebar.selectbox("Destination country", ["All countries", "AT", "DE", "CZ", "HU", "IT", "SI"])
service = st.sidebar.radio("Service", ["All services", "Standard", "Express"])
months = st.sidebar.select_slider("Months", options=list(range(1, 13)), value=(1, 12))

st.title("Which carrier keeps its promise?")
st.caption("2025 shipments. Empty cells are left out of each average, never counted as 0.")

# Apply the filters
selected = data[data["month"].between(months[0], months[1])]
if country != "All countries":
    selected = selected[selected["country"] == country]
if service != "All services":
    selected = selected[selected["service"] == service]

# Carriers that have no shipments in this selection
all_carriers = sorted(data["carrier"].dropna().unique())
present_carriers = set(selected["carrier"].dropna().unique())
missing = [c for c in all_carriers if c not in present_carriers]
st.write("**Carriers without shipments in this selection:** " + (", ".join(missing) if missing else "none"))

# Empty selection: show the message and stop
if selected.empty:
    st.info("No shipments for this selection")
    st.stop()

# One row per carrier
grouped = selected.groupby("carrier")
table = pd.DataFrame({
    "Shipments": grouped.size(),
    "Known result": grouped["on_time"].count(),  # only non-empty on_time values
    "On time %": grouped["on_time"].mean() * 100,
    "Transit days": grouped["transit_days"].mean(),
    "Cost per shipment €": grouped["cost_eur"].mean(),
    "Damaged %": grouped["damaged"].mean() * 100,
})
table.index.name = "Carrier"

styled = table.style.format({
    "Shipments": "{:d}",
    "Known result": "{:d}",
    "On time %": "{:.1f}",
    "Transit days": "{:.2f}",
    "Cost per shipment €": "{:.2f}",
    "Damaged %": "{:.1f}",
}, na_rep="–")
st.dataframe(styled)

# Best carrier: at least 30 shipments with a known result
eligible = table[table["Known result"] >= 30]
if eligible.empty:
    st.write("No carrier has at least 30 shipments with a known result in this selection.")
else:
    best = eligible["On time %"].idxmax()
    st.write(
        f"**{best}** keeps its delivery promise most often: "
        f"{eligible.loc[best, 'On time %']:.1f} % on time "
        f"({int(eligible.loc[best, 'Known result'])} shipments with a known result)."
    )

# Bar chart of On time % by carrier
chart_data = table.reset_index()[["Carrier", "On time %"]].rename(columns={"On time %": "On time"}).dropna()
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("Carrier:N", sort=None, title="Carrier"),
        y=alt.Y("On time:Q", title="On time %", scale=alt.Scale(domain=[0, 100])),
        tooltip=["Carrier", alt.Tooltip("On time:Q", format=".1f")],
    )
)
st.altair_chart(chart)
