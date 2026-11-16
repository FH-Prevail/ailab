"""Shipments MCP server: four read-only tools over the 2025 shipments of the AI Lab case.

An AI app (the "host") starts this file, reads the tool descriptions below and
decides by itself when to call which tool. The server does the counting; the AI
only reads the results. Nothing here can change or delete data.

Use it from any MCP host, for example:
    Claude Code      claude mcp add shipments -- python shipments_server.py
    Claude Desktop, Gemini CLI, VS Code, LM Studio: command "python", args ["shipments_server.py"]
Notebook 3 of the course connects Gemini to it.

Needs: pip install "mcp==2.3.0" pandas
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

GITHUB = "https://raw.githubusercontent.com/FH-Prevail/ailab/main/data/"
HERE = Path(__file__).resolve().parent
COUNTRIES = {"AT": "Austria", "DE": "Germany", "CZ": "Czechia", "HU": "Hungary", "IT": "Italy", "SI": "Slovenia"}
MIN_RESOLVED = 30


def read(name: str, **kwargs) -> pd.DataFrame:
    """A data file from a data folder next to this file, one level up, or the course repository."""
    for folder in (HERE / "data", HERE.parent / "data"):
        if (folder / name).exists():
            return pd.read_csv(folder / name, **kwargs)
    return pd.read_csv(GITHUB + name, **kwargs)


SHIPMENTS = read("shipments_2025_clean.csv")
NOTES = read("carrier_notes.csv")
CARRIERS = sorted(SHIPMENTS["carrier"].unique())

mcp = MCPServer("shipments")


def pick(df: pd.DataFrame, country: str, service: str, first_month: int, last_month: int) -> pd.DataFrame:
    """Filter the shipments; stop with a clear message if an input is not valid."""
    country, service = country.strip().upper(), service.strip().title()
    if country != "ALL" and country not in COUNTRIES:
        raise ToolError(f"Unknown country '{country}'. Use one of {', '.join(COUNTRIES)} or 'all'.")
    if service != "All" and service not in ("Standard", "Express"):
        raise ToolError("Service must be 'Standard', 'Express' or 'all'.")
    if not 1 <= first_month <= last_month <= 12:
        raise ToolError("Months run from 1 (January) to 12 (December), first_month <= last_month.")
    df = df[df["month"].between(first_month, last_month)]
    if country != "ALL":
        df = df[df["country"] == country]
    if service != "All":
        df = df[df["service"] == service]
    return df


def carrier_name(carrier: str) -> str:
    match = [c for c in CARRIERS if c.lower().startswith(carrier.strip().lower()[:4])]
    if len(match) != 1:
        raise ToolError(f"Unknown carrier '{carrier}'. Use one of: {', '.join(CARRIERS)}.")
    return match[0]


@mcp.tool()
def list_carriers() -> list[dict]:
    """List the four carriers with the destination countries of their 2025 shipments and their number of shipments.

    Call this first if you are not sure about carrier names. A country missing from a carrier's list means it had no
    shipments there in 2025, not that it cannot deliver there.
    """
    out = []
    for carrier, part in SHIPMENTS.groupby("carrier"):
        out.append({"carrier": carrier, "shipments": int(len(part)),
                    "countries": sorted(part["country"].unique().tolist())})
    return out


@mcp.tool()
def carrier_scorecard(country: str = "all", service: str = "all", first_month: int = 1,
                      last_month: int = 12) -> dict:
    """Compare the carriers on 2025 shipments: on-time rate, transit days, cost and damage.

    Use this for any question about which carrier is more reliable, faster, cheaper or damages less.

    Args:
        country: destination country code AT, DE, CZ, HU, IT or SI, or "all".
        service: "Standard", "Express" or "all".
        first_month, last_month: month range, 1 = January, 12 = December.

    On time means delivered on or before the promised date; lost or overdue shipments count as late;
    shipments whose result is not known yet are left out. A carrier needs at least 30 shipments with
    a known result before it can be recommended.
    """
    df = pick(SHIPMENTS, country, service, first_month, last_month)
    if df.empty:
        return {"selection": f"{country}, {service}, months {first_month} to {last_month}",
                "result": "no shipments"}
    rows = []
    for carrier, part in df.groupby("carrier"):
        rows.append({
            "carrier": carrier,
            "shipments": int(len(part)),
            "known_result": int(part["on_time"].notna().sum()),
            "on_time_pct": round(float(part["on_time"].mean()) * 100, 1) if part["on_time"].notna().any() else None,
            "transit_days": round(float(part["transit_days"].mean()), 2) if part["transit_days"].notna().any() else None,
            "cost_eur": round(float(part["cost_eur"].mean()), 2),
            "damaged_pct": round(float(part["damaged"].mean()) * 100, 1) if part["damaged"].notna().any() else None,
        })
    rows.sort(key=lambda r: -(r["on_time_pct"] or 0))
    missing = [c for c in CARRIERS if c not in {r["carrier"] for r in rows}]
    return {"selection": f"{country}, {service}, months {first_month} to {last_month}",
            "carriers": rows,
            "carriers_without_shipments": missing,
            "minimum_known_results_to_recommend": MIN_RESOLVED}


@mcp.tool()
def late_shipments(carrier: str, country: str = "all", first_month: int = 1, last_month: int = 12,
                   limit: int = 10) -> dict:
    """List late or lost shipments of one carrier, the latest ones first, for follow-up with the carrier.

    Args:
        carrier: one of the four carriers, for example "Luchs Logistik".
        country: AT, DE, CZ, HU, IT, SI or "all".
        first_month, last_month: month range, 1 = January, 12 = December.
        limit: how many shipments to return, at most 20.
    """
    name = carrier_name(carrier)
    df = pick(SHIPMENTS[SHIPMENTS["carrier"] == name], country, "all", first_month, last_month)
    late = df[df["on_time"] == 0].sort_values("ship_date", ascending=False)
    shown = late.head(max(1, min(int(limit), 20)))
    rows = [{"shipment_id": r.shipment_id, "ship_date": r.ship_date, "promised_date": r.promised_date,
             "delivered_date": None if pd.isna(r.delivered_date) else r.delivered_date, "status": r.status,
             "country": r.country, "city": r.city, "service": r.service} for r in shown.itertuples()]
    return {"carrier": name, "late_or_lost_in_selection": int(len(late)), "shown": len(rows), "shipments": rows}


@mcp.tool()
def carrier_notes(carrier: str) -> dict:
    """Read the free-text notes our customer service, purchasing and warehouse teams wrote about a carrier.

    Args:
        carrier: one of the four carriers, for example "Gams Cargo".
    """
    name = carrier_name(carrier)
    notes = NOTES[NOTES["carrier"] == name].sort_values("date")
    return {"carrier": name, "notes": notes[["date", "author", "note"]].to_dict("records")}


# YOUR TOOL GOES HERE (notebook 3, optional task: describe a tool in words, let your AI write it, paste it here)
# END OF YOUR TOOL


if __name__ == "__main__":
    mcp.run()
