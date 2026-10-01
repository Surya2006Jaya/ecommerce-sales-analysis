"""
E-Commerce Sales Raw Dataset Generator
--------------------------------------
Generates a realistic synthetic e-commerce dataset of 11,500+ records across 12 months (2025).
Includes realistic business patterns and intentional real-world data quality issues for data cleaning demonstration.
Reproducible with random seed 42.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

def generate_ecommerce_data(num_records=11500, random_seed=42):
    np.random.seed(random_seed)
    
    # 1. Product Catalog Definition (Category, Sub-Category, Products, Base Price, Base Cost Margin)
    catalog = [
        # Electronics
        ("Electronics", "Audio", "PROD-ELE-001", "Wireless Noise-Canceling Headphones", 149.99, 0.55),
        ("Electronics", "Audio", "PROD-ELE-002", "Bluetooth Portable Speaker", 59.99, 0.50),
        ("Electronics", "Phones & Accessories", "PROD-ELE-003", "Ultra Slim Smartphone Case", 19.99, 0.25),
        ("Electronics", "Phones & Accessories", "PROD-ELE-004", "Fast Wireless Charger Pad", 29.99, 0.40),
        ("Electronics", "Computers", "PROD-ELE-005", "Mechanical Gaming Keyboard", 89.99, 0.60),
        ("Electronics", "Computers", "PROD-ELE-006", "Ergonomic Wireless Mouse", 39.99, 0.45),
        ("Electronics", "Wearables", "PROD-ELE-007", "Fitness Smartwatch Pro", 199.99, 0.65),
        ("Electronics", "Wearables", "PROD-ELE-008", "Activity Tracker Band", 49.99, 0.40),
        
        # Home & Kitchen
        ("Home & Kitchen", "Kitchen Appliances", "PROD-HOM-001", "Digital Air Fryer 5.5L", 119.99, 0.70),
        ("Home & Kitchen", "Kitchen Appliances", "PROD-HOM-002", "Single-Serve Espresso Machine", 159.99, 0.75),
        ("Home & Kitchen", "Kitchenware", "PROD-HOM-003", "Non-Stick Ceramic Cookware Set", 89.99, 0.55),
        ("Home & Kitchen", "Kitchenware", "PROD-HOM-004", "Stainless Steel Knife Set (6pc)", 45.99, 0.45),
        ("Home & Kitchen", "Home Decor", "PROD-HOM-005", "Aroma Essential Oil Diffuser", 24.99, 0.35),
        ("Home & Kitchen", "Home Decor", "PROD-HOM-006", "Dimmable LED Desk Lamp", 34.99, 0.40),
        ("Home & Kitchen", "Bedding", "PROD-HOM-007", "Memory Foam Orthopedic Pillow", 39.99, 0.45),
        
        # Fashion & Apparel
        ("Fashion & Apparel", "Men's Clothing", "PROD-FAS-001", "Men's Slim Fit Cotton Chinos", 44.99, 0.40),
        ("Fashion & Apparel", "Men's Clothing", "PROD-FAS-002", "Classic Oxford Button-Down Shirt", 39.99, 0.35),
        ("Fashion & Apparel", "Women's Clothing", "PROD-FAS-003", "Women's High-Rise Yoga Leggings", 34.99, 0.30),
        ("Fashion & Apparel", "Women's Clothing", "PROD-FAS-004", "Floral Print Maxi Dress", 54.99, 0.38),
        ("Fashion & Apparel", "Footwear", "PROD-FAS-005", "Lightweight Breathable Running Shoes", 79.99, 0.50),
        ("Fashion & Apparel", "Footwear", "PROD-FAS-006", "Casual Canvas Slip-On Sneakers", 49.99, 0.42),
        ("Fashion & Apparel", "Accessories", "PROD-FAS-007", "Genuine Leather RFID Wallet", 29.99, 0.30),
        ("Fashion & Apparel", "Accessories", "PROD-FAS-008", "Polarized UV Sunglasses", 24.99, 0.25),
        
        # Beauty & Personal Care
        ("Beauty & Personal Care", "Skincare", "PROD-BEA-001", "Hydrating Hyaluronic Acid Serum", 28.99, 0.25),
        ("Beauty & Personal Care", "Skincare", "PROD-BEA-002", "Daily SPF 50 Facial Sunscreen", 21.99, 0.28),
        ("Beauty & Personal Care", "Haircare", "PROD-BEA-003", "Argan Oil Repair Hair Mask", 18.99, 0.30),
        ("Beauty & Personal Care", "Haircare", "PROD-BEA-004", "Ionic Hair Dryer 1800W", 69.99, 0.55),
        ("Beauty & Personal Care", "Oral Care", "PROD-BEA-005", "Sonic Rechargeable Electric Toothbrush", 49.99, 0.40),
        
        # Sports & Outdoors
        ("Sports & Outdoors", "Fitness Equipment", "PROD-SPO-001", "Adjustable Dumbbell Set (20kg)", 129.99, 0.72),
        ("Sports & Outdoors", "Fitness Equipment", "PROD-SPO-002", "Non-Slip Eco Yoga Mat (6mm)", 29.99, 0.35),
        ("Sports & Outdoors", "Outdoor Gear", "PROD-SPO-003", "Double Camping Hammock with Straps", 39.99, 0.45),
        ("Sports & Outdoors", "Outdoor Gear", "PROD-SPO-004", "Insulated Stainless Steel Water Bottle (1L)", 22.99, 0.30),
        ("Sports & Outdoors", "Cycling", "PROD-SPO-005", "Waterproof Bike Saddle Bag", 19.99, 0.35),
    ]
    
    catalog_df = pd.DataFrame(catalog, columns=[
        "Product_Category", "Sub_Category", "Product_ID", "Product_Name", "Base_Price", "Cost_Ratio"
    ])
    
    # 2. Regional and Location Profiles
    regions_cities = [
        ("North", "Chicago"), ("North", "Minneapolis"), ("North", "Detroit"), ("North", "Indianapolis"),
        ("South", "Houston"), ("South", "Atlanta"), ("South", "Miami"), ("South", "Dallas"),
        ("East", "New York"), ("East", "Boston"), ("East", "Philadelphia"), ("East", "Washington DC"),
        ("West", "Los Angeles"), ("West", "Seattle"), ("West", "San Francisco"), ("West", "Denver"),
        ("Central", "Kansas City"), ("Central", "St. Louis"), ("Central", "Omaha"), ("Central", "Columbus")
    ]
    
    # Regional traffic weights
    region_weights = [
        0.06, 0.03, 0.03, 0.03, # North ~15%
        0.08, 0.06, 0.05, 0.07, # South ~26%
        0.10, 0.05, 0.05, 0.04, # East ~24%
        0.10, 0.06, 0.06, 0.04, # West ~26%
        0.03, 0.02, 0.02, 0.02  # Central ~9%
    ]
    region_weights = np.array(region_weights) / sum(region_weights)
    
    # 3. Customer Pool (repeat behavior simulation)
    num_customers = 1800
    customer_ids = [f"CUST-{1000 + i}" for i in range(num_customers)]
    
    # Pareto in customer frequency: 20% of customers generate ~50-60% of orders
    cust_weights = np.random.pareto(a=1.5, size=num_customers)
    cust_weights = cust_weights / cust_weights.sum()
    
    # Customer fixed home locations
    cust_locations = {}
    for cid in customer_ids:
        idx = np.random.choice(len(regions_cities), p=region_weights)
        cust_locations[cid] = regions_cities[idx]
        
    # 4. Payment Methods
    payment_methods = ["Credit Card", "Debit Card", "PayPal", "Net Banking", "Cash on Delivery"]
    pm_weights = [0.45, 0.20, 0.20, 0.10, 0.05]
    
    # 5. Order Status
    order_statuses = ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"]
    status_weights = [0.84, 0.06, 0.04, 0.03, 0.03]
    
    # 6. Dates across 2025 (Jan 1, 2025 to Dec 31, 2025) with realistic seasonality
    # Higher sales in Nov/Dec (holiday peak), May/Jul (mid-year promotions)
    start_date = datetime(2025, 1, 1)
    
    # Monthly weight multipliers for seasonality (Jan to Dec)
    month_weights = [0.85, 0.80, 0.90, 0.95, 1.05, 1.00, 1.10, 1.00, 0.95, 1.05, 1.35, 1.45]
    month_weights = np.array(month_weights) / sum(month_weights)
    
    # Pre-sample days
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    records = []
    
    # Generate base clean transactions
    for i in range(num_records):
        order_id = f"ORD-2025-{10001 + i}"
        
        # Pick Month according to seasonal weights
        m_idx = np.random.choice(12, p=month_weights)
        day = np.random.randint(1, days_in_month[m_idx] + 1)
        # Hour and minute
        hour = np.random.randint(8, 23)
        minute = np.random.randint(0, 60)
        order_date = datetime(2025, m_idx + 1, day, hour, minute)
        
        # Pick Customer
        cust_id = np.random.choice(customer_ids, p=cust_weights)
        region, city = cust_locations[cust_id]
        
        # Pick Product
        prod_idx = np.random.choice(len(catalog_df))
        prod = catalog_df.iloc[prod_idx]
        
        # Quantity (typically 1-4, occasionally higher for accessories/bulk)
        if prod["Base_Price"] > 100:
            qty = np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05])
        elif prod["Base_Price"] > 40:
            qty = np.random.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.10, 0.05])
        else:
            qty = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.45, 0.25, 0.15, 0.08, 0.04, 0.03])
            
        unit_price = prod["Base_Price"]
        # Small unit price variance (+- 5%)
        unit_price = round(unit_price * np.random.uniform(0.95, 1.05), 2)
        
        # Discount Percentage (0%, 5%, 10%, 15%, 20%, 25%, 30%)
        # Q4 has slightly higher discount rates
        if m_idx in [10, 11]:
            discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], p=[0.20, 0.15, 0.20, 0.20, 0.12, 0.08, 0.05])
        else:
            discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.45, 0.25, 0.15, 0.10, 0.05])
            
        # Sales Amount
        sales_amt = round(qty * unit_price * (1 - discount), 2)
        
        # Cost Amount (Unit Cost * Qty)
        # Cost ratio varies slightly per batch
        unit_cost = round(unit_price * prod["Cost_Ratio"] * np.random.uniform(0.92, 1.08), 2)
        cost_amt = round(unit_cost * qty, 2)
        
        # Profit and Margin
        profit = round(sales_amt - cost_amt, 2)
        profit_margin = round((profit / sales_amt) * 100, 2) if sales_amt > 0 else 0.0
        
        payment = np.random.choice(payment_methods, p=pm_weights)
        status = np.random.choice(order_statuses, p=status_weights)
        
        records.append({
            "Order_ID": order_id,
            "Order_Date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Customer_ID": cust_id,
            "Product_ID": prod["Product_ID"],
            "Product_Name": prod["Product_Name"],
            "Product_Category": prod["Product_Category"],
            "Sub_Category": prod["Sub_Category"],
            "Quantity": qty,
            "Unit_Price": unit_price,
            "Discount_Percentage": discount,
            "Sales_Amount": sales_amt,
            "Cost_Amount": cost_amt,
            "Profit": profit,
            "Profit_Margin": profit_margin,
            "Customer_Location": city,
            "Region": region,
            "Payment_Method": payment,
            "Order_Status": status
        })
        
    df = pd.DataFrame(records)
    
    # -------------------------------------------------------------
    # INTENTIONAL REAL-WORLD DATA IMPERFECTIONS (Documented for Cleaning)
    # -------------------------------------------------------------
    
    # 1. Duplicate records (~60 rows)
    dup_indices = np.random.choice(df.index, size=60, replace=False)
    dup_rows = df.loc[dup_indices].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # 2. Missing values in non-critical / critical fields
    # Missing Customer_Location (~120 records)
    miss_loc_idx = np.random.choice(df.index, size=120, replace=False)
    df.loc[miss_loc_idx, "Customer_Location"] = np.nan
    
    # Missing Payment_Method (~85 records)
    miss_pm_idx = np.random.choice(df.index, size=85, replace=False)
    df.loc[miss_pm_idx, "Payment_Method"] = np.nan
    
    # Missing Discount_Percentage (~65 records -> should be imputed to 0.0)
    miss_disc_idx = np.random.choice(df.index, size=65, replace=False)
    df.loc[miss_disc_idx, "Discount_Percentage"] = np.nan
    
    # Missing Order_Status (~40 records -> should be imputed to 'Delivered' or 'Unknown')
    miss_st_idx = np.random.choice(df.index, size=40, replace=False)
    df.loc[miss_st_idx, "Order_Status"] = np.nan
    
    # 3. Inconsistent Text Capitalization & Leading/Trailing Whitespace
    # Categories with whitespace and lower/upper case
    messy_cat_idx = np.random.choice(df.index, size=350, replace=False)
    for idx in messy_cat_idx[:100]:
        df.loc[idx, "Product_Category"] = "  " + str(df.loc[idx, "Product_Category"]) + " "
    for idx in messy_cat_idx[100:200]:
        df.loc[idx, "Product_Category"] = str(df.loc[idx, "Product_Category"]).lower()
    for idx in messy_cat_idx[200:300]:
        df.loc[idx, "Product_Category"] = str(df.loc[idx, "Product_Category"]).upper()
    for idx in messy_cat_idx[300:]:
        df.loc[idx, "Region"] = " " + str(df.loc[idx, "Region"]).upper() + "  "

    # Inconsistent Order_Status formatting
    messy_stat_idx = np.random.choice(df.index, size=150, replace=False)
    for idx in messy_stat_idx[:75]:
        if pd.notna(df.loc[idx, "Order_Status"]):
            df.loc[idx, "Order_Status"] = str(df.loc[idx, "Order_Status"]).lower()
    for idx in messy_stat_idx[75:]:
        if pd.notna(df.loc[idx, "Order_Status"]):
            df.loc[idx, "Order_Status"] = " " + str(df.loc[idx, "Order_Status"]) + " "

    # 4. Invalid / Suspicious Values (Negative quantities, discounts as whole numbers, zero prices)
    # Negative quantities (e.g. -1 or -2 due to input sign glitch, 15 records)
    neg_qty_idx = np.random.choice(df.index, size=15, replace=False)
    df.loc[neg_qty_idx, "Quantity"] = -1 * np.random.choice([1, 2, 3], size=15)
    
    # Outlier / Impossible quantity (e.g. 999 or 500 typos, 4 records)
    outlier_qty_idx = np.random.choice(df.index, size=4, replace=False)
    df.loc[outlier_qty_idx, "Quantity"] = [999, 500, 888, 750]
    
    # Discount recorded as percentage integer e.g., 20 instead of 0.20 (25 records)
    pct_int_idx = np.random.choice(df.index, size=25, replace=False)
    df.loc[pct_int_idx, "Discount_Percentage"] = df.loc[pct_int_idx, "Discount_Percentage"] * 100
    
    # 5. Invalid / Inconsistent Calculations
    # Sales_Amount mismatch (e.g., outdated cached calculation, 30 records)
    calc_err_idx = np.random.choice(df.index, size=30, replace=False)
    df.loc[calc_err_idx, "Sales_Amount"] = -99.99  # Negative or corrupted
    
    # Profit calculation glitch (e.g. null profit or wrong sign, 20 records)
    prof_err_idx = np.random.choice(df.index, size=20, replace=False)
    df.loc[prof_err_idx, "Profit"] = 99999.0
    
    # 6. Column name styling variations in raw source
    # We will save standard column names as requested, but ensure cleaning script explicitly verifies and normalizes.
    
    # Shuffle dataframe to distribute duplicates and anomalies realistically
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    os.makedirs("ecommerce-sales-analysis/data/raw", exist_ok=True)
    os.makedirs("ecommerce-sales-analysis/data/cleaned", exist_ok=True)
    os.makedirs("ecommerce-sales-analysis/data/processed", exist_ok=True)
    
    df_raw = generate_ecommerce_data(num_records=11500, random_seed=42)
    raw_path = "ecommerce-sales-analysis/data/raw/ecommerce_sales_raw.csv"
    df_raw.to_csv(raw_path, index=False)
    print(f"Raw dataset successfully generated: {raw_path}")
    print(f"Total rows: {len(df_raw)}, Total columns: {len(df_raw.columns)}")
