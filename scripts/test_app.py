"""Test the reference app against the reference cells in evidence/check_table.csv.

    python3 scripts/test_app.py            # the reference app/app.py
    python3 scripts/test_app.py my_app.py  # any app that follows the spec (same widgets)

Runs the app headless with Streamlit's AppTest, sets the sidebar like a user would
and compares every carrier row the app shows with the check table: shipments,
resolved, on-time rate, transit days, cost, damage. An empty selection must say
"No shipments". Ends with ALL APP CHECKS PASSED or lists what differs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app" / "app.py"
CHECKS = pd.read_csv(ROOT / "evidence" / "check_table.csv", dtype={"month": str}).fillna("")
COLUMNS = {"Shipments": "shipments", "Known result": "resolved", "On time %": "on_time_pct",
           "Transit days": "transit_days", "Cost per shipment €": "cost_eur", "Damaged %": "damage_pct"}


def run(country: str, service: str, month: str) -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=90).run()
    at.sidebar.selectbox[0].select(country or "All countries").run()
    at.sidebar.radio[0].set_value(service or "All services").run()
    if month:
        at.sidebar.select_slider[0].set_range(int(month), int(month)).run()
    assert not at.exception, at.exception
    return at


def main() -> None:
    problems, compared = [], 0
    for (country, service, month), group in CHECKS.groupby(["country", "service", "month"], sort=False):
        at = run(country, service, month)
        for _, row in group.iterrows():
            if row["carrier"] == "":
                continue                                     # the all-carriers row has no line in the app
            if int(row["shipments"]) == 0:
                shown = at.dataframe[0].value.index.tolist() if at.dataframe else []
                said = any(f"No shipments in this selection" in c.value and row["carrier"] in c.value
                           for c in at.caption)
                if row["carrier"] in shown or not said:
                    problems.append(f"{row['check']}: a carrier without shipments must be named, not shown as a row")
                compared += 1
                continue
            table = at.dataframe[0].value
            if row["carrier"] not in table.index:
                problems.append(f"{row['check']}: carrier missing in the app")
                continue
            for col, key in COLUMNS.items():
                compared += 1
                got, want = float(table.loc[row["carrier"], col]), float(row[key])
                if abs(got - want) > 1e-6:
                    problems.append(f"{row['check']}: {col} app {got} vs reference {want}")

    # An empty selection must say "No shipments", not show zeros. Find one the sidebar can reach.
    clean = pd.read_csv(ROOT / "data" / "shipments_2025_clean.csv")
    sizes = clean.groupby(["country", "service", "month"]).size()
    full = pd.MultiIndex.from_product([sorted(clean["country"].unique()), ["Standard", "Express"], range(1, 13)])
    empty_cells = [cell for cell in full if cell not in sizes.index]
    if not empty_cells:
        print("every sidebar selection has shipments; the empty case is the carrier without shipments above")
    else:
        country, service, month = empty_cells[0]
        at = AppTest.from_file(str(APP), default_timeout=90).run()
        at.sidebar.selectbox[0].select(country).run()
        at.sidebar.radio[0].set_value(service).run()
        at.sidebar.select_slider[0].set_range(month, month).run()
        if not any("No shipments" in w.value for w in at.warning) or at.dataframe:
            problems.append(f"empty selection {country} {service} month {month} does not say 'No shipments'")
        else:
            print(f"empty selection {country} {service} month {month}: says 'No shipments'")

    if problems:
        print("\n".join(problems))
        raise SystemExit(f"{len(problems)} APP CHECKS FAILED")
    print(f"{compared} values compared with evidence/check_table.csv; ALL APP CHECKS PASSED")


if __name__ == "__main__":
    main()
