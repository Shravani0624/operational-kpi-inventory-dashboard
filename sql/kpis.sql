-- Operational KPIs. SYNTHETIC DATA ONLY.
-- Tables: inventory(date, category, units_sold, spend, stockout),
-- staffing(date, department, planned_hours, actual_hours).
-- Four SELECT queries, run in order by dashboard.py.

WITH daily AS (
    SELECT date, SUM(spend) AS daily_spend, SUM(units_sold) AS daily_units,
           SUM(stockout) AS stockout_categories
    FROM inventory
    GROUP BY date
)
SELECT date, daily_spend, daily_units, stockout_categories,
       AVG(daily_spend) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d_spend
FROM daily
ORDER BY date;

SELECT category, SUM(spend) AS total_spend, SUM(units_sold) AS total_units,
       SUM(stockout) AS stockout_days,
       SUM(spend) * 100.0 / SUM(SUM(spend)) OVER () AS pct_of_spend
FROM inventory
GROUP BY category
ORDER BY total_spend DESC;

WITH daily AS (
    SELECT date, SUM(spend) AS daily_spend FROM inventory GROUP BY date
)
SELECT date, daily_spend,
       LAG(daily_spend) OVER (ORDER BY date) AS previous_day_spend,
       daily_spend - LAG(daily_spend) OVER (ORDER BY date) AS day_change
FROM daily
ORDER BY date;

SELECT date, department, SUM(planned_hours) AS planned, SUM(actual_hours) AS actual,
       SUM(actual_hours) - SUM(planned_hours) AS variance_hours
FROM staffing
GROUP BY date, department
ORDER BY date, department;
