import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Carrier choice", layout="wide")

MIN_KNOWN = 30  # minimum shipments with a known result to rank a carrier


@st.cache_data
def load_data():
    data = pd.read_csv("https://raw.githubusercontent.com/FH-Prevail/ailab/main/data/shipments_2025_clean.csv")
    return data


data = load_data()
all_carriers = sorted(data["carrier"].dropna().unique())

st.title("Which carrier keeps its promise?")

# Sidebar inputs
country = st.sidebar.selectbox(
    "Destination country", ["All countries", "AT", "DE", "CZ", "HU", "IT", "SI"]
)
service = st.sidebar.radio("Service", ["All services", "Standard", "Express"])
month_from, month_to = st.sidebar.select_slider(
    "Months", options=list(range(1, 13)), value=(1, 12)
)

# Apply the filters
sel = data[(data["month"] >= month_from) & (data["month"] <= month_to)]
if country != "All countries":
    sel = sel[sel["country"] == country]
if service != "All services":
    sel = sel[sel["service"] == service]

# One row per carrier; mean() skips empty cells, count() counts non-empty ones
if sel.empty:
    table = pd.DataFrame()
else:
    g = sel.groupby("carrier")
    table = pd.DataFrame(
        {
            "Shipments": g.size(),
            "Known result": g["on_time"].count(),
            "On time %": g["on_time"].mean() * 100,
            "Transit days": g["transit_days"].mean(),
            "Cost per shipment €": g["cost_eur"].mean(),
            "Damaged %": g["damaged"].mean() * 100,
        }
    )

# Table or empty message
if table.empty:
    st.info("No shipments for this selection")
else:
    st.dataframe(
        table.style.format(
            {
                "Shipments": "{:d}",
                "Known result": "{:d}",
                "On time %": "{:.1f}",
                "Transit days": "{:.2f}",
                "Cost per shipment €": "{:.2f}",
                "Damaged %": "{:.1f}",
            },
            na_rep="–",
        ),
        use_container_width=True,
    )

# Best carrier among those with enough known results
if table.empty:
    eligible = pd.DataFrame()
else:
    eligible = table[table["Known result"] >= MIN_KNOWN].dropna(subset=["On time %"])
if eligible.empty:
    st.write(f"No carrier has at least {MIN_KNOWN} shipments with a known result, so no carrier can be named.")
else:
    top = eligible["On time %"].max()
    winners = eligible[eligible["On time %"] == top]
    names = ", ".join(winners.index)
    label = "Carriers" if len(winners) > 1 else "Carrier"
    st.write(
        f"**{label} {names}** {'have' if len(winners) > 1 else 'has'} the highest On time % "
        f"({top:.1f}%), among carriers with at least {MIN_KNOWN} shipments with a known result."
    )

# Carriers with no shipments in this selection
present = set(table.index) if not table.empty else set()
missing = [c for c in all_carriers if c not in present]
if missing:
    st.write("Carriers without shipments in this selection: " + ", ".join(missing))
else:
    st.write("Carriers without shipments in this selection: none")

# Bar chart of On time % by carrier (carriers with no known result are left out)
if not table.empty:
    chart_data = table.reset_index()[["carrier", "On time %"]].dropna()
    if not chart_data.empty:
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("carrier:N", title="Carrier", sort="-y"),
                y=alt.Y("On time %:Q", title="On time %", scale=alt.Scale(domain=[0, 100])),
                tooltip=["carrier", alt.Tooltip("On time %:Q", format=".1f")],
            )
        )
        st.altair_chart(chart, use_container_width=True)
