-- ==============================================================================
-- 02_product_analysis.sql
-- E-Commerce Sales Performance & Customer Behavior Analysis
-- Purpose: Category, Sub-Category, and Product-level Performance, Margins, and Pareto Analysis
-- ==============================================================================

-- 1. Product Category Performance Summary
-- Evaluates Revenue, Profit, Volume, and Profit Margin across all 5 major categories
SELECT 
    Product_Category,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct,
    ROUND(AVG(Discount_Percentage) * 100, 2) AS Avg_Discount_Pct
FROM sales_transactions
GROUP BY Product_Category
ORDER BY Total_Revenue DESC;


-- 2. Sub-Category Granular Margin and Profit Analysis
-- Uncovers high-volume vs high-margin sub-categories
SELECT 
    Product_Category,
    Sub_Category,
    SUM(Quantity) AS Units_Sold,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct
FROM sales_transactions
GROUP BY Product_Category, Sub_Category
ORDER BY Total_Profit DESC;


-- 3. Top 10 Best-Selling Products by Total Revenue
SELECT 
    Product_ID,
    Product_Name,
    Product_Category,
    SUM(Quantity) AS Units_Sold,
    ROUND(AVG(Unit_Price), 2) AS Avg_Selling_Price,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Realized_Margin_Pct
FROM sales_transactions
GROUP BY Product_ID, Product_Name, Product_Category
ORDER BY Total_Revenue DESC
LIMIT 10;


-- 4. Top 10 Most Profitable Products
SELECT 
    Product_ID,
    Product_Name,
    Product_Category,
    SUM(Quantity) AS Units_Sold,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Realized_Margin_Pct
FROM sales_transactions
GROUP BY Product_ID, Product_Name, Product_Category
ORDER BY Total_Profit DESC
LIMIT 10;


-- 5. Bottom 5 Least Profitable Products (Margin Leakage Identification)
SELECT 
    Product_ID,
    Product_Name,
    Product_Category,
    SUM(Quantity) AS Units_Sold,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Realized_Margin_Pct,
    ROUND(AVG(Discount_Percentage) * 100, 2) AS Avg_Discount_Pct
FROM sales_transactions
GROUP BY Product_ID, Product_Name, Product_Category
ORDER BY Total_Profit ASC
LIMIT 5;


-- 6. Discount Impact Analysis across Discount Bands
-- Assesses how aggressive discounting impacts realized gross margin %
SELECT 
    Discount_Band,
    COUNT(DISTINCT Order_ID) AS Orders_Count,
    SUM(Quantity) AS Units_Sold,
    ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Realized_Margin_Pct
FROM sales_transactions
GROUP BY Discount_Band
ORDER BY 
    CASE 
        WHEN Discount_Band = '0% (No Discount)' THEN 1
        WHEN Discount_Band = '1% - 10%' THEN 2
        WHEN Discount_Band = '11% - 20%' THEN 3
        ELSE 4
    END;


-- 7. Pareto Cumulative Profit Analysis by Category (Window Functions)
WITH Category_Totals AS (
    SELECT 
        Product_Category,
        ROUND(SUM(Profit), 2) AS Category_Profit
    FROM sales_transactions
    GROUP BY Product_Category
)
SELECT 
    Product_Category,
    Category_Profit,
    ROUND(Category_Profit * 100.0 / SUM(Category_Profit) OVER(), 2) AS Profit_Share_Pct,
    ROUND(SUM(Category_Profit) OVER(ORDER BY Category_Profit DESC) * 100.0 / SUM(Category_Profit) OVER(), 2) AS Cumulative_Profit_Pct
FROM Category_Totals
ORDER BY Category_Profit DESC;
