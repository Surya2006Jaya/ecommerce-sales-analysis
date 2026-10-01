-- ==============================================================================
-- 01_basic_analysis.sql
-- E-Commerce Sales Performance & Customer Behavior Analysis
-- Purpose: Calculate foundational business KPIs and aggregate performance metrics
-- ==============================================================================

-- 1. Overall Business KPIs Summary
-- Calculates Total Revenue, Total Cost, Total Gross Profit, Overall Profit Margin %,
-- Total Unique Orders, Total Unique Customers, Total Quantity Sold, and Average Order Value (AOV)
SELECT 
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Cost_Amount), 2) AS Total_Cost,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Overall_Profit_Margin_Pct,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    COUNT(DISTINCT Customer_ID) AS Total_Customers,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(AVG(Sales_Amount), 2) AS Avg_Order_Value,
    ROUND(AVG(Profit), 2) AS Avg_Profit_Per_Order,
    ROUND(AVG(Discount_Percentage) * 100, 2) AS Avg_Discount_Pct
FROM sales_transactions;


-- 2. Performance Breakdown by Order Status
-- Analyzes fulfillment pipeline and financial realization by status
SELECT 
    Order_Status,
    COUNT(DISTINCT Order_ID) AS Order_Count,
    ROUND(COUNT(DISTINCT Order_ID) * 100.0 / (SELECT COUNT(DISTINCT Order_ID) FROM sales_transactions), 2) AS Order_Share_Pct,
    ROUND(SUM(Sales_Amount), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct
FROM sales_transactions
GROUP BY Order_Status
ORDER BY Order_Count DESC;


-- 3. Payment Method Distribution and Profitability
-- Evaluates channel preferences and transaction profitability across payment options
SELECT 
    Payment_Method,
    COUNT(DISTINCT Order_ID) AS Transaction_Count,
    ROUND(SUM(Sales_Amount), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(AVG(Sales_Amount), 2) AS Avg_Ticket_Size,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct
FROM sales_transactions
GROUP BY Payment_Method
ORDER BY Total_Sales DESC;
