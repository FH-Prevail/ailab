"""Starter: proves that the data connection works. Replace all of this with your AI's app."""

import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/FH-Prevail/ailab/main/data/shipments_2025_clean.csv"

st.title("Your app goes here")
data = pd.read_csv(DATA_URL)
st.success(f"The data connection works: {len(data):,} shipments loaded.")
st.write("Now select everything in the editor on the left (Ctrl + A), paste the code your AI wrote, "
         "and click **Save**.")
st.dataframe(data.head(10))
