# Operational KPI & Inventory Dashboard

![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=postgresql&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat&logo=powerbi&logoColor=black)

**Portfolio:** https://shravani0624.github.io/portfolio/ | **Profile:** https://github.com/Shravani0624


## Data notice
**All data in this project is SYNTHETIC, generated for demonstration.**
It is not Pinevox data and not any real business's inventory or staffing
data. Spend spikes and stockouts are deliberately planted.

## Problem
Operations reporting needs one view of spend, units, stockouts and
staffing, with anomalies surfaced early and a root-cause direction,
not just a monthly total.

## Method
`dashboard.py` (Python, Pandas, Matplotlib, standard-library SQLite)
loads 120 synthetic inventory rows (30 days, 4 categories) and 60
staffing rows (30 days, 2 departments), then:

1. Runs the four SQL KPIs in `sql/kpis.sql` for real, in SQLite:
   daily spend/units/stockouts with a 7-day rolling average (CTE +
   window function), category totals and share of spend, day-on-day
   change (LAG window function), and staffing planned vs actual by
   department.
2. Flags anomalies: daily spend more than 2 standard deviations above
   its 7-day rolling mean, or any stockout day.
3. Produces charts (daily spend vs rolling mean, daily overtime) and
   a written summary with root-cause notes.

## Verified run results
Run with `python dashboard.py` (verified October 2026):

- Inventory rows: **120**; days covered: **30**
- Total spend: **319,319.06**; total units sold: **14,353**
- Stockout days (any category): **2** (14 Feb, Groceries; 21 Feb, Electronics)
- Spend anomaly days: **2**, the same two planted spike days
- Anomaly rows flagged: **2**
- Total overtime hours vs plan: **268.0**
- Category spend share: Groceries **32.1%**, Electronics **28.7%**,
  Clothing **20.2%**, Home **19.0%**
- All four SQL queries in `sql/kpis.sql` executed successfully in this
  run (an earlier draft failed on a window-over-aggregate query and
  was fixed with a CTE; the shipped SQL is the verified version).

## How to run
```bash
pip install -r requirements.txt
python dashboard.py
```
Outputs are written to `output/`: `daily_kpis.csv`,
`category_kpis.csv`, `day_changes.csv`, `staffing_kpis.csv`,
`staffing_summary.csv`, `anomalies.csv`, `summary_report.md`,
`charts.png`.

## Skills shown
SQL (CTEs, window functions, LAG, rolling averages), Python (Pandas,
Matplotlib), KPI design, anomaly detection, root-cause analysis,
operational reporting. The 10% inventory overspending reduction on
Shravani's CV is her real work history, not a result of this synthetic
project, and is not claimed as one here.
