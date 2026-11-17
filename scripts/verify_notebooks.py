"""Run the three notebooks like Colab and check every # CHECK line.

    python3 scripts/verify_notebooks.py           # local files (works before anything is published)
    python3 scripts/verify_notebooks.py --github  # the published files on GitHub

Each notebook runs in a fresh temporary folder, as in a new Colab session. Without
--github, a small local web server serves this repository and stands in for
raw.githubusercontent.com, so the notebooks run unchanged. Notebook 3's Gemini cells run
against a stand-in Gemini endpoint (scripts/fake_gemini.py) that asks for one tool call and
then answers: that tests the plumbing (key, model list, MCP host loop), not a real model.
After the run, notebook 2 tests the reference app (six of six checks must pass) and the app
with one wrong line (it must fail).

A CHECK line passes when every number in it appears in the cell's output, or, for a line
without numbers, when its text appears there. The notebooks stay saved without outputs.
Ends with ALL NOTEBOOK CHECKS PASSED.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
RAW = "https://raw.githubusercontent.com/FH-Prevail/ailab/main"
NOTEBOOKS = ["1_ask_your_data.ipynb", "2_build_the_app.ipynb", "3_give_the_ai_tools.ipynb"]
TEXT_APP = '''
# An app that shows its numbers as text ("85.1%", "1,234"), as AI-written apps often do: the test must still read them.
import pandas as pd
import streamlit as st
data = pd.read_csv(DATA)
country = st.sidebar.selectbox("Destination country", ["All countries", "AT", "DE", "CZ", "HU", "IT", "SI"])
service = st.sidebar.radio("Service", ["All services", "Standard", "Express"])
first, last = st.sidebar.select_slider("Months", options=list(range(1, 13)), value=(1, 12))
d = data[data["month"].between(first, last)]
if country != "All countries":
    d = d[d["country"] == country]
if service != "All services":
    d = d[d["service"] == service]
t = d.groupby("carrier").agg(**{"Known result": ("on_time", "count"), "On time %": ("on_time", "mean"),
                                "Damaged %": ("damaged", "mean")})
t["Known result"] = t["Known result"].map("{:,}".format)
t["On time %"] = (t["On time %"] * 100).map("{:.1f}%".format)
t["Damaged %"] = (t["Damaged %"] * 100).map("{:.1f} %".format)
st.dataframe(t.reset_index(), hide_index=True)
'''
EXTRA = {  # cells run after a notebook, not saved: they check what the notebook only offers
    "2_build_the_app.ipynb": [
        "import urllib.request\nurllib.request.urlretrieve(RAW_URL + '/app/buggy_app.py', 'buggy_app.py')\n"
        f"TEXT_APP = {TEXT_APP!r}\n"
        "open('text_app.py', 'w', encoding='utf-8').write(TEXT_APP.replace('DATA', repr(RAW_URL + '/data/shipments_2025_clean.csv')))\n"
        "print('REFERENCE'); test_my_app('reference_app.py')\nprint('BUGGY'); test_my_app('buggy_app.py')\n"
        "print('TEXT APP'); test_my_app('text_app.py')",
    ],
}


def windows_ready(nb):
    """Runs the notebook as it is, on every system. Until 17 November 2026 this put a line in front of the notebook on
    Windows that gave the kernel's stderr a file handle: the MCP client passes its errlog (by default sys.stderr) to the
    server process, and a kernel without a handle fails with UnsupportedOperation: fileno. Colab now has such a kernel
    too (Python 3.13, newer ipykernel), so notebook 3 itself sends the server's messages to a file (errlog=SERVER_LOG),
    and the verifier must not hide the problem any more."""
    return nb


def serve():
    """Serve the repository; .py and .json files get the GitHub address replaced by this server's own."""
    target = {}

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send_head(self):
            path = Path(self.translate_path(self.path))
            if path.suffix in (".py", ".json") and path.is_file():
                body = path.read_text(encoding="utf-8").replace(RAW, target["base"]).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                import io
                return io.BytesIO(body)
            return super().send_head()

    httpd = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
    target["base"] = f"http://127.0.0.1:{httpd.server_address[1]}"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, target["base"]


def numbers(text: str) -> list[str]:
    """Every number in the text, by value: 17,700.0 and 17700 are the same, so are 3.4 and 3.40."""
    return [f"{float(n.replace(',', '')):g}" for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


def output_text(cell) -> str:
    parts = []
    for out in cell.get("outputs", []):
        if out.get("output_type") == "stream":
            parts.append(out.get("text", ""))
        elif out.get("output_type") in ("execute_result", "display_data"):
            parts.append(out.get("data", {}).get("text/plain", ""))
        elif out.get("output_type") == "error":
            parts.append("\n".join(out.get("traceback", [])))
    return "\n".join(parts)


def check_cell(cell) -> list[str]:
    problems = []
    out = output_text(cell)
    out_numbers = set(numbers(out))
    flat = " ".join(out.split())
    for line in cell.source.splitlines():
        if "# CHECK:" not in line:
            continue
        want = line.split("# CHECK:", 1)[1].strip()
        need = numbers(want)
        if need:
            missing = [n for n in need if n not in out_numbers]
            if missing:
                problems.append(f"CHECK '{want}': not in output: {missing}")
        elif " ".join(want.split()) not in flat:
            problems.append(f"CHECK '{want}': text not in output")
    return problems


def run_recovery(base: str) -> list[str]:
    """Notebook 1 for a pair whose cleaning failed: the closed answer cell of section 3 is never run.
    The "continue from here" cell alone must make sections 4 and 5 work, with the same CHECK values."""
    nb = windows_ready(nbformat.read(ROOT / "notebooks" / "1_ask_your_data.ipynb", as_version=4))
    nb.cells = [c for c in nb.cells if not (c.cell_type == "code" and "Our answer with the metric contract" in c.source)]
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.source = cell.source.replace(RAW, base)
    with tempfile.TemporaryDirectory() as tmp:
        NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": tmp}},
                       allow_errors=True).execute()
    problems = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        errors = [o for o in cell.get("outputs", []) if o.get("output_type") == "error"]
        if errors:
            problems.append(f"recovery path, cell {i}: {errors[0].get('ename')}: {errors[0].get('evalue')[:200]}")
        problems += [f"recovery path, cell {i}: {p_}" for p_ in check_cell(cell)]
    return problems


SAMPLE_TOOL = '''
@mcp.tool()
def cost_per_kg(carrier: str, country: str = "all") -> dict:
    """Total cost divided by total weight, in euro per kg, for one carrier's 2025 shipments.

    Args:
        carrier: one of the four carriers.
        country: AT, DE, CZ, HU, IT, SI or "all".
    """
    name = carrier_name(carrier)
    df = pick(SHIPMENTS[SHIPMENTS["carrier"] == name], country, "all", 1, 12)
    return {"carrier": name, "country": country, "eur_per_kg": round(float(df["cost_eur"].sum() / df["weight_kg"].sum()), 2)}
'''


def run_new_tool(base: str, env: dict) -> list[str]:
    """Notebook 3, section 5, the way a student does it: a new tool pasted into the cell, the cell run twice.
    The tool must appear once, answer, and show through pretty() (a shape pretty() does not know)."""
    nb = windows_ready(nbformat.read(ROOT / "notebooks" / "3_give_the_ai_tools.ipynb", as_version=4))
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.source = cell.source.replace(RAW, base)
            if cell.source.startswith("NEW_TOOL = '''"):
                cell.source = cell.source.replace("NEW_TOOL = '''\n'''", "NEW_TOOL = '''" + SAMPLE_TOOL + "'''", 1)
                rerun = cell.source.split("\n# CHECK")[0]
    nb.cells.append(nbformat.v4.new_code_cell(rerun + "\n" +
        "names = [t.name for t in await list_tools()]\nprint('TOOLS', names, names.count('cost_per_kg'))\n"
        "print(pretty(await call('cost_per_kg', carrier='Gams', country='IT')))"))
    old = dict(os.environ)
    os.environ.update(env)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": tmp}},
                           allow_errors=True).execute()
    finally:
        os.environ.clear()
        os.environ.update(old)
    problems = []
    for i, cell in enumerate(nb.cells):
        errors = [o for o in cell.get("outputs", []) if o.get("output_type") == "error"] if cell.cell_type == "code" else []
        if errors:
            problems.append(f"new tool, cell {i}: {errors[0].get('ename')}: {errors[0].get('evalue')[:200]}")
    last = output_text(nb.cells[-1])
    if "cost_per_kg'] 1" not in last.replace('", "', "', '") and "'cost_per_kg'] 1" not in last:
        problems.append("the new tool is not listed exactly once after running the cell twice:\n" + last[:400])
    if '"eur_per_kg"' not in last:
        problems.append("the new tool's result does not show:\n" + last[-400:])
    return problems


def run_without_key(base: str) -> list[str]:
    """Notebook 3 the way most students start it: no key. Every Gemini cell must explain, none may fail."""
    nb = windows_ready(nbformat.read(ROOT / "notebooks" / "3_give_the_ai_tools.ipynb", as_version=4))
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.source = cell.source.replace(RAW, base)
    saved = {k: os.environ.pop(k) for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_BASE_URL") if k in os.environ}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": tmp}},
                           allow_errors=True).execute()
    finally:
        os.environ.update(saved)
    problems = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        errors = [o for o in cell.get("outputs", []) if o.get("output_type") == "error"]
        if errors:
            problems.append(f"without a key, cell {i}: {errors[0].get('ename')}: {errors[0].get('evalue')[:200]}")
    live = [output_text(c) for c in nb.cells if "live" in c.metadata.get("tags", [])]
    if not any("No key yet" in t for t in live) or not any("No Gemini model yet" in t for t in live):
        problems.append("without a key, the Gemini cells do not explain what to do")
    return problems


def run(name: str, base: str, env: dict) -> list[str]:
    nb = windows_ready(nbformat.read(ROOT / "notebooks" / name, as_version=4))
    original = len(nb.cells)
    for text in EXTRA.get(name, []):
        nb.cells.append(nbformat.v4.new_code_cell(f"RAW_URL = {base!r}\n" + text))
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.source = cell.source.replace(RAW, base)
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        old = dict(os.environ)
        os.environ.update(env)
        try:
            NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": tmp}},
                           allow_errors=True).execute()
        finally:
            os.environ.clear()
            os.environ.update(old)
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        errors = [o for o in cell.get("outputs", []) if o.get("output_type") == "error"]
        if errors:
            problems.append(f"cell {i}: {errors[0].get('ename')}: {errors[0].get('evalue')[:300]}")
        problems += [f"cell {i}: {p}" for p in check_cell(cell)]
    if name == "2_build_the_app.ipynb":
        text = output_text(nb.cells[original])
        ref, _, rest = text.partition("BUGGY")
        bug, _, as_text = rest.partition("TEXT APP")
        if "6 of 6 checks passed" not in ref:
            problems.append("reference app does not pass the six app checks:\n" + ref[-800:])
        if "6 of 6 checks passed" not in as_text:
            problems.append("an app that shows its numbers as text (\"85.1%\") is not read:\n" + as_text[-800:])
        if "6 of 6 checks passed" in bug or "OFF" not in bug:
            problems.append("the app with one wrong line is not caught:\n" + bug[-800:])
        else:
            print("   reference app 6 of 6; app with one wrong line:", bug.count("OFF "), "checks off;",
                  "app with numbers as text (\"85.1%\"): 6 of 6" if "6 of 6 checks passed" in as_text else "")
    if name == "3_give_the_ai_tools.ipynb":
        live = [output_text(c) for c in nb.cells if "live" in c.metadata.get("tags", [])]
        asked = [t for t in live if "QUESTION:" in t]
        if not asked or not all("TOOL CALL  carrier_scorecard(country='IT')" in t and "ANSWER:" in t for t in asked):
            problems.append("the Gemini host loop did not complete against the stand-in endpoint")
        else:
            print(f"   {len(asked)} ask() cells completed the host loop against the stand-in Gemini endpoint")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github", action="store_true")
    args = ap.parse_args()
    httpd, base = (None, RAW) if args.github else serve()
    fake = subprocess.Popen([sys.executable, str(ROOT / "scripts" / "fake_gemini.py"), "0"],
                            stdout=subprocess.PIPE, text=True)
    port = fake.stdout.readline().strip()
    env = {"GEMINI_API_KEY": "stand-in-key", "GOOGLE_GEMINI_BASE_URL": f"http://127.0.0.1:{port}"}
    failed = 0
    try:
        for name in NOTEBOOKS:
            problems = run(name, base, env)
            print(("OK   " if not problems else "FAIL ") + name)
            for p in problems:
                print("   ", p)
            failed += bool(problems)
        problems = run_recovery(base)
        print(("OK   " if not problems else "FAIL ") + "1_ask_your_data.ipynb from the checkpoint only")
        for p_ in problems:
            print("   ", p_)
        failed += bool(problems)
        problems = run_new_tool(base, env)
        print(("OK   " if not problems else "FAIL ") + "3_give_the_ai_tools.ipynb with a new tool pasted in, cell run twice")
        for p_ in problems:
            print("   ", p_)
        failed += bool(problems)
        problems = run_without_key(base)
        print(("OK   " if not problems else "FAIL ") + "3_give_the_ai_tools.ipynb without a key")
        for p_ in problems:
            print("   ", p_)
        failed += bool(problems)
    finally:
        fake.terminate()
        if httpd:
            httpd.shutdown()
    if failed:
        raise SystemExit(f"{failed} NOTEBOOK(S) FAILED")
    print("ALL NOTEBOOK CHECKS PASSED")


if __name__ == "__main__":
    main()
