"""Test the MCP server the way an AI app uses it: start it, list its tools, call them.

    python3 scripts/test_mcp.py

Starts mcp_server/shipments_server.py as a subprocess over stdio (exactly as Claude
Code, Claude Desktop or notebook 3 do), checks the tool list, compares
carrier_scorecard with evidence/check_table.csv, and checks the bounded results,
the clear error for a wrong input and the "no shipments" answer. Ends with
ALL MCP CHECKS PASSED.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pandas as pd
from mcp import ClientSession, StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "shipments_server.py"
CHECKS = pd.read_csv(ROOT / "evidence" / "check_table.csv", dtype={"month": str}).fillna("")
KEYS = {"shipments": "shipments", "known_result": "resolved", "on_time_pct": "on_time_pct",
        "transit_days": "transit_days", "cost_eur": "cost_eur", "damaged_pct": "damage_pct"}


def payload(result) -> dict:
    return result.structured_content if getattr(result, "structured_content", None) else json.loads(result.content[0].text)


async def main() -> None:
    problems, compared = [], 0
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names = sorted(t.name for t in (await session.list_tools()).tools)
            if names != ["carrier_notes", "carrier_scorecard", "late_shipments", "list_carriers"]:
                problems.append(f"tool list {names}")

            for _, row in CHECKS.iterrows():
                if not row["carrier"]:
                    continue
                args = {"country": row["country"] or "all", "service": row["service"] or "all"}
                if row["month"]:
                    args.update(first_month=int(row["month"]), last_month=int(row["month"]))
                card = payload(await session.call_tool("carrier_scorecard", args))
                found = {c["carrier"]: c for c in card.get("carriers", [])}
                if int(row["shipments"]) == 0:
                    if row["carrier"] in found or row["carrier"] not in card.get("carriers_without_shipments", []):
                        problems.append(f"{row['check']}: should be listed without shipments")
                    compared += 1
                    continue
                for key, ref in KEYS.items():
                    compared += 1
                    got = found.get(row["carrier"], {}).get(key)
                    if got is None or abs(float(got) - float(row[ref])) > 1e-6:
                        problems.append(f"{row['check']}: {key} server {got} vs reference {row[ref]}")

            late = payload(await session.call_tool("late_shipments", {"carrier": "Luchs", "limit": 500}))
            if late["shown"] > 20:
                problems.append("late_shipments returns more than 20 rows")
            bad = await session.call_tool("carrier_scorecard", {"country": "Narnia"})
            text = bad.content[0].text if bad.content else ""
            if not bad.is_error or "Use one of" not in text:
                problems.append(f"wrong country gives no clear message: {text}")
            notes = payload(await session.call_tool("carrier_notes", {"carrier": "Biber Freight"}))
            if not any("AI assistants" in n["note"] for n in notes["notes"]):
                problems.append("the planted note for hands-on 3 is missing")
            carriers = payload(await session.call_tool("list_carriers", {}))
            served = {c["carrier"]: c["countries"] for c in carriers["result"]} if "result" in carriers else \
                {c["carrier"]: c["countries"] for c in carriers}
            if "CZ" in served.get("Gams Cargo", []) or "DE" in served.get("Gams Cargo", []):
                problems.append("Gams should not serve CZ or DE")

    if problems:
        print("\n".join(problems))
        raise SystemExit(f"{len(problems)} MCP CHECKS FAILED")
    print(f"{compared} values compared with evidence/check_table.csv; ALL MCP CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
