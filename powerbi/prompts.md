# The Prompts Of The Power BI Demo

Open a terminal in the folder of this repository and type `claude` (in GitHub Copilot CLI: `copilot`). Run the prompts one at a time, with your project `powerbi/CarrierScorecard.pbip` open in Power BI Desktop (see [README.md](README.md), "Setup"). Read what the agent plans before you approve a change. Prompts 1 to 3 use the MCP server; prompt 4 uses the report authoring skill.

Claude Code asks before it calls a Power BI tool, changes a file, or runs a program such as the report tool. Read what it wants to do, then allow it. Prompt 4 has many small steps. Before you send it, press **Shift + Tab** until Claude Code shows that it accepts edits: then it changes files without asking each time, but still asks before it runs a program. When it asks to run the report tool (`powerbi-report-author`), choose the option that does not ask again for it.

## 1. Connect

```
Use the Power BI MCP server. Connect to 'CarrierScorecard' in Power BI Desktop and list its
tables and columns. Do not change anything yet.
```

You should see one table, `shipments`, with the 19 columns of `data/shipments_2025_clean.csv`.

## 2. Reuse the KPI definitions of the app

```
Read app/app.py. It computes six KPIs per carrier from the shipments table. Create the same
six KPIs as DAX measures in the shipments table, in a display folder "Scorecard", each with a
one-line description:
- Shipments: number of rows
- Known result: number of non-empty on_time values
- On time %: on_time added up, divided by Known result; format 0.0%
- Transit days: average of transit_days; format 0.00
- Cost per shipment €: average of cost_eur; format 0.00
- Damaged %: damaged added up, divided by the number of non-empty damaged values; format 0.0%
Empty cells mean "not known yet" or "does not apply": never treat them as 0. Show me the DAX
before you create the measures.
```

The agent shows the DAX and waits. Compare it with [measures.dax](measures.dax), then answer `Create them.`

## 3. Check the numbers against what we trust

```
Run one DAX query that returns the six measures per carrier for country = "IT", all services,
all months. Compare each value with the Italy rows of evidence/check_table.csv (on_time_pct is
in percent there). Then do the same for country = "DE" with service = "Standard", and for
carrier = "Luchs Logistik" in month 12. Compare counts exactly. Multiply both percentage measures by 100
and round to one decimal; round transit days and cost to two decimals before comparing with the CSV.
List every difference, or say that all match.
```

## 4. Build the report page like the app

First save the project in Power BI Desktop (Ctrl+S): the skill reads the measures from the saved files.

```
Use the powerbi-report-cli skill. Power BI Desktop has the project
powerbi/CarrierScorecard.pbip open, and it is saved. Fill its empty page with a page
"Carrier Scorecard" like app/app.py: slicers for country, service and month; a table with one
row per carrier and the six Scorecard measures; a bar chart of On time % by carrier; a line
chart of On time % by month with one line per carrier. Carrier colours: Biber Freight #0B5CAD,
Falke Transport #E66A1F, Gams Cargo #1B9E5A, Luchs Logistik #D04F95. Validate the report
files, then reload the report in Power BI Desktop.
```

The page appears in the open Power BI Desktop; this took about four minutes in our test. If Power BI shows "This project's files were changed externally", click **Apply external changes**.
