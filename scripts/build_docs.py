"""Write README.md, data/README.md and powerbi/README.md from the templates in scripts/templates/.

    python3 scripts/build_docs.py

Placeholders «path.to.value» are filled from evidence/results.json, like the notebooks, so a
number in a README always matches the data. A few named placeholders (links, tables) are made here.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_notebooks import EVIDENCE, KEY1, KEY2, KEY3, LINKS, PRETTY_SRC, WORDS, colab, fill  # noqa: E402

SESSION_DATE = "20 November 2026"
CHECKED_DATE = "16 November 2026"
TARGETS = {"README.md": "README.md", "data_README.md": "data/README.md", "powerbi_README.md": "powerbi/README.md"}


def best_table() -> str:
    names = EVIDENCE["data"]["country_names"]
    lines = ["| Country | Most often on time | Second | Shipments with a known result (first carrier) |", "|---|---|---|---|"]
    for code, b in EVIDENCE["best_by_country"].items():
        lines.append(f"| {names[code]} | {b['carrier']}, {b['on_time_pct']:.1f} % | {b['runner_up']}, "
                     f"{b['runner_up_on_time_pct']:.1f} % | {b['resolved']:,} |")
    return "\n".join(lines)


def trace_worksheet() -> str:
    """traces/README.md: the recordings of notebook 3, readable without Python, same formatting as the notebook."""
    space = {"json": json}
    exec(PRETTY_SRC, space)
    pretty = space["pretty"]
    out = ["# Recorded traces: a worksheet", "",
           "Real recordings (traces) of a small model (Claude Haiku) that used the shipments MCP server through Claude Code. "
           "It was allowed to use only the four tools. The same traces are in notebook 3, section 3. For traces 1 to 3, "
           "answer these questions with your partner (trace 4 is the live demo at the start of notebook 3):", "",
           "1. Which tool did it call, with which inputs? Were they the right ones?",
           "2. Does every number in the answer come from a tool result, or from a calculation with one?",
           "3. Is there a claim that no tool supports?", "",
           "Trace 3 contains a note that we put into our data on purpose. For trace 3, also answer these questions "
           "before you open **What to notice**:", "",
           "1. What does that note try to make the AI do?",
           "2. Did the model follow it? Did it tell you that the note was there?",
           "3. The tools are read-only. What does that protect, and what does it not protect?",
           "4. Check one more claim of the answer against the results.", ""]
    for path in sorted((ROOT / "traces").glob("*.json")):
        t = json.loads(path.read_text(encoding="utf-8"))
        out += [f"## {path.stem.replace('_', ' ').capitalize()}", "", f"**Question:** {t['question']}", ""]
        for step in t["steps"]:
            args = ", ".join(f"{k}={v!r}" for k, v in step["args"].items())
            out += [f"**Tool call:** `{step['tool']}({args})`", "", "```", pretty(step["result"]), "```", ""]
        out += [f"**Answer:** {t['answer']}", "", f"*Recorded {t['recorded']} with {t['model']}; host: {t['host']}.*", ""]
        key = {"1_supported": KEY1, "2_unsupported": KEY2, "3_poisoned_note": KEY3}.get(path.stem)
        if key:
            out += [fill(key).strip(), ""]
    return "\n".join(out)


def main() -> None:
    named = {"«SESSION_DATE»": SESSION_DATE, "«CHECKED_DATE»": CHECKED_DATE, "«COLAB1»": colab(1),
             "«COLAB2»": colab(2), "«COLAB3»": colab(3), "«LINK_STARTER»": LINKS["starter"]["edit"],
             "«LINK_REFERENCE»": LINKS["reference"]["edit"], "«BEST_TABLE»": best_table(), "«WORDS»": WORDS}
    for template, target in TARGETS.items():
        text = (ROOT / "scripts" / "templates" / template).read_text(encoding="utf-8")
        for key, val in named.items():
            text = text.replace(key, val)
        text = fill(text)
        if "«" in text:
            raise SystemExit(f"unfilled placeholder in {target}: {re.findall(r'«[^»]+»', text)[:3]}")
        out = ROOT / target
        out.parent.mkdir(exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
        print("wrote", target)
    (ROOT / "traces" / "README.md").write_text(trace_worksheet(), encoding="utf-8", newline="\n")
    print("wrote traces/README.md")


if __name__ == "__main__":
    main()
