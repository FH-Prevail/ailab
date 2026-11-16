# The Prompts Of The Power BI Demo

One at a time, in Claude Code (or Copilot) started in the folder of this repository, with `CarrierScorecard.pbip` open in Power BI Desktop. Read what the agent plans before you approve a change.

## 1. Connect

```
Use the Power BI MCP server. Connect to 'CarrierScorecard' in Power BI Desktop and list its
tables and columns. Do not change anything yet.
```

You should see one table, `shipments`, with the columns of `data/shipments_2025_clean.csv`.

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

## 3. Check the numbers against what we trust

```
Run one DAX query that returns the six measures per carrier for country = "IT", all services,
all months. Compare each value with the Italy rows of evidence/check_table.csv (on_time_pct is
in percent there). Then do the same for country = "DE" with service = "Standard", and for
carrier = "Luchs Logistik" in month 12. Compare counts exactly. Multiply both percentage measures by 100
and round to one decimal; round transit days and cost to two decimals before comparing with the CSV.
List every difference, or say that all match.
```

## 4. Optional: the report page (uses the report authoring skill)

Save the project in Desktop first. Then:

```
Use the powerbi-report-cli skill. In the CarrierScorecard.pbip project add a report page
"Carrier Scorecard" like app/app.py: slicers for country, service and month; a table with one
row per carrier and the six Scorecard measures; a bar chart of On time % by carrier; a line
chart of On time % by month with one line per carrier. Carrier colours: Biber Freight #0B5CAD,
Falke Transport #E66A1F, Gams Cargo #1B9E5A, Luchs Logistik #D04F95. Validate the report
files, then tell me to reopen the project in Power BI Desktop.
```

Close Power BI Desktop before the agent writes the report files, and reopen the project afterwards.
