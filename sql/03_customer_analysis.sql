-- ==============================================================================
-- 03_customer_analysis.sql
-- E-Commerce Sales Performance & Customer Behavior Analysis
-- Purpose: Customer Lifetime Value, Segmentation, Repeat vs One-Time Behavior, and Top Spenders
-- ==============================================================================

-- 1. Customer Spending Tiers Summary
-- Analyzes customer count, order frequency, revenue contribution, and margin across segments
SELECT 
    Customer_Segment,
    COUNT(DISTINCT Customer_ID) AS Total_Customers,
    ROUND(COUNT(DISTINCT Customer_ID) * 100.0 / (SELECT COUNT(DISTINCT Customer_ID) FROM customer_profiles), 2) AS Customer_Share_Pct,
    SUM(Total_Orders) AS Total_Orders_Placed,
    ROUND(SUM(Total_Revenue), 2) AS Total_Segment_Revenue,
    ROUND(SUM(Total_Revenue) * 100.0 / (SELECT SUM(Total_Revenue) FROM customer_profiles), 2) AS Revenue_Share_Pct,
    ROUND(SUM(Total_Profit), 2) AS Total_Segment_Profit,
    ROUND(SUM(Total_Profit) / SUM(Total_Revenue) * 100, 2) AS Segment_Profit_Margin_Pct,
    ROUND(AVG(Average_Order_Value), 2) AS Avg_AOV_Per_Customer
FROM customer_profiles
GROUP BY Customer_Segment
ORDER BY Total_Segment_Revenue DESC;


-- 2. Repeat vs One-Time Customer Comparison
-- Evaluates retention power and value difference between repeat buyers and single-purchase users
SELECT 
    Customer_Type,
    COUNT(DISTINCT Customer_ID) AS Customer_Count,
    ROUND(COUNT(DISTINCT Customer_ID) * 100.0 / (SELECT COUNT(DISTINCT Customer_ID) FROM customer_profiles), 2) AS Customer_Pct,
    SUM(Total_Orders) AS Total_Orders,
    ROUND(SUM(Total_Revenue), 2) AS Total_Revenue,
    ROUND(SUM(Total_Revenue) * 100.0 / (SELECT SUM(Total_Revenue) FROM customer_profiles), 2) AS Revenue_Contribution_Pct,
    ROUND(SUM(Total_Profit), 2) AS Total_Profit,
    ROUND(AVG(Total_Revenue), 2) AS Avg_Spend_Per_Customer
FROM customer_profiles
GROUP BY Customer_Type;


-- 3. Top 10 Highest-Value Customers (VIP Accounts)
SELECT 
    Customer_ID,
    Customer_Location,
    Region,
    Total_Orders,
    Total_Quantity,
    Total_Revenue,
    Total_Profit,
    Customer_Profit_Margin,
    Average_Order_Value,
    First_Order_Date,
    Last_Order_Date
FROM customer_profiles
ORDER BY Total_Revenue DESC
LIMIT 10;


-- 4. Top 10% Spenders Concentration Analysis (Quantile / NTILE Window Function)
WITH Customer_Deciles AS (
    SELECT 
        Customer_ID,
        Total_Revenue,
        Total_Profit,
        NTILE(10) OVER (ORDER BY Total_Revenue DESC) AS Decile_Rank
    FROM customer_profiles
)
SELECT 
    CASE 
        WHEN Decile_Rank = 1 THEN 'Top 10% Spenders'
        ELSE 'Remaining 90% Customers'
    END AS Customer_Group,
    COUNT(Customer_ID) AS Customer_Count,
    ROUND(SUM(Total_Revenue), 2) AS Group_Revenue,
    ROUND(SUM(Total_Revenue) * 100.0 / (SELECT SUM(Total_Revenue) FROM customer_profiles), 2) AS Revenue_Share_Pct,
    ROUND(SUM(Total_Profit), 2) AS Group_Profit,
    ROUND(SUM(Total_Profit) / SUM(Total_Revenue) * 100, 2) AS Realized_Margin_Pct
FROM Customer_Deciles
GROUP BY 
    CASE 
        WHEN Decile_Rank = 1 THEN 'Top 10% Spenders'
        ELSE 'Remaining 90% Customers'
    END
ORDER BY Group_Revenue DESC;


-- 5. Frequency Distribution (Number of Orders per Customer)
SELECT 
    Total_Orders AS Orders_Placed,
    COUNT(Customer_ID) AS Customer_Count,
    ROUND(SUM(Total_Revenue), 2) AS Total_Revenue_Generated,
    ROUND(AVG(Total_Revenue), 2) AS Avg_Revenue_Per_User
FROM customer_profiles
GROUP BY Total_Orders
ORDER BY Orders_Placed ASC;
