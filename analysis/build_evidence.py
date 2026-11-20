"""Freeze every number the session shows into evidence/results.json.

The notebooks (text, pictures and # CHECK lines), the README, the app test, the MCP
test and the Power BI check all read the files this script writes, so they show
exactly what the data says. Nothing is typed in by hand.

    python3 analysis/build_evidence.py

Writes
    evidence/results.json            every number of the session
    evidence/check_table.csv         reference cells the app, the MCP server and Power BI must match
    data/shipments_2025_clean.csv    the cleaned table (the checkpoint for block 2)

The metric contract (DATA_RULES) is implemented twice here: once on the raw export
(the reference) and once as plain averages on the cleaned table (how the app, the
MCP server and Power BI compute). The script stops if the two disagree, or if one
of the findings the session teaches does not hold in the data.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "shipments_2025.csv"
NOTES = ROOT / "data" / "carrier_notes.csv"
CLEAN = ROOT / "data" / "shipments_2025_clean.csv"
OUT = ROOT / "evidence" / "results.json"
CHECKS = ROOT / "evidence" / "check_table.csv"

EXPORT_DATE = pd.Timestamp("2025-12-31")     # the export ran at the end of this day
GRAMS_FROM = pd.Timestamp("2025-09-01")      # Wels writes grams into weight_kg from this day
COUNTRIES = ["AT", "DE", "CZ", "HU", "IT", "SI"]
COUNTRY_NAMES = {"AT": "Austria", "DE": "Germany", "CZ": "Czechia", "HU": "Hungary", "IT": "Italy",
                 "SI": "Slovenia"}
CARRIERS = ["Biber Freight", "Falke Transport", "Gams Cargo", "Luchs Logistik"]
MIN_SHIPMENTS = 30          # a carrier needs this many resolved shipments in a cell to be recommended

DATA_RULES = [
    "One row per shipment: drop rows that repeat a shipment_id (keep the first).",
    "Carrier names: trim spaces, drop ' GmbH' and write them in title case, which leaves four carriers.",
    "Weight: from 1 September 2025 the new scale at Wels writes grams into weight_kg; "
    "divide those rows by 1,000.",
    "On time: delivered on or before promised_date. Lost counts as late. Still in transit with the promised "
    "date already passed (on or before 31 December 2025) counts as late. Still in transit with the promised "
    "date after the export is not known yet: leave it out of the on-time rate and count it separately.",
    "Transit days: calendar days from ship_date to delivered_date, delivered shipments only.",
    "Damage rate: damaged shipments as a share of delivered shipments.",
    "Cost per shipment: the average of cost_eur over all shipments.",
]


# ---------------------------------------------------------------- the reference (raw export + rules)
def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW, parse_dates=["ship_date", "promised_date", "delivered_date"])


def apply_rules(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.drop_duplicates(subset="shipment_id", keep="first").copy()
    df["carrier"] = df["carrier"].str.strip().str.replace(r"\s+GmbH$", "", regex=True).str.title()
    grams = (df["warehouse"] == "Wels") & (df["ship_date"] >= GRAMS_FROM)
    df.loc[grams, "weight_kg"] = (df.loc[grams, "weight_kg"] / 1000).round(1)
    delivered = df["status"] == "delivered"
    overdue = (df["status"] == "in_transit") & (df["promised_date"] <= EXPORT_DATE)
    df["resolved"] = delivered | (df["status"] == "lost") | overdue
    df["is_on_time"] = delivered & (df["delivered_date"] <= df["promised_date"])
    df["is_delivered"] = delivered
    df["transit"] = (df["delivered_date"] - df["ship_date"]).dt.days
    df["month"] = df["ship_date"].dt.month
    return df


def reference_kpis(df: pd.DataFrame) -> dict:
    """The scorecard for one slice, computed from the rules with explicit counts."""
    resolved = df[df["resolved"]]
    delivered = df[df["is_delivered"]]
    n_resolved, n_on_time = int(len(resolved)), int(resolved["is_on_time"].sum())
    return {
        "shipments": int(len(df)),
        "resolved": n_resolved,
        "on_time": n_on_time,
        "late_or_lost": n_resolved - n_on_time,
        "not_known_yet": int(len(df) - n_resolved),
        "on_time_pct": pct(n_on_time / n_resolved) if n_resolved else None,
        "transit_days": round(float(delivered["transit"].mean()), 2) if len(delivered) else None,
        "cost_eur": round(float(df["cost_eur"].mean()), 2) if len(df) else None,
        "damaged": int(delivered["damaged"].sum()),
        "delivered": int(len(delivered)),
        "damage_pct": pct(delivered["damaged"].mean()) if len(delivered) else None,
    }


def pct(x: float) -> float:
    return round(float(x) * 100, 1)


def falke_on_gams_routes(resolved: pd.DataFrame) -> float:
    """Falke's on-time share if it had Gams' routes: its rate per country, weighted by Gams' shipments there."""
    gams = resolved[resolved["carrier"] == "Gams Cargo"].groupby("country").size()
    falke = resolved[resolved["carrier"] == "Falke Transport"].groupby("country")["is_on_time"].mean()
    return float((falke[gams.index] * gams).sum() / gams.sum())


# ---------------------------------------------------------------- the cleaned table (block 2 checkpoint)
def wrong_line(clean: pd.DataFrame) -> dict:
    """What the one wrong line of app/buggy_app.py does: on_time.fillna(0) counts 'not known yet' as late.

    The right numbers and the wrong ones, per carrier, for Italy (whole year), Germany Standard and December.
    """
    def view(part: pd.DataFrame) -> dict:
        filled = part.assign(on_time=part["on_time"].fillna(0))
        out = {}
        for carrier, g in sorted(part.groupby("carrier")):
            f = filled[filled["carrier"] == carrier]
            out[carrier] = {"shipments": int(len(g)),
                            "known_right": int(g["on_time"].count()), "known_wrong": int(f["on_time"].count()),
                            "right_pct": pct(g["on_time"].mean()), "wrong_pct": pct(f["on_time"].mean())}
        return out

    def top(v: dict, which: str) -> str:
        ok = {c: r[f"{which}_pct"] for c, r in v.items() if r[f"known_{which}"] >= MIN_SHIPMENTS}
        return max(ok, key=ok.get)

    not_known = clean["on_time"].isna()
    views = {"IT": view(clean[clean["country"] == "IT"]),
             "DE_Standard": view(clean[(clean["country"] == "DE") & (clean["service"] == "Standard")]),
             "December": view(clean[clean["month"] == 12])}
    return {"not_known_yet": int(not_known.sum()),
            "not_known_months": sorted(int(m) for m in clean.loc[not_known, "month"].unique()),
            **views,
            "december_best_right": top(views["December"], "right"),
            "december_best_wrong": top(views["December"], "wrong")}


def make_clean_table(df: pd.DataFrame) -> pd.DataFrame:
    """Columns where a plain average is the right KPI: empty means 'does not apply'."""
    out = df[["shipment_id", "ship_date", "promised_date", "delivered_date", "status", "carrier", "service",
              "warehouse", "country", "city", "distance_km", "weight_kg", "parcels", "cost_eur", "damaged",
              "customer_id", "month"]].copy()
    out["on_time"] = df["is_on_time"].astype("Int64").where(df["resolved"])
    out["transit_days"] = df["transit"].astype("Int64").where(df["is_delivered"])
    out["damaged"] = df["damaged"].astype("Int64").where(df["is_delivered"])
    for col in ["ship_date", "promised_date", "delivered_date"]:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    return out


def clean_kpis(t: pd.DataFrame) -> dict:
    """How the app, the MCP server and Power BI compute: plain averages of the cleaned table."""
    return {
        "shipments": int(len(t)),
        "on_time_pct": pct(t["on_time"].mean()) if t["on_time"].notna().any() else None,
        "transit_days": round(float(t["transit_days"].mean()), 2) if t["transit_days"].notna().any() else None,
        "cost_eur": round(float(t["cost_eur"].mean()), 2) if len(t) else None,
        "damage_pct": pct(t["damaged"].mean()) if t["damaged"].notna().any() else None,
    }


# ---------------------------------------------------------------- views
def scorecard(df: pd.DataFrame) -> dict:
    return {carrier: reference_kpis(part) for carrier, part in sorted(df.groupby("carrier"))}


def best(card: dict) -> dict | None:
    """Highest on-time rate among carriers with at least MIN_SHIPMENTS resolved shipments; cost breaks ties."""
    eligible = [(c, k) for c, k in card.items() if k["resolved"] >= MIN_SHIPMENTS]
    if not eligible:
        return None
    eligible.sort(key=lambda ck: (-ck[1]["on_time_pct"], ck[1]["cost_eur"]))
    winner, k = eligible[0]
    runner = eligible[1] if len(eligible) > 1 else None
    return {"carrier": winner, **k, "runner_up": runner[0] if runner else None,
            "runner_up_on_time_pct": runner[1]["on_time_pct"] if runner else None,
            "margin_pts": round(k["on_time_pct"] - runner[1]["on_time_pct"], 1) if runner else None}


def lazy_views(raw: pd.DataFrame) -> dict:
    """What a quick, unchecked analysis prints: no rules applied."""
    r = raw.copy()
    r["on_time"] = r["delivered_date"] <= r["promised_date"]       # a missing date compares as False: late
    nan_late = {c: pct(v) for c, v in r.groupby("carrier")["on_time"].mean().items()}
    d = raw.dropna(subset=["delivered_date"]).copy()
    d["on_time"] = d["delivered_date"] <= d["promised_date"]
    dropped = {c: pct(v) for c, v in d.groupby("carrier")["on_time"].mean().items()}
    return {
        "on_time_pct_missing_as_late": nan_late,
        "on_time_pct_missing_dropped": dropped,
        "rows_per_name": {c: int(v) for c, v in raw["carrier"].value_counts().items()},
        "ranking_missing_as_late": [c for c, _ in sorted(nan_late.items(), key=lambda kv: -kv[1])],
        "ranking_missing_dropped": [c for c, _ in sorted(dropped.items(), key=lambda kv: -kv[1])],
    }


def luchs_repeats_only(raw: pd.DataFrame) -> float:
    """Luchs with only the repeats removed, a missing date still counted as late: separates the two effects."""
    d = raw.drop_duplicates(subset="shipment_id")
    d = d[d["carrier"] == "Luchs Logistik"]
    return pct((d["delivered_date"] <= d["promised_date"]).mean())


def hand_example(raw: pd.DataFrame, df: pd.DataFrame) -> dict:
    """Six real rows that show every part of the on-time rule; small enough to compute by hand."""
    luchs = df[df["carrier"] == "Luchs Logistik"]
    on_time = luchs[luchs["is_on_time"] & (luchs["month"] == 12)].iloc[0]
    dup_ids = raw[raw.duplicated(subset="shipment_id")]["shipment_id"]
    late = luchs[(luchs["is_delivered"]) & ~luchs["is_on_time"] & luchs["shipment_id"].isin(dup_ids)].iloc[-1]
    lost = df[df["status"] == "lost"].iloc[-1]
    overdue = df[(df["status"] == "in_transit") & (df["promised_date"] <= EXPORT_DATE)].iloc[0]
    open_ = df[(df["status"] == "in_transit") & (df["promised_date"] > EXPORT_DATE)].iloc[-1]
    ids = [on_time["shipment_id"], late["shipment_id"], late["shipment_id"], lost["shipment_id"],
           overdue["shipment_id"], open_["shipment_id"]]
    rows = []
    for i, sid in enumerate(ids):
        r = raw[raw["shipment_id"] == sid].iloc[0]
        rows.append({k: (v.strftime("%Y-%m-%d") if isinstance(v, pd.Timestamp) else ("" if pd.isna(v) else v))
                     for k, v in r[["shipment_id", "ship_date", "promised_date", "delivered_date", "status",
                                     "carrier"]].items()})
        rows[-1]["repeat"] = i == 2
    verdict = ["on time", "late", "repeat of the row above: drop it", "lost: late",
               "in transit, promise already passed: late", "in transit, promise after the export: not known yet"]
    for row, v in zip(rows, verdict):
        row["verdict"] = v
    with_date = [r for r in rows if r["delivered_date"]]
    on_time_rows = sum(r["delivered_date"] <= r["promised_date"] for r in with_date)
    return {"rows": rows, "shipments": 5, "resolved": 4, "on_time": 1, "on_time_pct": pct(1 / 4),
            # Two shortcuts an unchecked analysis takes, on the same six rows:
            "dropped_rows_with_date": len(with_date), "dropped_on_time": on_time_rows,
            "dropped_on_time_pct": pct(on_time_rows / len(with_date)),        # rows without a date dropped
            "all_rows": len(rows), "all_rows_on_time_pct": pct(on_time_rows / len(rows))}  # missing = late, repeat kept


def check_rows(df: pd.DataFrame) -> list[dict]:
    """Reference cells: the filters the app, the MCP server and Power BI are tested on."""
    cells = [("all carriers, whole year", {}, None)]
    cells += [(f"{c}, whole year", {"carrier": c}, None) for c in CARRIERS]
    cells += [(f"Italy, {c}", {"country": "IT", "carrier": c}, None) for c in CARRIERS]
    cells += [(f"Italy Express, {c}", {"country": "IT", "service": "Express", "carrier": c}, None)
              for c in ["Biber Freight", "Falke Transport", "Gams Cargo"]]
    cells += [(f"Germany Standard, {c}", {"country": "DE", "service": "Standard", "carrier": c}, None)
              for c in ["Biber Freight", "Falke Transport", "Luchs Logistik"]]
    cells += [("Czechia, Gams Cargo (no shipments)", {"country": "CZ", "carrier": "Gams Cargo"}, None),
              ("Luchs Logistik, December", {"carrier": "Luchs Logistik"}, 12),
              ("Luchs Logistik Express, whole year", {"carrier": "Luchs Logistik", "service": "Express"}, None)]
    out = []
    for name, f, month in cells:
        part = df
        for col, val in f.items():
            part = part[part[col] == val]
        if month:
            part = part[part["month"] == month]
        k = reference_kpis(part)
        out.append({"check": name, "country": f.get("country", ""), "service": f.get("service", ""),
                    "carrier": f.get("carrier", ""), "month": str(month or ""), **k})
    return out


# ---------------------------------------------------------------- the findings the session teaches
def assert_findings(r: dict) -> list[str]:
    """Stop the build if the data no longer shows what the notebooks say."""
    failed = []

    def need(ok: bool, what: str) -> None:
        if not ok:
            failed.append(what)

    p = r["paradox"]
    need(p["overall"]["Falke Transport"] - p["overall"]["Gams Cargo"] >= 1.0, "Falke ahead of Gams overall by 1 pt")
    for c, v in p["countries"].items():
        need(v["Gams Cargo"] - v["Falke Transport"] >= 3.0, f"Gams ahead of Falke in {c} by 3 pts")
        need(v["gams_resolved"] >= 150 and v["falke_resolved"] >= 60, f"group sizes in {c}")
    need(p["overall"]["Gams Cargo"] - p["falke_on_gams_routes_pct"] >= 5.0, "on Gams' routes, Falke is 5 pts behind")
    bc = r["by_country"]
    for c in ["Biber Freight", "Falke Transport", "Gams Cargo"]:   # "harder routes": every carrier there is below its Austria rate
        for land in ["HU", "IT", "SI"]:
            need(bc[land][c]["on_time_pct"] < bc["AT"][c]["on_time_pct"], f"{c} on time less often in {land} than in AT")
    e = r["express"]
    need(e["Luchs Logistik"]["Standard"]["on_time_pct"] - e["Luchs Logistik"]["Express"]["on_time_pct"] >= 30,
         "Luchs Express misses its promise far more often")
    need(abs(e["Luchs Logistik"]["Standard"]["transit_days"] - e["Luchs Logistik"]["Express"]["transit_days"]) <= 0.5,
         "Luchs Express hardly faster")
    for c in ["Biber Freight", "Falke Transport", "Gams Cargo"]:
        need(e[c]["Standard"]["transit_days"] - e[c]["Express"]["transit_days"] >= 1.0, f"{c} Express a day faster")
    need(r["checks"]["luchs_rest_of_year_on_time_pct"] - r["checks"]["luchs_december_on_time_pct"] >= 15,
         "Luchs collapses in December")
    dmg = {c: v["damage_pct"] for c, v in r["overall"].items()}
    need(dmg["Biber Freight"] >= 2.5 * max(v for c, v in dmg.items() if c != "Biber Freight"), "Biber damages most")
    std_cost = {c: e[c]["Standard"]["cost_eur"] for c in e}
    need(min(std_cost, key=std_cost.get) == "Biber Freight", "Biber cheapest for Standard")
    need(r["luchs_effect_of_rules"]["clean"] - r["luchs_effect_of_rules"]["raw_missing_as_late"] >= 4,
         "the repeats make Luchs look worse by 4 pts")
    need(r["data"]["duplicate_rows_luchs"] / r["data"]["duplicate_rows"] >= 0.6, "repeats are mostly Luchs")
    need(r["data"]["weight_max_raw"] > 100_000 and r["data"]["grams_rows"] >= 500, "grams visible")
    need(r["data"]["carrier_spellings"] == 6 and len(r["data"]["carriers"]) == 4, "six spellings, four carriers")
    need(r["data"]["overdue_in_transit"] > 0 and r["data"]["not_known_yet"] > 0, "both kinds of in-transit rows")
    w = r["wrong_line"]
    need(w["not_known_months"] == [12], "every 'not known yet' shipment is from December")
    need(w["december_best_right"] != w["december_best_wrong"], "the wrong line changes December's best carrier")
    need(w["IT"]["Gams Cargo"]["right_pct"] != w["IT"]["Gams Cargo"]["wrong_pct"]
         and w["IT"]["Falke Transport"]["right_pct"] == w["IT"]["Falke Transport"]["wrong_pct"],
         "Italy: the wrong line moves Gams, not Falke")
    h = r["hand_example"]
    need(len({h["on_time_pct"], h["dropped_on_time_pct"], h["all_rows_on_time_pct"]}) == 3, "hand example: three answers")
    return failed


def main() -> None:
    raw = load_raw()
    df = apply_rules(raw)
    notes = pd.read_csv(NOTES)
    clean_table = make_clean_table(df)

    grams = (raw["warehouse"] == "Wels") & (raw["ship_date"] >= GRAMS_FROM)
    wels = raw[raw["warehouse"] == "Wels"]
    wels_median_before = float(wels[wels["ship_date"] < GRAMS_FROM]["weight_kg"].median())
    wels_median_after = float(wels[wels["ship_date"] >= GRAMS_FROM]["weight_kg"].median())
    dup_rows = int(raw.duplicated(subset="shipment_id").sum())
    raw_luchs = raw[raw["carrier"] == "Luchs Logistik"]
    in_transit = df[df["status"] == "in_transit"]

    data = {
        "rows": int(len(raw)),
        "shipments": int(raw["shipment_id"].nunique()),
        "duplicate_rows": dup_rows,
        "duplicate_rows_luchs": int(raw_luchs.duplicated(subset="shipment_id").sum()),
        "columns": list(raw.columns),
        "clean_columns": list(clean_table.columns),
        "first_ship_date": raw["ship_date"].min().strftime("%Y-%m-%d"),
        "last_ship_date": raw["ship_date"].max().strftime("%Y-%m-%d"),
        "export_date": EXPORT_DATE.strftime("%Y-%m-%d"),
        "carrier_spellings": int(raw["carrier"].nunique()),
        "carrier_spelling_counts": {c: int(v) for c, v in raw["carrier"].value_counts().items()},
        "carriers": sorted(df["carrier"].unique().tolist()),
        "countries": COUNTRIES,
        "country_names": COUNTRY_NAMES,
        "cities": int(raw["city"].nunique()),
        "customers": int(raw["customer_id"].nunique()),
        "warehouses": sorted(raw["warehouse"].unique().tolist()),
        "status_counts": {k: int(v) for k, v in df["status"].value_counts().items()},
        "overdue_in_transit": int((in_transit["promised_date"] <= EXPORT_DATE).sum()),
        "not_known_yet": int((in_transit["promised_date"] > EXPORT_DATE).sum()),
        "resolved": int(df["resolved"].sum()),
        "raw_rows_without_delivery_date": int(raw["delivered_date"].isna().sum()),
        "raw_status_rows": {k: int(v) for k, v in raw["status"].value_counts().items()},
        "grams_rows": int(grams.sum()),
        "grams_shipments": int((df["warehouse"].eq("Wels") & df["ship_date"].ge(GRAMS_FROM)).sum()),
        "wels_median_weight_before_sep": round(wels_median_before, 1),
        "wels_median_weight_from_sep": round(wels_median_after, 1),
        "weight_max_raw": float(raw["weight_kg"].max()),
        "weight_mean_raw": round(float(raw["weight_kg"].mean()), 1),
        "weight_mean_clean": round(float(df["weight_kg"].mean()), 1),
        "weight_max_clean": float(df["weight_kg"].max()),
        "weight_median_clean": round(float(df["weight_kg"].median()), 1),
        "express_share_pct": pct((df["service"] == "Express").mean()),
        "notes": int(len(notes)),
        "min_shipments_to_recommend": MIN_SHIPMENTS,
        "rules": DATA_RULES,
    }

    overall = scorecard(df)
    by_country = {c: scorecard(df[df["country"] == c]) for c in COUNTRIES}
    by_country_service = {c: {s: scorecard(df[(df["country"] == c) & (df["service"] == s)])
                              for s in ["Standard", "Express"]} for c in COUNTRIES}
    express = {carrier: {s: reference_kpis(part[part["service"] == s]) for s in ["Standard", "Express"]}
               for carrier, part in sorted(df.groupby("carrier"))}
    resolved = df[df["resolved"]]
    monthly = {carrier: {int(m): pct(v) for m, v in part.groupby("month")["is_on_time"].mean().items()}
               for carrier, part in sorted(resolved.groupby("carrier"))}

    both = [c for c in COUNTRIES if "Gams Cargo" in by_country[c] and "Falke Transport" in by_country[c]]
    paradox = {
        "overall": {"Gams Cargo": overall["Gams Cargo"]["on_time_pct"],
                    "Falke Transport": overall["Falke Transport"]["on_time_pct"]},
        "countries": {c: {"Gams Cargo": by_country[c]["Gams Cargo"]["on_time_pct"],
                          "Falke Transport": by_country[c]["Falke Transport"]["on_time_pct"],
                          "gams_resolved": by_country[c]["Gams Cargo"]["resolved"],
                          "falke_resolved": by_country[c]["Falke Transport"]["resolved"]} for c in both},
        "gams_share_in_hu_it_si_pct": pct(df[df["carrier"] == "Gams Cargo"]["country"].isin(["HU", "IT", "SI"]).mean()),
        "falke_share_in_at_pct": pct((df[df["carrier"] == "Falke Transport"]["country"] == "AT").mean()),
        # The fair test: Falke's on-time rate in each country, weighted like Gams' shipments (its routes)
        "falke_on_gams_routes_pct": pct(falke_on_gams_routes(resolved)),
    }

    lazy = lazy_views(raw)
    results = {
        "data": data,
        "hand_example": hand_example(raw, df),
        "lazy": lazy,
        "luchs_effect_of_rules": {"raw_missing_as_late": lazy["on_time_pct_missing_as_late"]["Luchs Logistik"],
                                  "repeats_removed_missing_as_late": luchs_repeats_only(raw),
                                  "clean": overall["Luchs Logistik"]["on_time_pct"]},
        "overall": overall,
        "by_country": by_country,
        "by_country_service": by_country_service,
        "best_by_country": {c: best(by_country[c]) for c in COUNTRIES},
        "best_by_country_standard": {c: best(by_country_service[c]["Standard"]) for c in COUNTRIES},
        "express": express,
        "monthly_on_time_pct": monthly,
        "monthly_shipments": {int(m): int(v) for m, v in df.groupby("month").size().items()},
        "paradox": paradox,
        "wrong_line": wrong_line(clean_table),
        "checks": {
            "luchs_december_on_time_pct": monthly["Luchs Logistik"][12],
            "luchs_rest_of_year_on_time_pct": pct(resolved[(resolved["carrier"] == "Luchs Logistik") &
                                                           (resolved["month"] < 12)]["is_on_time"].mean()),
        },
    }

    # The second implementation must agree with the reference in every cell.
    disagreements = []
    for name, f, month in [(r["check"], {k: r[k] for k in ["country", "service", "carrier"] if r[k]}, r["month"])
                           for r in check_rows(df)]:
        part = clean_table
        for col, val in f.items():
            part = part[part[col] == val]
        if month:
            part = part[part["month"] == int(month)]
        if name.startswith("Luchs Logistik, December") and part.empty:
            raise SystemExit("the December cell selected nothing: the cross-check would be empty")
        ref = reference_kpis(df[df["shipment_id"].isin(part["shipment_id"])])
        got = clean_kpis(part)
        for key, val in got.items():
            if val != ref[key]:
                disagreements.append(f"{name}: {key} {val} != {ref[key]}")
    if disagreements:
        raise SystemExit("cleaned table and reference disagree:\n" + "\n".join(disagreements))

    failed = assert_findings(results)
    if failed:
        raise SystemExit("findings the session teaches do not hold:\n" + "\n".join(failed))

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    pd.DataFrame(check_rows(df)).to_csv(CHECKS, index=False, lineterminator="\n")
    clean_table.to_csv(CLEAN, index=False, lineterminator="\n")
    print(f"wrote {OUT.relative_to(ROOT)}, {CHECKS.relative_to(ROOT)}, {CLEAN.relative_to(ROOT)}; "
          f"every finding holds, both implementations agree")


if __name__ == "__main__":
    main()
