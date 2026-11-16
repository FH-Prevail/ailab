# Course data: the 2025 shipments of a spare-parts distributor

Invented (synthetic) data for the AI Lab session on vibe analytics, vibe coding and MCP. The company, its customers and the four carriers (Biber Freight, Falke Transport, Gams Cargo, Luchs Logistik) are invented. If a name looks like a real company, that is by chance. `make_dataset.py` makes the files with a fixed random seed (a fixed start value for the random numbers), so running it again gives the same files.

## Files

| File | Rows | One row is |
|---|---|---|
| `shipments_2025.csv` | «data.rows» | one row of the export (a shipment, as the system exported it) |
| `shipments_2025_clean.csv` | «data.shipments» | one shipment, after the metric contract of notebook 1 |
| `carrier_notes.csv` | «data.notes» | one note our customer service, purchasing or warehouse team wrote about a carrier |
| `make_dataset.py` | | the generator (fixed seed) |

Shipped from the warehouses in **Linz** and **Wels** to customers in Austria (AT), Germany (DE), Czechia (CZ), Hungary (HU), Italy (IT) and Slovenia (SI), from «data.first_ship_date» to «data.last_ship_date». The export ran at the end of «data.export_date».

## `shipments_2025.csv`: the raw export

| Column | Meaning |
|---|---|
| `shipment_id` | the shipment number |
| `ship_date` | the day the carrier collected it |
| `promised_date` | the delivery day the carrier promised (business days, Monday to Friday) |
| `delivered_date` | the day it arrived; empty if it has not arrived |
| `status` | `delivered`, `lost` or `in_transit` (still on its way when the export ran) |
| `carrier` | the carrier |
| `service` | `Standard` or `Express` |
| `warehouse` | `Linz` or `Wels` |
| `country`, `city` | where it went |
| `distance_km` | road distance from the warehouse |
| `weight_kg` | weight of the shipment |
| `parcels` | number of parcels |
| `cost_eur` | what the carrier charged, in euro |
| `damaged` | 1 if it arrived damaged |
| `customer_id` | the customer |

Like most real exports, this file has a few problems. Finding them is part of hands-on 1.

## `shipments_2025_clean.csv`: after the metric contract

The same columns, cleaned with the rules of notebook 1, section 3. There are also three columns where an empty cell means "does not apply" or "not known yet". So a simple average gives the right number:

| Column | Meaning |
|---|---|
| `on_time` | 1 on time, 0 late or lost, empty if the result is not known yet |
| `transit_days` | calendar days from `ship_date` to `delivered_date`; empty unless delivered |
| `damaged` | 1 or 0 for delivered shipments; empty otherwise |
| `month` | the month of `ship_date`, 1 to 12 |

## `carrier_notes.csv`

`date`, `carrier`, `author`, `note`. One note contains text written for AI assistants. It is the example of prompt injection (text that tries to control an AI) in hands-on 3, not advice.

## Licence

Free to use for teaching. Synthetic data; no real company is described.
