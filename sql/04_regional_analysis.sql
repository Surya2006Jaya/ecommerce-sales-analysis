-- ==============================================================================
-- 04_regional_analysis.sql
-- E-Commerce Sales Performance & Customer Behavior Analysis
-- Purpose: Geographical Sales Performance, Regional Profit Margins, and City-level Rankings
-- ==============================================================================

-- 1. High-Level Regional Performance Comparison
-- Ranks geographic regions by revenue, profit, margins, and order volume
SELECT 
    Region,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    COUNT(DISTINCT Customer_ID) AS Total_Customers,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Sales_Amount) * 100.0 / (SELECT SUM(Sales_Amount) FROM sales_transactions), 2) AS Revenue_Share_Pct,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) * 100.0 / (SELECT SUM(Profit) FROM sales_transactions), 2) AS Profit_Share_Pct,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct,
    ROUND(AVG(Sales_Amount), 2) AS Avg_Order_Value
FROM sales_transactions
GROUP BY Region
ORDER BY Total_Revenue DESC;


-- 2. Top Performing Cities by Total Sales
SELECT 
    Customer_Location AS City,
    Region,
    COUNT(DISTINCT Order_ID) AS Order_Count,
    COUNT(DISTINCT Customer_ID) AS Unique_Customers,
    ROUND(SUM(Sales_Amount), 2) AS City_Revenue,
    ROUND(SUM(Profit), 2) AS City_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS City_Profit_Margin_Pct
FROM sales_transactions
GROUP BY Customer_Location, Region
ORDER BY City_Revenue DESC
LIMIT 10;


-- 3. Lowest Performing Cities (Revenue & Margin Opportunities)
SELECT 
    Customer_Location AS City,
    Region,
    COUNT(DISTINCT Order_ID) AS Order_Count,
    ROUND(SUM(Sales_Amount), 2) AS City_Revenue,
    ROUND(SUM(Profit), 2) AS City_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS City_Profit_Margin_Pct
FROM sales_transactions
GROUP BY Customer_Location, Region
ORDER BY City_Revenue ASC
LIMIT 5;


-- 4. Regional Category Preference Matrix (Cross-Tab / Pivot Analysis)
SELECT 
    Region,
    ROUND(SUM(CASE WHEN Product_Category = 'Electronics' THEN Sales_Amount ELSE 0 END), 2) AS Electronics_Sales,
    ROUND(SUM(CASE WHEN Product_Category = 'Fashion & Apparel' THEN Sales_Amount ELSE 0 END), 2) AS Fashion_Sales,
    ROUND(SUM(CASE WHEN Product_Category = 'Home & Kitchen' THEN Sales_Amount ELSE 0 END), 2) AS Home_Kitchen_Sales,
    ROUND(SUM(CASE WHEN Product_Category = 'Beauty & Personal Care' THEN Sales_Amount ELSE 0 END), 2) AS Beauty_Sales,
    ROUND(SUM(CASE WHEN Product_Category = 'Sports & Outdoors' THEN Sales_Amount ELSE 0 END), 2) AS Sports_Sales
FROM sales_transactions
GROUP BY Region
ORDER BY Region;
