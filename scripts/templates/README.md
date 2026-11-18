# AI Lab · Vibe Analytics, Vibe Coding And MCP

**FH OÖ · Sina Mirshahi · «SESSION_DATE»**

Course material for one session. One case runs through the whole session: an invented company in Upper Austria sells spare parts and must sign new contracts with its carriers (delivery companies). The head of logistics asks: **For each country, which delivery company (carrier) should we use? And when is the faster, more expensive Express service worth its price?**

You answer in three steps. First, an AI writes the code for your analysis (vibe analytics). Then an AI builds an app from your answer, without you writing the code (vibe coding). Finally, you give an AI tools, so that it can find information on its own (MCP, the Model Context Protocol). Every step ends with a check that you can trust.

## Start here

You need two things: a **Google account**, and one **AI assistant** that you can use (ChatGPT, Gemini, Claude or Copilot).

1. Open notebook 1: click its **Open in Colab** button in the table below.
2. Follow the notebook from the top. It tells you each step.

There are no slides. Each notebook has everything, from top to bottom: what I show on the screen, your tasks, and the **Look back** blocks that we open after a task.

**The plan:** block 1 is notebook 1 and section 1 of notebook 2. Block 2 is the rest of notebook 2, then notebook 3. At the end you post three lines in the chat, or give them to me on paper: one carrier recommendation with its number, one app check you ran, and one thing you learned from a recording.

Share only course data with AI tools, never company data.

## Notebooks

| Notebook | What you do | Open in Colab |
|---|---|---|
| [1 · Ask Your Data](notebooks/1_ask_your_data.ipynb) | Block 1: ask an AI about the export, check the data, agree on a definition, compare within each country | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](«COLAB1») |
| [2 · Build The App](notebooks/2_build_the_app.ipynb) | Section 1 in block 1 (read the spec). The rest in block 2: let an AI write the app, run it in your browser, test it with numbers you know | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](«COLAB2») |
| [3 · Give The AI Tools](notebooks/3_give_the_ai_tools.ipynb) | Block 2: an MCP server with four tools, recordings to check; after class (optional): the tools themselves, your own questions to Gemini | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](«COLAB3») |

If a button does not open, copy the address: «COLAB1», «COLAB2», «COLAB3». Or open Colab, choose **File, Open notebook, GitHub**, and type `FH-Prevail/ailab`.

## Words we use

«WORDS»

## The app in your browser (block 2)

No installation and no account: Streamlit (a Python tool for small web apps) runs inside the browser ([stlite](https://github.com/whitphx/stlite)). Notebook 2 tells you when to use these links.

- [Starter](«LINK_STARTER»): the app editor, with a small app that only loads the data. You replace its code with your AI's app and click **Save**.
- [Reference app](«LINK_REFERENCE»): our version, if you are stuck. Its code is [app/app.py](app/app.py).
- [An app with one wrong line](app/buggy_app.py): test it and find the line.

The first time, the starter can take up to a minute to load.

## Gemini API key (after class, notebook 3)

You need the key only for sections 3 and 4 of notebook 3, after class. It is free in Google AI Studio: [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Section 3 of notebook 3 shows each step. The free version (free tier) allows only a limited number of requests per minute and per day. The limits change, so check them in AI Studio (checked «CHECKED_DATE»). Store the key as a Colab secret, never in a cell or a prompt. Your questions and the tool results in notebook 3 go to Google; the app in your browser stays in your browser.

---

## For later (not needed in class)

### The data

The data is not real (it is synthetic), but it is built like a real export. The company and the four carriers are invented. [data/README.md](data/README.md) describes every column.

| File | What it is | Used in |
|---|---|---|
| [shipments_2025.csv](data/shipments_2025.csv) | the raw export: «data.rows» rows, every shipment of 2025, problems included | notebook 1 |
| [shipments_2025_clean.csv](data/shipments_2025_clean.csv) | the same shipments after the metric contract: «data.shipments» rows | notebooks 2 and 3, the app, Power BI |
| [carrier_notes.csv](data/carrier_notes.csv) | «data.notes» notes our teams wrote about the carriers | notebook 3 (the MCP server) |

Download a file with the **Download raw file** button on its GitHub page.

### The app and the MCP server on your own computer

- **The app:** `pip install streamlit pandas altair`, then `streamlit run app/app.py`.
- **The MCP server:** [mcp_server/shipments_server.py](mcp_server/shipments_server.py) gives any MCP host four read-only tools (they read the cleaned table, but never change it): `list_carriers`, `carrier_scorecard`, `late_shipments`, `carrier_notes`. It needs `pip install "mcp==2.3.0" pandas` and reads the data from a `data/` folder next to it, or from this repository.
  - **Claude Code:** `claude mcp add shipments -- python mcp_server/shipments_server.py`
  - **Claude Desktop, Gemini CLI, VS Code, LM Studio:** add a server with command `python` and argument `path/to/shipments_server.py` in the host's MCP settings.

Any MCP host that can start a local program and is allowed to do so can use it. [traces/](traces/) holds four real recordings of a model using these tools (question, tool calls, results, answer), also as a readable [worksheet](traces/README.md).

### Power BI

The demo of block 2 uses the app's KPI definitions (KPIs: key numbers such as on time %) again in Power BI, with Microsoft's Power BI MCP server: [powerbi/README.md](powerbi/README.md), with the prompts and the DAX measures. It needs Windows and Power BI Desktop.

### How the numbers were made

`data/make_dataset.py` makes the data (fixed seed, identical files every time). `analysis/build_evidence.py` applies the metric contract and writes every number that the notebooks, the pictures and the checks show into `evidence/results.json` and `evidence/check_table.csv`. It stops if a result that the session teaches is no longer true. `scripts/test_app.py` and `scripts/test_mcp.py` check the app and the MCP server against the same table. `scripts/build_figures.py` draws the pictures in the notebooks (it needs matplotlib).

```bash
python3 -m pip install -r requirements.txt
python3 data/make_dataset.py
python3 analysis/build_evidence.py
python3 scripts/test_app.py
python3 scripts/test_mcp.py
```

## After the session: what we found

<details>
<summary>Open this after the session: it shows the answer to notebook 1.</summary>

On time, by country (the metric contract, shipments with a known result):

«BEST_TABLE»

These are observations from 2025: a starting point for the 2027 contracts, not proof. Groups with only a few shipments, and carriers with very similar results, need more data. Recent months matter.

</details>

Free to use for teaching. Synthetic data; no real company is described.
