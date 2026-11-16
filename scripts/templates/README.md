# AI Lab · Vibe Analytics, Vibe Coding And MCP

**FH OÖ · Sina Mirshahi · «SESSION_DATE»**

Course material for one session in two blocks and three steps. One case runs through the whole session: an invented company in Upper Austria sells spare parts and must sign new contracts with its carriers. The head of logistics asks: **For each country, which delivery company (carrier) should we use? And when is the faster, more expensive Express service worth its price?**

You answer with an AI that writes the code (vibe analytics). Then an AI builds an app from your answer, without you writing the code (vibe coding). Finally, you give an AI tools, so that it can find information on its own (MCP, the Model Context Protocol). Every step ends with a check that you can trust.

## Words we use

«WORDS»

## Slides

[The slides as PDF](slides/AI_Lab_Vibe_Analytics_Coding_MCP.pdf)

## Notebooks

| Notebook | What it is for | Open in Colab |
|---|---|---|
| [1 · Ask Your Data](notebooks/1_ask_your_data.ipynb) | Hands-on 1: ask an AI about the export, check the data, agree on a definition, compare within each country | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](«COLAB1») |
| [2 · Build The App](notebooks/2_build_the_app.ipynb) | Hands-on 2: write a spec, let an AI write the app, run it in your browser, test it with numbers you know | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](«COLAB2») |
| [3 · Give The AI Tools](notebooks/3_give_the_ai_tools.ipynb) | Hands-on 3: an MCP server with four tools, recorded traces to check, and (optional) your own questions to Gemini | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](«COLAB3») |

If a button does not open, copy the address: «COLAB1», «COLAB2», «COLAB3». Or open Colab, choose **File, Open notebook, GitHub**, type `FH-Prevail/ailab`.

**Keep your work:** in Colab choose **File, Save a copy in Drive** before you change anything.

**Which AI?** Any you can use: Gemini in Colab, Google AI Studio, ChatGPT, Claude or Microsoft Copilot. The prompts are written for all of them.

## The app in your browser (hands-on 2)

No installation and no account: Streamlit (a Python tool for small web apps) runs inside the browser ([stlite](https://github.com/whitphx/stlite)).

- [Starter](«LINK_STARTER»): shows that the data connection works; replace its code with your AI's app and click **Save**.
- [Reference app](«LINK_REFERENCE»): our version, if you are stuck. Its code is [app/app.py](app/app.py).
- [An app with one wrong line](app/buggy_app.py): test it and find the line.

On your own computer instead: `pip install streamlit pandas altair`, then `streamlit run app/app.py`.

## The data

The data is not real (it is synthetic), but it is built like a real export. The company and the four carriers are invented. [data/README.md](data/README.md) describes every column.

| File | What it is | Used in |
|---|---|---|
| [shipments_2025.csv](data/shipments_2025.csv) | the raw export: «data.rows» rows, every shipment of 2025, problems included | notebook 1 |
| [shipments_2025_clean.csv](data/shipments_2025_clean.csv) | the same shipments after the metric contract: «data.shipments» rows | notebooks 2 and 3, the app, Power BI |
| [carrier_notes.csv](data/carrier_notes.csv) | «data.notes» notes our teams wrote about the carriers | notebook 3 (the MCP server) |

Download a file with the **Download raw file** button on its GitHub page.

## The MCP server

[mcp_server/shipments_server.py](mcp_server/shipments_server.py) gives any MCP host four read-only tools (they read the cleaned table, but never change it): `list_carriers`, `carrier_scorecard`, `late_shipments`, `carrier_notes`. It needs `pip install "mcp==2.3.0" pandas` and reads the data from a `data/` folder next to it, or from this repository.

- **Claude Code:** `claude mcp add shipments -- python mcp_server/shipments_server.py`
- **Claude Desktop, Gemini CLI, VS Code, LM Studio:** add a server with command `python` and argument `path/to/shipments_server.py` in the host's MCP settings.
- **Notebook 3:** connects Gemini to it from Colab.

Any MCP host that can start a local program and is allowed to do so can use it. [traces/](traces/) holds four real recordings of a model using these tools (question, tool calls, results, answer), also as a readable [worksheet](traces/README.md).

## Power BI

The demo of block 2 uses the app's KPI definitions (KPIs: key numbers such as on time %) again in Power BI, with Microsoft's Power BI MCP server: [powerbi/README.md](powerbi/README.md), with the prompts and the DAX measures. It needs Windows and Power BI Desktop.

## Good to know

- **Gemini API key** (notebook 3, section 4): free in Google AI Studio. The free version (free tier) allows only a limited number of requests per minute and per day. The limits change, so check them in AI Studio (checked «CHECKED_DATE»). Store the key as a Colab secret, never in a cell or a prompt.
- **Your data:** share only course data with AI tools. Questions and tool results in notebook 3 go to Google; the app in your browser stays in your browser.

## How the numbers were made

`data/make_dataset.py` makes the data (fixed seed, identical files every time). `analysis/build_evidence.py` applies the metric contract and writes every number the slides, notebooks and checks show into `evidence/results.json` and `evidence/check_table.csv`. It stops if a result that the session teaches is no longer true. `scripts/test_app.py` and `scripts/test_mcp.py` check the app and the MCP server against the same table.

```bash
python3 -m pip install -r requirements.txt
python3 data/make_dataset.py
python3 analysis/build_evidence.py
python3 scripts/test_app.py
python3 scripts/test_mcp.py
```

## After the session: what we found

On time, by country (the metric contract, shipments with a known result):

«BEST_TABLE»

These are observations from 2025: a starting point for the 2027 contracts, not proof. Groups with only a few shipments, and carriers with very similar results, need more data. Recent months matter.

Free to use for teaching. Synthetic data; no real company is described.
