# -*- coding: utf-8 -*-
"""build_figures.py - the four pictures the notebooks show (there is no slide deck any more).

    python3 scripts/build_figures.py        # writes figures/*.png

The notebooks load the pictures from the course page (figures/ on GitHub). Numbers in a picture
come from evidence/results.json, like everywhere else. Needs matplotlib.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
R = json.loads((ROOT / "evidence" / "results.json").read_text(encoding="utf-8"))

BLUE, INK, GREY, LINE, PANEL = "#004B96", "#1A1A1A", "#595959", "#A6A6A6", "#F4F4F4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})


def canvas(w, h):
    """A blank drawing area, w by h inches; one unit is one inch."""
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def node(ax, x, y, w, h, title, sub="", size=12, fill="white", edge=BLUE):
    """A box with a bold first line and a normal second line; (x, y) is its lower left corner."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.07", fc=fill, ec=edge, lw=1.6))
    if sub:
        ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", fontsize=size, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center", fontsize=size - 1, color=INK)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=size, fontweight="bold", color=INK)


def arrow(ax, x1, y1, x2, y2, color=BLUE, lw=1.6):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=16))


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, dpi=150, facecolor="white")
    plt.close(fig)
    print("wrote figures/" + name)


def row_of_boxes(ax, boxes, y, w, h, gap, x0, size=12):
    """Boxes in a row with an arrow between neighbours; returns the x of every box."""
    xs = [x0 + i * (w + gap) for i in range(len(boxes))]
    for i, (x, (title, sub)) in enumerate(zip(xs, boxes)):
        node(ax, x, y, w, h, title, sub, size=size)
        if i < len(boxes) - 1:
            arrow(ax, x + w + 0.07, y + h / 2, x + w + gap - 0.07, y + h / 2)
    return xs


def vibe_analytics():
    fig, ax = canvas(11, 1.5)
    row_of_boxes(ax, [("Your question", "in plain words"), ("The AI writes code", "in your AI chat"),
                      ("The code runs", "on your data, in Colab"), ("An answer", "a table, a chart")],
                 y=0.25, w=2.3, h=1.0, gap=0.5, x0=0.15)
    save(fig, "vibe_analytics.png")


def vibe_coding():
    fig, ax = canvas(11, 2.3)
    w, h, gap, y = 1.86, 1.0, 0.36, 1.1
    xs = row_of_boxes(ax, [("1 · Describe", "the spec"), ("2 · The AI writes", "the code"), ("3 · Run it", "in the browser"),
                           ("4 · Test it", "with numbers you know"), ("5 · Change", "one thing")],
                      y=y, w=w, h=h, gap=gap, x0=0.15, size=11)
    last, two, low = xs[4] + w / 2, xs[1] + w / 2, 0.55
    ax.plot([last, last, two], [y, low, low], color=BLUE, lw=1.6, solid_capstyle="butt")
    arrow(ax, two, low, two, y - 0.03)
    ax.text((last + two) / 2, low - 0.25, "repeat: one change at a time, test again after each change",
            ha="center", va="center", fontsize=11, color=GREY, style="italic")
    save(fig, "vibe_coding.png")


def why_mcp():
    fig, ax = canvas(11, 4.3)
    apps = ["Claude", "ChatGPT", "Copilot", "LM Studio"]
    systems = ["ERP", "Power BI", "Excel", "Database"]
    ys = [3.0 - i * 0.72 for i in range(4)]
    bw, bh = 1.45, 0.5
    for side, x0 in ((0, 0.15), (1, 5.85)):
        ax.text(x0, 3.95, "Without a standard" if side == 0 else "With MCP", fontsize=14, fontweight="bold", color=INK, va="center")
        ax_x, sys_x = x0, x0 + 3.55
        if side == 0:
            for ya in ys:
                for ysys in ys:
                    ax.plot([ax_x + bw, sys_x], [ya + bh / 2, ysys + bh / 2], color=GREY, lw=0.9)
            ax.text(x0, 0.28, "4 apps × 4 systems = 16 connections", fontsize=12, color=INK, va="center")
        else:
            mx, mw = x0 + 1.95, 1.1
            ax.add_patch(FancyBboxPatch((mx, ys[3]), mw, ys[0] + bh - ys[3], boxstyle="round,pad=0,rounding_size=0.07",
                                        fc=PANEL, ec=BLUE, lw=1.8))
            ax.text(mx + mw / 2, (ys[0] + bh + ys[3]) / 2, "MCP", ha="center", va="center", fontsize=15, fontweight="bold", color=INK)
            for y in ys:
                ax.plot([ax_x + bw, mx], [y + bh / 2, y + bh / 2], color=BLUE, lw=1.4)
                ax.plot([mx + mw, sys_x], [y + bh / 2, y + bh / 2], color=BLUE, lw=1.4)
            ax.text(x0, 0.28, "4 + 4 = 8, and each new app or system adds one", fontsize=12, color=INK, va="center")
        for y, a, s in zip(ys, apps, systems):
            node(ax, ax_x, y, bw, bh, a, size=11)
            node(ax, sys_x, y, bw, bh, s, size=11)
    save(fig, "why_mcp.png")


def tool_call():
    fig, ax = canvas(11, 5.6)
    cols = {"host": 1.6, "model": 5.5, "server": 9.4}
    heads = {"host": ("Host", "the app you talk to"), "model": ("Model", "Gemini, Claude, GPT"),
             "server": ("MCP server", "shipments_server.py")}
    top = 4.75
    for key, x in cols.items():
        node(ax, x - 1.3, top, 2.6, 0.72, *heads[key], size=12)
        ax.plot([x, x], [0.15, top], color=LINE, lw=1.0, ls=(0, (5, 4)))
    it = R["by_country"]["IT"]["Gams Cargo"]
    messages = [("host", "server", "1  Which tools do you have?"),
                ("server", "host", "2  Four tools: name, description, inputs"),
                ("host", "model", "3  Your question + the four descriptions"),
                ("model", "host", "4  “Call carrier_scorecard(country = IT)”"),
                ("host", "server", "5  Run it: the server counts the shipments"),
                ("server", "host", f"6  Gams Cargo {it['on_time_pct']:.1f} % of {it['resolved']}, ..."),
                ("host", "model", "7  Here is the result"),
                ("model", "host", "8  The answer, in words")]
    for i, (a, b, label) in enumerate(messages):
        y = 4.2 - i * 0.56
        x1, x2 = cols[a], cols[b]
        across = {a, b} == {"host", "server"}
        arrow(ax, x1, y, x2, y, color=BLUE if across else GREY, lw=1.5)
        lo, hi = (cols["model"], cols["server"]) if across else (min(x1, x2), max(x1, x2))
        ax.text((lo + hi) / 2, y + 0.16, label, ha="center", va="center", fontsize=11, color=INK)
    save(fig, "tool_call.png")


if __name__ == "__main__":
    vibe_analytics()
    vibe_coding()
    why_mcp()
    tool_call()
