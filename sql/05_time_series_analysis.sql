-- ==============================================================================
-- 05_time_series_analysis.sql
-- E-Commerce Sales Performance & Customer Behavior Analysis
-- Purpose: Monthly Trends, MoM Growth Rates, Seasonality, and Quarterly Performance
-- ==============================================================================

-- 1. Monthly Performance Trends with Month-over-Month (MoM) Growth (Window Functions)
WITH Monthly_Agg AS (
    SELECT 
        Year_Month,
        Month_Name,
        COUNT(DISTINCT Order_ID) AS Total_Orders,
        ROUND(SUM(Sales_Amount), 2) AS Monthly_Revenue,
        ROUND(SUM(Profit), 2) AS Monthly_Profit,
        ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct,
        ROUND(AVG(Sales_Amount), 2) AS Avg_Order_Value
    FROM sales_transactions
    GROUP BY Year_Month, Month_Name
)
SELECT 
    Year_Month,
    Month_Name,
    Total_Orders,
    Monthly_Revenue,
    LAG(Monthly_Revenue, 1) OVER (ORDER BY Year_Month) AS Prev_Month_Revenue,
    ROUND((Monthly_Revenue - LAG(Monthly_Revenue, 1) OVER (ORDER BY Year_Month)) * 100.0 / 
          LAG(Monthly_Revenue, 1) OVER (ORDER BY Year_Month), 2) AS MoM_Revenue_Growth_Pct,
    Monthly_Profit,
    LAG(Monthly_Profit, 1) OVER (ORDER BY Year_Month) AS Prev_Month_Profit,
    ROUND((Monthly_Profit - LAG(Monthly_Profit, 1) OVER (ORDER BY Year_Month)) * 100.0 / 
          LAG(Monthly_Profit, 1) OVER (ORDER BY Year_Month), 2) AS MoM_Profit_Growth_Pct,
    Profit_Margin_Pct,
    Avg_Order_Value
FROM Monthly_Agg
ORDER BY Year_Month;


-- 2. Quarterly Financial Summary & Performance
SELECT 
    Quarter,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    ROUND(SUM(Sales_Amount), 2) AS Quarterly_Revenue,
    ROUND(SUM(Profit), 2) AS Quarterly_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Quarterly_Margin_Pct,
    ROUND(AVG(Sales_Amount), 2) AS Avg_Order_Value,
    ROUND(AVG(Discount_Percentage) * 100, 2) AS Avg_Discount_Pct
FROM sales_transactions
GROUP BY Quarter
ORDER BY Quarter;


-- 3. Peak and Trough Months (Highest and Lowest Performing Periods)
WITH Monthly_Performance AS (
    SELECT 
        Year_Month, 
        Month_Name, 
        ROUND(SUM(Sales_Amount), 2) AS Monthly_Revenue,
        ROUND(SUM(Profit), 2) AS Monthly_Profit
    FROM sales_transactions
    GROUP BY Year_Month, Month_Name
)
SELECT 'Highest Revenue Month' AS Metric_Type, Year_Month, Month_Name, Monthly_Revenue AS Value
FROM Monthly_Performance
ORDER BY Monthly_Revenue DESC
LIMIT 1;

WITH Monthly_Performance AS (
    SELECT 
        Year_Month, 
        Month_Name, 
        ROUND(SUM(Sales_Amount), 2) AS Monthly_Revenue,
        ROUND(SUM(Profit), 2) AS Monthly_Profit
    FROM sales_transactions
    GROUP BY Year_Month, Month_Name
)
SELECT 'Lowest Revenue Month' AS Metric_Type, Year_Month, Month_Name, Monthly_Revenue AS Value
FROM Monthly_Performance
ORDER BY Monthly_Revenue ASC
LIMIT 1;

WITH Monthly_Performance AS (
    SELECT 
        Year_Month, 
        Month_Name, 
        ROUND(SUM(Sales_Amount), 2) AS Monthly_Revenue,
        ROUND(SUM(Profit), 2) AS Monthly_Profit
    FROM sales_transactions
    GROUP BY Year_Month, Month_Name
)
SELECT 'Highest Profit Month' AS Metric_Type, Year_Month, Month_Name, Monthly_Profit AS Value
FROM Monthly_Performance
ORDER BY Monthly_Profit DESC
LIMIT 1;

WITH Monthly_Performance AS (
    SELECT 
        Year_Month, 
        Month_Name, 
        ROUND(SUM(Sales_Amount), 2) AS Monthly_Revenue,
        ROUND(SUM(Profit), 2) AS Monthly_Profit
    FROM sales_transactions
    GROUP BY Year_Month, Month_Name
)
SELECT 'Lowest Profit Month' AS Metric_Type, Year_Month, Month_Name, Monthly_Profit AS Value
FROM Monthly_Performance
ORDER BY Monthly_Profit ASC
LIMIT 1;


-- 4. Day of the Week Purchasing Patterns
SELECT 
    Weekday_Name,
    COUNT(DISTINCT Order_ID) AS Orders_Count,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(AVG(Sales_Amount), 2) AS Avg_Order_Value,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct
FROM sales_transactions
GROUP BY Day_of_Week, Weekday_Name
ORDER BY Day_of_Week;
