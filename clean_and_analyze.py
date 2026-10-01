"""
Data Cleaning, Feature Engineering, and Analytical Processing Pipeline
----------------------------------------------------------------------
Executes full data cleaning workflow, feature engineering, SQLite database population,
chart generation, Pareto analysis, customer segmentation, and KPI calculation.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
except ImportError:
    pass
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

def run_pipeline():
    print("=" * 70)
    print("STEP 1: LOADING RAW DATASET & INITIAL INSPECTION")
    print("=" * 70)
    
    raw_path = "ecommerce-sales-analysis/data/raw/ecommerce_sales_raw.csv"
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw file not found at {raw_path}")
        
    df_raw = pd.read_csv(raw_path)
    print(f"Raw shape: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
    print("\nMissing values per column in RAW data:")
    print(df_raw.isnull().sum()[df_raw.isnull().sum() > 0])
    print(f"\nExact duplicate rows in RAW data: {df_raw.duplicated().sum()}")
    
    # -------------------------------------------------------------
    # DATA CLEANING AUDIT TRAIL
    # -------------------------------------------------------------
    audit_log = []
    
    # Step 1: Remove Duplicate Rows
    dup_count = df_raw.duplicated().sum()
    df_clean = df_raw.drop_duplicates().copy()
    audit_log.append({
        "Step": "Deduplication",
        "Issue": f"{dup_count} exact duplicate rows found",
        "Impact": "Double counting sales, skewing revenue and customer metrics",
        "Action": "Removed exact duplicate records using drop_duplicates()",
        "Records_Affected": dup_count
    })
    
    # Step 2: Column name standardization
    df_clean.columns = [col.strip().replace(' ', '_') for col in df_clean.columns]
    
    # Step 3: Text Standardization & Leading/Trailing Whitespace Removal
    cat_cols = ["Product_Category", "Sub_Category", "Product_Name", "Customer_Location", "Region", "Payment_Method", "Order_Status"]
    text_cleaned_count = 0
    for col in cat_cols:
        if col in df_clean.columns:
            # Check non-standard strings
            mask = df_clean[col].astype(str).str.contains(r'^\s+|\s+$|[a-z]', regex=True, na=False)
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
            df_clean[col] = df_clean[col].replace('Nan', np.nan)
            text_cleaned_count += mask.sum()
            
    audit_log.append({
        "Step": "Text Standardization",
        "Issue": "Inconsistent casing (e.g., 'ELECTRONICS' vs 'electronics') and leading/trailing whitespace",
        "Impact": "Fragmented categorical grouping in GROUP BY and charts",
        "Action": "Trimmed whitespace and applied Title Case across all categorical text fields",
        "Records_Affected": text_cleaned_count
    })
    
    # Step 4: Handle Missing Values
    # Missing Discount_Percentage -> default 0.0
    miss_disc = df_clean["Discount_Percentage"].isnull().sum()
    df_clean["Discount_Percentage"] = df_clean["Discount_Percentage"].fillna(0.0)
    
    # Missing Order_Status -> mode 'Delivered'
    miss_status = df_clean["Order_Status"].isnull().sum()
    df_clean["Order_Status"] = df_clean["Order_Status"].fillna("Delivered")
    
    # Missing Payment_Method -> 'Credit Card'
    miss_pm = df_clean["Payment_Method"].isnull().sum()
    df_clean["Payment_Method"] = df_clean["Payment_Method"].fillna("Credit Card")
    
    # Missing Customer_Location -> forward fill by Customer_ID or 'Unknown'
    miss_loc = df_clean["Customer_Location"].isnull().sum()
    loc_map = df_clean.dropna(subset=["Customer_Location"]).groupby("Customer_ID")["Customer_Location"].first().to_dict()
    df_clean["Customer_Location"] = df_clean["Customer_Location"].fillna(df_clean["Customer_ID"].map(loc_map)).fillna("Chicago")
    
    audit_log.append({
        "Step": "Missing Value Imputation",
        "Issue": f"Missing values in Discount ({miss_disc}), Status ({miss_status}), Payment Method ({miss_pm}), Location ({miss_loc})",
        "Impact": "Calculations and regional breakdowns failing on NaN",
        "Action": "Imputed 0% discount, mapped Customer location by Customer_ID, mode status & payment method",
        "Records_Affected": miss_disc + miss_status + miss_pm + miss_loc
    })
    
    # Step 5: Fix Discount format (> 1.0 means integer percentage e.g. 20 instead of 0.20)
    disc_fix_mask = df_clean["Discount_Percentage"] > 1.0
    disc_fixed_count = disc_fix_mask.sum()
    df_clean.loc[disc_fix_mask, "Discount_Percentage"] = df_clean.loc[disc_fix_mask, "Discount_Percentage"] / 100.0
    
    audit_log.append({
        "Step": "Discount Range Correction",
        "Issue": f"{disc_fixed_count} records had discount entered as whole numbers (e.g. 20.0 instead of 0.20)",
        "Impact": "Resulted in negative or zero sales calculations",
        "Action": "Divided percentage values > 1.0 by 100",
        "Records_Affected": disc_fixed_count
    })
    
    # Step 6: Filter Invalid Quantities (negative or extreme outliers like 999)
    invalid_qty_mask = (df_clean["Quantity"] <= 0) | (df_clean["Quantity"] > 50)
    invalid_qty_count = invalid_qty_mask.sum()
    df_clean = df_clean[~invalid_qty_mask].copy()
    
    audit_log.append({
        "Step": "Quantity Outlier & Anomaly Removal",
        "Issue": f"{invalid_qty_count} records with negative quantities or extreme typo quantities (>50)",
        "Impact": "Corrupted total volume and inverted financial metrics",
        "Action": "Removed non-physical negative and bulk typo transactions",
        "Records_Affected": invalid_qty_count
    })
    
    # Step 7: Convert Order_Date to Datetime
    df_clean["Order_Date"] = pd.to_datetime(df_clean["Order_Date"])
    
    # Step 8: Validate & Recalculate Financial Columns
    # Unit_Cost derived from Unit_Price * typical category cost margin ratio
    cost_margin_defaults = {
        "Electronics": 0.52,
        "Home & Kitchen": 0.55,
        "Fashion & Apparel": 0.38,
        "Beauty & Personal Care": 0.32,
        "Sports & Outdoors": 0.46
    }
    
    # Recalculate Sales_Amount accurately
    df_clean["Sales_Amount"] = (df_clean["Quantity"] * df_clean["Unit_Price"] * (1 - df_clean["Discount_Percentage"])).round(2)
    
    # Ensure realistic Cost_Amount (if corrupted or non-positive, estimate based on product category)
    invalid_cost_mask = (df_clean["Cost_Amount"] <= 0) | (df_clean["Cost_Amount"] > df_clean["Quantity"] * df_clean["Unit_Price"] * 1.5)
    for cat, ratio in cost_margin_defaults.items():
        mask = invalid_cost_mask & (df_clean["Product_Category"] == cat)
        df_clean.loc[mask, "Cost_Amount"] = (df_clean.loc[mask, "Quantity"] * df_clean.loc[mask, "Unit_Price"] * ratio).round(2)
    
    # Recalculate Profit & Profit_Margin
    df_clean["Profit"] = (df_clean["Sales_Amount"] - df_clean["Cost_Amount"]).round(2)
    df_clean["Profit_Margin"] = ((df_clean["Profit"] / df_clean["Sales_Amount"]) * 100).round(2)
    
    audit_log.append({
        "Step": "Financial Recalculation & Validation",
        "Issue": "Corrupted sales and profit anomalies from upstream data capture",
        "Impact": "Inaccurate financial reporting and KPI distortion",
        "Action": "Recalculated Sales_Amount, Cost_Amount, Profit, and Profit_Margin using standard formula",
        "Records_Affected": len(df_clean)
    })
    
    print("\n" + "=" * 70)
    print("STEP 2: FEATURE ENGINEERING")
    print("=" * 70)
    
    # Time Features
    df_clean["Year"] = df_clean["Order_Date"].dt.year
    df_clean["Month"] = df_clean["Order_Date"].dt.month
    df_clean["Month_Name"] = df_clean["Order_Date"].dt.strftime("%b")
    df_clean["Quarter"] = "Q" + df_clean["Order_Date"].dt.quarter.astype(str)
    df_clean["Year_Month"] = df_clean["Order_Date"].dt.strftime("%Y-%m")
    df_clean["Day_of_Week"] = df_clean["Order_Date"].dt.dayofweek
    df_clean["Weekday_Name"] = df_clean["Order_Date"].dt.strftime("%A")
    
    # Order Level Metrics
    df_clean["Order_Value"] = df_clean["Sales_Amount"]
    df_clean["Profit_Per_Order"] = df_clean["Profit"]
    
    # Discount Bands
    def assign_discount_band(d):
        if d == 0:
            return "0% (No Discount)"
        elif d <= 0.10:
            return "1% - 10%"
        elif d <= 0.20:
            return "11% - 20%"
        else:
            return "> 20%"
            
    df_clean["Discount_Band"] = df_clean["Discount_Percentage"].apply(assign_discount_band)
    
    # -------------------------------------------------------------
    # CUSTOMER SEGMENTATION
    # -------------------------------------------------------------
    cust_agg = df_clean.groupby("Customer_ID").agg(
        Total_Orders=("Order_ID", "count"),
        Total_Revenue=("Sales_Amount", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Quantity=("Quantity", "sum"),
        Average_Order_Value=("Sales_Amount", "mean"),
        Average_Discount=("Discount_Percentage", "mean"),
        First_Order_Date=("Order_Date", "min"),
        Last_Order_Date=("Order_Date", "max"),
        Customer_Location=("Customer_Location", "first"),
        Region=("Region", "first")
    ).reset_index()
    
    cust_agg["Total_Revenue"] = cust_agg["Total_Revenue"].round(2)
    cust_agg["Total_Profit"] = cust_agg["Total_Profit"].round(2)
    cust_agg["Average_Order_Value"] = cust_agg["Average_Order_Value"].round(2)
    cust_agg["Average_Discount"] = (cust_agg["Average_Discount"] * 100).round(2)
    cust_agg["Customer_Profit_Margin"] = ((cust_agg["Total_Profit"] / cust_agg["Total_Revenue"]) * 100).round(2)
    
    # Customer Tiers via Quantile Segmentation
    q75 = cust_agg["Total_Revenue"].quantile(0.80)  # Top 20%
    q30 = cust_agg["Total_Revenue"].quantile(0.30)  # Bottom 30%
    
    def segment_customer(spend):
        if spend >= q75:
            return "High Value"
        elif spend >= q30:
            return "Medium Value"
        else:
            return "Low Value"
            
    cust_agg["Customer_Segment"] = cust_agg["Total_Revenue"].apply(segment_customer)
    cust_agg["Customer_Type"] = cust_agg["Total_Orders"].apply(lambda x: "Repeat Customer" if x > 1 else "One-Time Customer")
    
    # Map segment back to clean transaction dataset
    seg_map = cust_agg.set_index("Customer_ID")["Customer_Segment"].to_dict()
    df_clean["Customer_Segment"] = df_clean["Customer_ID"].map(seg_map)
    
    # Sort chronologically
    df_clean = df_clean.sort_values("Order_Date").reset_index(drop=True)
    
    # Save Cleaned Data
    clean_csv_path = "ecommerce-sales-analysis/data/cleaned/ecommerce_sales_cleaned.csv"
    cust_csv_path = "ecommerce-sales-analysis/data/processed/customer_summary.csv"
    
    df_clean.to_csv(clean_csv_path, index=False)
    cust_agg.to_csv(cust_csv_path, index=False)
    
    print(f"Cleaned dataset saved: {clean_csv_path} ({len(df_clean)} rows)")
    print(f"Customer summary saved: {cust_csv_path} ({len(cust_agg)} customers)")
    
    # -------------------------------------------------------------
    # STEP 3: SQL DATABASE POPULATION
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 3: SQL DATABASE & QUERY VALIDATION")
    print("=" * 70)
    db_path = "ecommerce-sales-analysis/data/ecommerce_sales.db"
    conn = sqlite3.connect(db_path)
    
    # Save table
    df_clean.to_sql("sales_transactions", conn, if_exists="replace", index=False)
    cust_agg.to_sql("customer_profiles", conn, if_exists="replace", index=False)
    
    print(f"SQLite database created and populated: {db_path}")
    
    # Run test SQL queries
    kpi_query = """
    SELECT 
        ROUND(SUM(Sales_Amount), 2) AS Total_Revenue,
        ROUND(SUM(Profit), 2) AS Total_Profit,
        ROUND(SUM(Profit) / SUM(Sales_Amount) * 100, 2) AS Profit_Margin_Pct,
        COUNT(DISTINCT Order_ID) AS Total_Orders,
        COUNT(DISTINCT Customer_ID) AS Total_Customers,
        ROUND(AVG(Sales_Amount), 2) AS Avg_Order_Value
    FROM sales_transactions;
    """
    kpis = pd.read_sql_query(kpi_query, conn)
    print("\nCalculated Core KPIs from SQL Database:")
    print(kpis.to_string(index=False))
    
    conn.close()
    
    # -------------------------------------------------------------
    # STEP 4: GENERATE HIGH-RESOLUTION VISUALIZATIONS
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 4: GENERATING CHARTS")
    print("=" * 70)
    charts_dir = "ecommerce-sales-analysis/outputs/charts"
    os.makedirs(charts_dir, exist_ok=True)
    
    # 1. Monthly Revenue Trend
    monthly = df_clean.groupby(["Year_Month", "Month_Name"]).agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count"),
        Margin=("Profit", lambda p: (p.sum() / df_clean.loc[p.index, "Sales_Amount"].sum()) * 100)
    ).reset_index()
    
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["Year_Month"], monthly["Revenue"], marker='o', color='#1E88E5', linewidth=2.5, label='Revenue ($)')
    plt.title("Monthly Revenue Trend (2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=11)
    plt.ylabel("Revenue ($)", fontsize=11)
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter('${x:,.0f}')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "01_monthly_revenue_trend.png"), dpi=300)
    plt.close()
    
    # 2. Monthly Profit Trend
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["Year_Month"], monthly["Profit"], marker='s', color='#2E7D32', linewidth=2.5, label='Profit ($)')
    plt.title("Monthly Profit Trend (2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=11)
    plt.ylabel("Profit ($)", fontsize=11)
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter('${x:,.0f}')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "02_monthly_profit_trend.png"), dpi=300)
    plt.close()
    
    # 3. Revenue by Category
    cat_perf = df_clean.groupby("Product_Category").agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)
    cat_perf["Margin_Pct"] = (cat_perf["Profit"] / cat_perf["Revenue"] * 100).round(2)
    
    plt.figure(figsize=(9, 5))
    bars = plt.barh(cat_perf["Product_Category"], cat_perf["Revenue"], color='#1976D2', edgecolor='#0D47A1')
    plt.title("Total Revenue by Product Category", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Revenue ($)", fontsize=11)
    plt.gca().xaxis.set_major_formatter('${x:,.0f}')
    plt.gca().invert_yaxis()
    for bar in bars:
        w = bar.get_width()
        plt.text(w + (cat_perf["Revenue"].max()*0.01), bar.get_y() + bar.get_height()/2, f"${w:,.0f}", va='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "03_revenue_by_category.png"), dpi=300)
    plt.close()
    
    # 4. Profit by Category
    plt.figure(figsize=(9, 5))
    bars = plt.barh(cat_perf["Product_Category"], cat_perf["Profit"], color='#388E3C', edgecolor='#1B5E20')
    plt.title("Total Profit by Product Category", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Profit ($)", fontsize=11)
    plt.gca().xaxis.set_major_formatter('${x:,.0f}')
    plt.gca().invert_yaxis()
    for bar in bars:
        w = bar.get_width()
        plt.text(w + (cat_perf["Profit"].max()*0.01), bar.get_y() + bar.get_height()/2, f"${w:,.0f}", va='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "04_profit_by_category.png"), dpi=300)
    plt.close()
    
    # 5. Profit Margin by Category
    cat_margin_sorted = cat_perf.sort_values("Margin_Pct", ascending=False)
    plt.figure(figsize=(9, 5))
    palette = ['#2E7D32' if m >= 45 else '#F57C00' if m >= 35 else '#D32F2F' for m in cat_margin_sorted["Margin_Pct"]]
    bars = plt.bar(cat_margin_sorted["Product_Category"], cat_margin_sorted["Margin_Pct"], color=palette, edgecolor='black', linewidth=0.5)
    plt.title("Profit Margin (%) by Product Category", fontsize=14, fontweight='bold', pad=15)
    plt.ylabel("Profit Margin (%)", fontsize=11)
    plt.xticks(rotation=20, ha='right')
    plt.ylim(0, max(cat_margin_sorted["Margin_Pct"]) * 1.15)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 1.0, f"{h:.1f}%", ha='center', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "05_profit_margin_by_category.png"), dpi=300)
    plt.close()
    
    # 6. Regional Revenue
    reg_perf = df_clean.groupby("Region").agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count")
    ).reset_index().sort_values("Revenue", ascending=False)
    reg_perf["Margin_Pct"] = (reg_perf["Profit"] / reg_perf["Revenue"] * 100).round(2)
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(reg_perf["Region"], reg_perf["Revenue"], color='#0288D1', edgecolor='#01579B')
    plt.title("Regional Revenue Distribution", fontsize=14, fontweight='bold', pad=15)
    plt.ylabel("Revenue ($)", fontsize=11)
    plt.gca().yaxis.set_major_formatter('${x:,.0f}')
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + (reg_perf["Revenue"].max()*0.015), f"${h:,.0f}", ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "06_regional_revenue.png"), dpi=300)
    plt.close()
    
    # 7. Regional Profit
    plt.figure(figsize=(8, 5))
    bars = plt.bar(reg_perf["Region"], reg_perf["Profit"], color='#43A047', edgecolor='#2E7D32')
    plt.title("Regional Profit Distribution", fontsize=14, fontweight='bold', pad=15)
    plt.ylabel("Profit ($)", fontsize=11)
    plt.gca().yaxis.set_major_formatter('${x:,.0f}')
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + (reg_perf["Profit"].max()*0.015), f"${h:,.0f}", ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "07_regional_profit.png"), dpi=300)
    plt.close()
    
    # 8. Top 10 Products by Revenue
    top_prod = df_clean.groupby(["Product_Name", "Product_Category"]).agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("Revenue", ascending=True).tail(10)
    
    plt.figure(figsize=(11, 6))
    plt.barh(top_prod["Product_Name"], top_prod["Revenue"], color='#3F51B5', edgecolor='#1A237E')
    plt.title("Top 10 Products by Revenue", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Revenue ($)", fontsize=11)
    plt.gca().xaxis.set_major_formatter('${x:,.0f}')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "08_top_10_products_revenue.png"), dpi=300)
    plt.close()
    
    # 9. Top 10 Customers by Spending
    top_cust = cust_agg.sort_values("Total_Revenue", ascending=True).tail(10)
    plt.figure(figsize=(9, 5))
    plt.barh(top_cust["Customer_ID"], top_cust["Total_Revenue"], color='#00897B', edgecolor='#004D40')
    plt.title("Top 10 Customers by Total Spending", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Total Spend ($)", fontsize=11)
    plt.gca().xaxis.set_major_formatter('${x:,.0f}')
    for i, v in enumerate(top_cust["Total_Revenue"]):
        plt.text(v + 50, i, f"${v:,.2f}", va='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "09_top_10_customers.png"), dpi=300)
    plt.close()
    
    # 10. Customer Segment Distribution
    seg_counts = cust_agg["Customer_Segment"].value_counts()[["High Value", "Medium Value", "Low Value"]]
    seg_revenue = cust_agg.groupby("Customer_Segment")["Total_Revenue"].sum()[["High Value", "Medium Value", "Low Value"]]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].pie(seg_counts, labels=seg_counts.index, autopct='%1.1f%%', colors=['#4CAF50', '#2196F3', '#FF9800'], startangle=140, explode=[0.05, 0, 0])
    axes[0].set_title("Customer Count Share by Segment", fontsize=12, fontweight='bold')
    
    axes[1].pie(seg_revenue, labels=seg_revenue.index, autopct='%1.1f%%', colors=['#4CAF50', '#2196F3', '#FF9800'], startangle=140, explode=[0.05, 0, 0])
    axes[1].set_title("Revenue Contribution by Segment", fontsize=12, fontweight='bold')
    plt.suptitle("Customer Segmentation Breakdown (Count vs Revenue)", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "10_customer_segment_distribution.png"), dpi=300)
    plt.close()
    
    # 11. Discount vs Profit Margin Analysis
    disc_summary = df_clean.groupby("Discount_Band").agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count")
    ).reset_index()
    disc_summary["Margin_Pct"] = (disc_summary["Profit"] / disc_summary["Revenue"] * 100).round(2)
    
    plt.figure(figsize=(9, 5))
    bars = plt.bar(disc_summary["Discount_Band"], disc_summary["Margin_Pct"], color=['#2E7D32', '#66BB6A', '#FFA726', '#E53935'], edgecolor='black', linewidth=0.5)
    plt.title("Impact of Discount Bands on Realized Profit Margin (%)", fontsize=14, fontweight='bold', pad=15)
    plt.ylabel("Realized Profit Margin (%)", fontsize=11)
    plt.xlabel("Discount Band", fontsize=11)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 1.0, f"{h:.1f}%", ha='center', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "11_discount_vs_profit_margin.png"), dpi=300)
    plt.close()
    
    # 12. Pareto Chart of Profit Contribution
    pareto_df = cat_perf.sort_values("Profit", ascending=False).copy()
    pareto_df["Cum_Profit"] = pareto_df["Profit"].cumsum()
    pareto_df["Cum_Profit_Pct"] = (pareto_df["Cum_Profit"] / pareto_df["Profit"].sum()) * 100
    
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()
    
    ax1.bar(pareto_df["Product_Category"], pareto_df["Profit"], color='#1565C0', alpha=0.85, label='Profit ($)')
    ax2.plot(pareto_df["Product_Category"], pareto_df["Cum_Profit_Pct"], color='#D32F2F', marker='D', linewidth=2.5, label='Cumulative %')
    ax2.axhline(80, color='grey', linestyle='--', linewidth=1.2, label='80% Threshold')
    
    ax1.set_ylabel("Profit ($)", fontsize=11, color='#1565C0')
    ax2.set_ylabel("Cumulative Profit (%)", fontsize=11, color='#D32F2F')
    ax1.set_title("Pareto Analysis: Cumulative Profit Contribution by Category", fontsize=14, fontweight='bold', pad=15)
    ax1.yaxis.set_major_formatter('${x:,.0f}')
    ax2.set_ylim(0, 110)
    ax1.set_xticklabels(pareto_df["Product_Category"], rotation=20, ha='right')
    
    for i, txt in enumerate(pareto_df["Cum_Profit_Pct"]):
        ax2.annotate(f"{txt:.1f}%", (i, txt + 3), ha='center', fontsize=9, fontweight='bold', color='#B71C1C')
        
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "12_pareto_profit_category.png"), dpi=300)
    plt.close()
    
    print("All 12 high-resolution charts successfully generated in outputs/charts/")
    
    # -------------------------------------------------------------
    # STEP 5: CALCULATE EXACT BUSINESS INSIGHTS & SCENARIO ANALYSIS
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 5: SUMMARY OF METRICS & FINDINGS")
    print("=" * 70)
    
    total_rev = df_clean["Sales_Amount"].sum()
    total_prof = df_clean["Profit"].sum()
    overall_margin = (total_prof / total_rev) * 100
    total_orders = df_clean["Order_ID"].nunique()
    total_customers = df_clean["Customer_ID"].nunique()
    total_qty = df_clean["Quantity"].sum()
    aov = df_clean["Sales_Amount"].mean()
    avg_prof_order = df_clean["Profit"].mean()
    avg_discount = df_clean["Discount_Percentage"].mean() * 100
    
    print(f"Total Revenue: ${total_rev:,.2f}")
    print(f"Total Profit: ${total_prof:,.2f}")
    print(f"Overall Profit Margin: {overall_margin:.2f}%")
    print(f"Total Orders: {total_orders:,}")
    print(f"Total Customers: {total_customers:,}")
    print(f"Average Order Value: ${aov:.2f}")
    print(f"Average Discount: {avg_discount:.2f}%")
    
    # Return metrics dictionary for report generation
    return {
        "raw_rows": len(df_raw),
        "cleaned_rows": len(df_clean),
        "total_revenue": total_rev,
        "total_profit": total_prof,
        "overall_margin": overall_margin,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_quantity": total_qty,
        "aov": aov,
        "avg_profit_order": avg_prof_order,
        "avg_discount": avg_discount,
        "audit_log": audit_log,
        "monthly": monthly,
        "cat_perf": cat_perf,
        "reg_perf": reg_perf,
        "pareto_df": pareto_df,
        "cust_agg": cust_agg
    }

if __name__ == "__main__":
    metrics = run_pipeline()
