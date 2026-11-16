# Reuse Our KPI Definitions In Power BI

The demo in block 2: an AI agent (an AI that works on its own, step by step) reads the KPI definitions of our Streamlit app (`app/app.py`). KPIs are key numbers such as on time %. The agent builds the same measures (formulas) in a Power BI model. Then it checks them against the numbers we already trust (`evidence/check_table.csv`). Two separate parts do the work:

| Part | What it does | How it connects to Power BI |
|---|---|---|
| **Power BI Authoring MCP server** (Microsoft, formerly "Modeling MCP server") | reads and changes the **semantic model** (the tables and formulas behind a report): tables, columns, measures, relationships; runs DAX queries (DAX is the formula language of Power BI) | live, through MCP, to the model open in Power BI Desktop |
| **Report authoring skill** (`powerbi-authoring` plugin from Microsoft's `skills-for-fabric`) | writes **report pages and visuals** | by editing the report files of a project saved as `.pbip`; Desktop shows them after you reopen the project |

The MCP server cannot draw charts (visuals). The skill does not change the open model. The agent here is Claude Code; VS Code with GitHub Copilot or the GitHub Copilot CLI work the same way.

## What you need

- Windows with **Power BI Desktop** (free). The local MCP server does not run on macOS.
- **Node.js 18 or newer** (for `npx`).
- An MCP host: **Claude Code**, or **VS Code with GitHub Copilot** (Copilot is free for verified students).
- This repository: `app/app.py`, `data/shipments_2025_clean.csv`, `evidence/check_table.csv`.

## Setup (once)

1. **Power BI Desktop:** before you import anything, open *File, Options and settings, Options, Current file, Regional settings* and set *Locale for import* to **English (United States)**. The CSV uses a decimal point; with a German locale, 23.77 € would be read as 2,377 €.
2. *Get data, Text/CSV*, choose `data/shipments_2025_clean.csv`, *Load*. Rename the table to `shipments`.
3. *File, Save as*, type **Power BI project (.pbip)**, name it `CarrierScorecard`.
4. Register the MCP server with your host. In Claude Code on Windows (the `cmd /c` wrapper lets Windows start `npx`):

   ```
   claude mcp add powerbi-authoring --scope user -- cmd /c npx -y @microsoft/powerbi-modeling-mcp@latest --start
   ```

   In VS Code: install the extension *Power BI Modeling MCP* or add the server in `.vscode/mcp.json` with `"command": "npx", "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"]`.
5. The server blocks every tool until its licence terms (EULA) are accepted. Read them first; the agent then asks you to accept them once.
6. For report pages, add the skill (Claude Code):

   ```
   claude plugin marketplace add microsoft/skills-for-fabric
   claude plugin install powerbi-authoring@fabric-collection
   ```

## The prompts

Run them one at a time in the folder of this repository, with `CarrierScorecard` open in Power BI Desktop. They are in [prompts.md](prompts.md). If the agent cannot create a measure, [measures.dax](measures.dax) has all six to paste in by hand (*Modeling, New measure*).

## What to check

The measures must reproduce the reference cells, for example Italy, all services, Gams Cargo: **85.1 % on time** of **429** shipments with a known result. Every reference cell is in [`evidence/check_table.csv`](../evidence/check_table.csv). Same definitions, same numbers, in any tool: that is the point of the metric contract.

## Good to know

- The model metadata and the results of DAX queries go to the AI provider of your host. Use course data or data you are allowed to share.
- Keep the `.pbip` folder in version control (for example Git), or make a copy before the agent changes it.
- Microsoft also runs a hosted Power BI MCP server for models published in Fabric workspaces (a preview; an administrator of your organisation must switch it on). The demo uses the local one.
- Checked against Microsoft's documentation on 16 November 2026; tools change, so check the current pages: *Power BI Authoring MCP server* and *Power BI agentic development* on learn.microsoft.com.
