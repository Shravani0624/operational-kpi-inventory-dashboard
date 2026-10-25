"""
Operational KPI & Inventory Dashboard.
SYNTHETIC DATA ONLY: generated for demonstration. Not Pinevox real data.
Loads synthetic inventory and staffing data into SQLite, runs the SQL
KPIs in sql/kpis.sql (CTEs and window functions), detects anomalies
against a 7-day rolling mean, and produces charts plus a summary report.

Run:  python dashboard.py
Requires: pandas, matplotlib (standard-library sqlite3 for the SQL)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)


def main():
    inv = pd.read_csv(BASE / "data" / "inventory.csv", parse_dates=["date"])
    staff = pd.read_csv(BASE / "data" / "staffing.csv", parse_dates=["date"])

    con = sqlite3.connect(":memory:")
    inv.to_sql("inventory", con, index=False)
    staff.to_sql("staffing", con, index=False)
    sql_text = (BASE / "sql" / "kpis.sql").read_text()
    # kpis.sql holds four SELECT queries separated by semicolons.
    queries = [q.strip() for q in sql_text.split(";") if q.strip()]
    # Strip leading comment lines from each query block.
    clean = []
    for q in queries:
        lines = [ln for ln in q.splitlines() if not ln.strip().startswith("--")]
        if "\n".join(lines).strip():
            clean.append("\n".join(lines))
    results = {}
    for i, q in enumerate(clean, start=1):
        try:
            results[f"query_{i}"] = pd.read_sql_query(q, con)
        except Exception as e:  # keep the dashboard running and report the failure
            print(f"Query {i} failed: {e}")
    if "query_1" in results:
        results["query_1"].to_csv(OUT / "daily_kpis.csv", index=False)
    if "query_2" in results:
        results["query_2"].to_csv(OUT / "category_kpis.csv", index=False)
    if "query_3" in results:
        results["query_3"].to_csv(OUT / "day_changes.csv", index=False)
    if "query_4" in results:
        results["query_4"].to_csv(OUT / "staffing_kpis.csv", index=False)
    print(f"SQL queries run successfully: {sorted(results.keys())}")

    # Anomaly detection: daily spend more than 2 standard deviations above
    # its 7-day rolling mean, or a stockout day.
    daily = inv.groupby("date").agg(spend=("spend", "sum"), stockouts=("stockout", "sum"),
                                    units=("units_sold", "sum")).reset_index()
    daily["rolling_mean"] = daily["spend"].rolling(7).mean()
    daily["rolling_std"] = daily["spend"].rolling(7).std()
    daily["anomaly"] = (daily["spend"] > daily["rolling_mean"] + 2 * daily["rolling_std"]) | (daily["stockouts"] > 0)
    anomalies = daily[daily["anomaly"]]
    anomalies.to_csv(OUT / "anomalies.csv", index=False)

    staff_daily = staff.groupby("date").agg(
        planned=("planned_hours", "sum"), actual=("actual_hours", "sum")).reset_index()
    staff_daily["overtime"] = (staff_daily["actual"] - staff_daily["planned"]).clip(lower=0)
    staff_daily.to_csv(OUT / "staffing_summary.csv", index=False)

    total_spend = float(inv["spend"].sum())
    total_units = int(inv["units_sold"].sum())
    stockout_days = int(daily["stockouts"].gt(0).sum())
    spend_anomalies = int((daily["spend"] > daily["rolling_mean"] + 2 * daily["rolling_std"]).sum())
    overtime = float(staff_daily["overtime"].sum())
    report = (
        "# Operational KPI Summary (SYNTHETIC DATA)\n\n"
        f"- Inventory rows: {len(inv)}, days covered: {inv['date'].nunique()}\n"
        f"- Total spend: {total_spend:,.2f}; total units sold: {total_units}\n"
        f"- Stockout days (any category): {stockout_days}\n"
        f"- Spend anomaly days (>2 SD above 7-day rolling mean): {spend_anomalies}\n"
        f"- Anomaly rows flagged (spend anomaly or stockout): {len(anomalies)}\n"
        f"- Total overtime hours vs plan: {overtime:.1f}\n\n"
        "Root-cause notes (synthetic patterns to investigate, not findings\n"
        "about a real business):\n"
        "- Check stockout days first: a stockout usually follows a demand\n"
        "  spike or a late replenishment, and it suppresses units sold.\n"
        "- Check spend anomaly days against category: a single category\n"
        "  driving the spike points to ordering, price, or a data-entry error.\n"
        "- Check overtime against stockout/spend days: staffing pressure and\n"
        "  inventory pressure often arrive together and should be reported\n"
        "  together, not as separate stories.\n"
    )
    (OUT / "summary_report.md").write_text(report)
    print(report)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(daily["date"], daily["spend"], label="Daily spend")
    axes[0].plot(daily["date"], daily["rolling_mean"], label="7-day rolling mean")
    axes[0].set_title("Daily spend vs 7-day rolling mean (synthetic)")
    axes[0].legend()
    axes[1].bar(staff_daily["date"], staff_daily["overtime"])
    axes[1].set_title("Daily overtime hours vs plan (synthetic)")
    plt.tight_layout()
    plt.savefig(OUT / "charts.png", dpi=150)
    print(f"Charts saved to {OUT / 'charts.png'}")


if __name__ == "__main__":
    main()
