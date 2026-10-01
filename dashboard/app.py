"""
Interactive Streamlit Dashboard
-------------------------------
E-Commerce Sales Performance & Customer Insights
Provides interactive filtering, dynamic KPI calculations, multi-section analytical deep-dives,
and scenario simulation for executive decision-making.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="E-Commerce Sales & Customer Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern, Premium Data Analytics Interface
st.markdown("""
<style>
    /* Metric Cards Styling */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 20px;
        color: #F8FAFC;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 4px;
        color: #10B981;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1E293B;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 6px;
        margin-top: 24px;
        margin-bottom: 18px;
    }
    
    /* Insight Callouts */
    .insight-box {
        background-color: #F0F9FF;
        border-left: 4px solid #0284C7;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 14px;
    }
    .insight-title {
        font-weight: 700;
        color: #0369A1;
        font-size: 1rem;
        margin-bottom: 4px;
    }
    .insight-body {
        font-size: 0.92rem;
        color: #334155;
        line-height: 1.5;
    }
    
    /* Hide Streamlit Default Header Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to locate dataset regardless of working directory
@st.cache_data
def load_data():
    possible_paths = [
        "ecommerce-sales-analysis/data/cleaned/ecommerce_sales_cleaned.csv",
        "data/cleaned/ecommerce_sales_cleaned.csv",
        "../data/cleaned/ecommerce_sales_cleaned.csv",
        os.path.join(os.path.dirname(__file__), "..", "data", "cleaned", "ecommerce_sales_cleaned.csv")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            df["Order_Date"] = pd.to_datetime(df["Order_Date"])
            return df
    raise FileNotFoundError("Cleaned dataset not found. Please run clean_and_analyze.py first.")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# -------------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/analytics.png", width=64)
st.sidebar.title("Analytics Filters")
st.sidebar.markdown("Filter transactions dynamically:")

# 1. Date Range
min_date = df["Order_Date"].dt.date.min()
max_date = df["Order_Date"].dt.date.max()
date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# 2. Region
all_regions = sorted(df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", options=all_regions, default=all_regions)

# 3. Product Category
all_cats = sorted(df["Product_Category"].dropna().unique().tolist())
selected_cats = st.sidebar.multiselect("Product Category", options=all_cats, default=all_cats)

# 4. Sub-Category (Dynamic based on category selection)
available_subs = sorted(df[df["Product_Category"].isin(selected_cats)]["Sub_Category"].dropna().unique().tolist())
selected_subs = st.sidebar.multiselect("Sub-Category", options=available_subs, default=available_subs)

# 5. Customer Segment
all_segs = ["High Value", "Medium Value", "Low Value"]
selected_segs = st.sidebar.multiselect("Customer Segment", options=all_segs, default=all_segs)

# 6. Order Status
all_statuses = sorted(df["Order_Status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect("Order Status", options=all_statuses, default=all_statuses)

# Filter Dataframe
if len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = df[
        (df["Order_Date"].dt.date >= start_d) &
        (df["Order_Date"].dt.date <= end_d) &
        (df["Region"].isin(selected_regions)) &
        (df["Product_Category"].isin(selected_cats)) &
        (df["Sub_Category"].isin(selected_subs)) &
        (df["Customer_Segment"].isin(selected_segs)) &
        (df["Order_Status"].isin(selected_statuses))
    ].copy()
else:
    filtered_df = df.copy()

if filtered_df.empty:
    st.warning("No transactions match the selected filter criteria. Please broaden your selection.")
    st.stop()

# -------------------------------------------------------------
# MAIN DASHBOARD HEADER
# -------------------------------------------------------------
st.title("🛍️ E-Commerce Sales Performance & Customer Insights")
st.markdown("An executive business analytics dashboard monitoring financial health, product profitability, customer lifetime value, and growth opportunities.")

# -------------------------------------------------------------
# TOP KPI CARDS (Calculated Dynamically)
# -------------------------------------------------------------
tot_rev = filtered_df["Sales_Amount"].sum()
tot_prof = filtered_df["Profit"].sum()
prof_margin = (tot_prof / tot_rev * 100) if tot_rev > 0 else 0.0
tot_orders = filtered_df["Order_ID"].nunique()
tot_customers = filtered_df["Customer_ID"].nunique()
aov = filtered_df["Sales_Amount"].mean() if not filtered_df.empty else 0.0

kpi_cols = st.columns(6)
kpi_cols[0].markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Revenue</div>
    <div class="metric-value">${tot_rev:,.0f}</div>
    <div class="metric-delta">Gross Volume</div>
</div>
""", unsafe_allow_html=True)

kpi_cols[1].markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Profit</div>
    <div class="metric-value">${tot_prof:,.0f}</div>
    <div class="metric-delta">Net Gross Profit</div>
</div>
""", unsafe_allow_html=True)

kpi_cols[2].markdown(f"""
<div class="metric-card">
    <div class="metric-label">Profit Margin</div>
    <div class="metric-value">{prof_margin:.1f}%</div>
    <div class="metric-delta">Realized Margin</div>
</div>
""", unsafe_allow_html=True)

kpi_cols[3].markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Orders</div>
    <div class="metric-value">{tot_orders:,}</div>
    <div class="metric-delta">Transactions</div>
</div>
""", unsafe_allow_html=True)

kpi_cols[4].markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Customers</div>
    <div class="metric-value">{tot_customers:,}</div>
    <div class="metric-delta">Active Buyers</div>
</div>
""", unsafe_allow_html=True)

kpi_cols[5].markdown(f"""
<div class="metric-card">
    <div class="metric-label">Avg Order Value</div>
    <div class="metric-value">${aov:.2f}</div>
    <div class="metric-delta">Per Order Spend</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# TABS FOR NAVIGATION
# -------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Overview",
    "📦 Product Performance",
    "👥 Customer Insights",
    "🗺️ Regional Performance",
    "💡 Business Insights & Scenario Target"
])

# Try importing plotly for interactive charts, else use altair/streamlit
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-title">Monthly Revenue & Profit Growth Trends</div>', unsafe_allow_html=True)
    
    monthly_data = filtered_df.groupby("Year_Month").agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "count")
    ).reset_index()
    
    if HAS_PLOTLY:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly_data["Year_Month"], y=monthly_data["Revenue"],
            name="Revenue ($)", marker_color="#3B82F6"
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_data["Year_Month"], y=monthly_data["Profit"],
            name="Profit ($)", mode="lines+markers", line=dict(color="#10B981", width=3)
        ))
        fig_trend.update_layout(
            title="Monthly Revenue vs. Profit Trajectory",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.line_chart(monthly_data.set_index("Year_Month")[["Revenue", "Profit"]])
        
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Revenue by Product Category</div>', unsafe_allow_html=True)
        cat_rev = filtered_df.groupby("Product_Category")["Sales_Amount"].sum().reset_index().sort_values("Sales_Amount", ascending=False)
        if HAS_PLOTLY:
            fig_cat_rev = px.bar(
                cat_rev, x="Sales_Amount", y="Product_Category", orientation='h',
                labels={"Sales_Amount": "Revenue ($)", "Product_Category": "Category"},
                color="Sales_Amount", color_continuous_scale="Blues"
            )
            fig_cat_rev.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
            st.plotly_chart(fig_cat_rev, use_container_width=True)
        else:
            st.bar_chart(cat_rev.set_index("Product_Category"))
            
    with c2:
        st.markdown('<div class="section-title">Profit by Product Category</div>', unsafe_allow_html=True)
        cat_prof = filtered_df.groupby("Product_Category")["Profit"].sum().reset_index().sort_values("Profit", ascending=False)
        if HAS_PLOTLY:
            fig_cat_prof = px.bar(
                cat_prof, x="Profit", y="Product_Category", orientation='h',
                labels={"Profit": "Profit ($)", "Product_Category": "Category"},
                color="Profit", color_continuous_scale="Greens"
            )
            fig_cat_prof.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
            st.plotly_chart(fig_cat_prof, use_container_width=True)
        else:
            st.bar_chart(cat_prof.set_index("Product_Category"))

# -------------------------------------------------------------
# TAB 2: PRODUCT PERFORMANCE
# -------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-title">Category & Sub-Category Financial Matrix</div>', unsafe_allow_html=True)
    
    cat_summary = filtered_df.groupby("Product_Category").agg(
        Orders=("Order_ID", "count"),
        Units_Sold=("Quantity", "sum"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount_Percentage", "mean")
    ).reset_index()
    cat_summary["Profit_Margin_%"] = (cat_summary["Profit"] / cat_summary["Revenue"] * 100).round(2)
    cat_summary["Avg_Discount_%"] = (cat_summary["Avg_Discount"] * 100).round(2)
    
    st.dataframe(
        cat_summary.sort_values("Revenue", ascending=False).style.format({
            "Revenue": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Profit_Margin_%": "{:.2f}%",
            "Avg_Discount_%": "{:.2f}%",
            "Units_Sold": "{:,}",
            "Orders": "{:,}"
        }),
        use_container_width=True
    )
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown('<div class="section-title">Top 10 Products by Revenue</div>', unsafe_allow_html=True)
        top_prods = filtered_df.groupby(["Product_Name", "Product_Category"]).agg(
            Revenue=("Sales_Amount", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Revenue", ascending=False).head(10)
        
        if HAS_PLOTLY:
            fig_top_p = px.bar(
                top_prods, x="Revenue", y="Product_Name", orientation='h',
                color="Product_Category",
                labels={"Revenue": "Revenue ($)", "Product_Name": "Product"}
            )
            fig_top_p.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
            st.plotly_chart(fig_top_p, use_container_width=True)
        else:
            st.dataframe(top_prods)
            
    with col_p2:
        st.markdown('<div class="section-title">Bottom 5 Products by Profit (Margin Risk)</div>', unsafe_allow_html=True)
        bot_prods = filtered_df.groupby(["Product_Name", "Product_Category"]).agg(
            Revenue=("Sales_Amount", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Profit", ascending=True).head(5)
        bot_prods["Margin_%"] = (bot_prods["Profit"] / bot_prods["Revenue"] * 100).round(2)
        
        st.dataframe(
            bot_prods.style.format({
                "Revenue": "${:,.2f}",
                "Profit": "${:,.2f}",
                "Margin_%": "{:.2f}%"
            }),
            use_container_width=True
        )
        
        st.markdown("""
        > **Data Alert**: Bottom products with aggressive discounts erode contribution margin. Rebalance promotional thresholds.
        """)

    st.markdown('<div class="section-title">Discount Band Impact on Profitability</div>', unsafe_allow_html=True)
    disc_analysis = filtered_df.groupby("Discount_Band").agg(
        Orders=("Order_ID", "count"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    disc_analysis["Profit_Margin_%"] = (disc_analysis["Profit"] / disc_analysis["Revenue"] * 100).round(2)
    
    if HAS_PLOTLY:
        fig_disc = px.bar(
            disc_analysis, x="Discount_Band", y="Profit_Margin_%",
            color="Profit_Margin_%", color_continuous_scale="RdYlGn",
            text="Profit_Margin_%", title="Realized Profit Margin % Across Discount Bands"
        )
        fig_disc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_disc.update_layout(template="plotly_white", yaxis=dict(range=[0, max(disc_analysis["Profit_Margin_%"])*1.2]))
        st.plotly_chart(fig_disc, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: CUSTOMER INSIGHTS
# -------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-title">Customer Segmentation & Value Distribution</div>', unsafe_allow_html=True)
    
    cust_agg = filtered_df.groupby("Customer_ID").agg(
        Total_Orders=("Order_ID", "count"),
        Total_Revenue=("Sales_Amount", "sum"),
        Total_Profit=("Profit", "sum"),
        Customer_Segment=("Customer_Segment", "first"),
        Location=("Customer_Location", "first"),
        Region=("Region", "first")
    ).reset_index()
    
    c_seg1, c_seg2 = st.columns(2)
    with c_seg1:
        seg_counts = cust_agg["Customer_Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]
        if HAS_PLOTLY:
            fig_pie1 = px.pie(
                seg_counts, names="Segment", values="Count",
                title="Customer Count Distribution", hole=0.4,
                color="Segment", color_discrete_map={"High Value": "#10B981", "Medium Value": "#3B82F6", "Low Value": "#F59E0B"}
            )
            st.plotly_chart(fig_pie1, use_container_width=True)
            
    with c_seg2:
        seg_rev = cust_agg.groupby("Customer_Segment")["Total_Revenue"].sum().reset_index()
        if HAS_PLOTLY:
            fig_pie2 = px.pie(
                seg_rev, names="Customer_Segment", values="Total_Revenue",
                title="Revenue Contribution by Customer Segment", hole=0.4,
                color="Customer_Segment", color_discrete_map={"High Value": "#10B981", "Medium Value": "#3B82F6", "Low Value": "#F59E0B"}
            )
            st.plotly_chart(fig_pie2, use_container_width=True)
            
    st.markdown('<div class="section-title">Repeat vs. One-Time Customer Analysis</div>', unsafe_allow_html=True)
    cust_agg["Customer_Type"] = cust_agg["Total_Orders"].apply(lambda x: "Repeat Buyer (>1 Order)" if x > 1 else "One-Time Buyer (1 Order)")
    repeat_summary = cust_agg.groupby("Customer_Type").agg(
        Customer_Count=("Customer_ID", "count"),
        Total_Revenue=("Total_Revenue", "sum"),
        Total_Profit=("Total_Profit", "sum"),
        Avg_Orders_Per_Cust=("Total_Orders", "mean")
    ).reset_index()
    repeat_summary["Revenue_Share_%"] = (repeat_summary["Total_Revenue"] / repeat_summary["Total_Revenue"].sum() * 100).round(2)
    
    st.dataframe(
        repeat_summary.style.format({
            "Total_Revenue": "${:,.2f}",
            "Total_Profit": "${:,.2f}",
            "Revenue_Share_%": "{:.2f}%",
            "Avg_Orders_Per_Cust": "{:.1f}",
            "Customer_Count": "{:,}"
        }),
        use_container_width=True
    )
    
    st.markdown('<div class="section-title">Top 10 High-Value VIP Customers</div>', unsafe_allow_html=True)
    top_vip = cust_agg.sort_values("Total_Revenue", ascending=False).head(10)
    top_vip["Profit_Margin_%"] = (top_vip["Total_Profit"] / top_vip["Total_Revenue"] * 100).round(2)
    st.dataframe(
        top_vip[["Customer_ID", "Location", "Region", "Customer_Segment", "Total_Orders", "Total_Revenue", "Total_Profit", "Profit_Margin_%"]].style.format({
            "Total_Revenue": "${:,.2f}",
            "Total_Profit": "${:,.2f}",
            "Profit_Margin_%": "{:.2f}%",
            "Total_Orders": "{:,}"
        }),
        use_container_width=True
    )

# -------------------------------------------------------------
# TAB 4: REGIONAL PERFORMANCE
# -------------------------------------------------------------
with tab4:
    st.markdown('<div class="section-title">Regional Sales & Margin Breakdown</div>', unsafe_allow_html=True)
    
    reg_summary = filtered_df.groupby("Region").agg(
        Orders=("Order_ID", "count"),
        Customers=("Customer_ID", "nunique"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    reg_summary["Profit_Margin_%"] = (reg_summary["Profit"] / reg_summary["Revenue"] * 100).round(2)
    reg_summary["Revenue_Share_%"] = (reg_summary["Revenue"] / reg_summary["Revenue"].sum() * 100).round(2)
    
    rc1, rc2 = st.columns(2)
    with rc1:
        if HAS_PLOTLY:
            fig_reg_rev = px.bar(
                reg_summary.sort_values("Revenue", ascending=False),
                x="Region", y="Revenue", color="Profit_Margin_%",
                labels={"Revenue": "Revenue ($)"},
                title="Regional Revenue & Realized Profit Margin",
                color_continuous_scale="Blues"
            )
            fig_reg_rev.update_layout(template="plotly_white")
            st.plotly_chart(fig_reg_rev, use_container_width=True)
    with rc2:
        if HAS_PLOTLY:
            fig_reg_prof = px.pie(
                reg_summary, names="Region", values="Profit",
                title="Regional Profit Distribution", hole=0.35,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig_reg_prof, use_container_width=True)
            
    st.markdown('<div class="section-title">Top 10 Performing Cities by Revenue</div>', unsafe_allow_html=True)
    city_perf = filtered_df.groupby(["Customer_Location", "Region"]).agg(
        Orders=("Order_ID", "count"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("Revenue", ascending=False).head(10)
    city_perf["Profit_Margin_%"] = (city_perf["Profit"] / city_perf["Revenue"] * 100).round(2)
    
    st.dataframe(
        city_perf.style.format({
            "Revenue": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Profit_Margin_%": "{:.2f}%",
            "Orders": "{:,}"
        }),
        use_container_width=True
    )

# -------------------------------------------------------------
# TAB 5: BUSINESS INSIGHTS & SCENARIO TARGET
# -------------------------------------------------------------
with tab5:
    st.markdown('<div class="section-title">Automated Data-Driven Business Insights</div>', unsafe_allow_html=True)
    
    # 1. Category performance
    best_cat = cat_summary.sort_values("Revenue", ascending=False).iloc[0]
    best_cat_rev_pct = (best_cat["Revenue"] / tot_rev) * 100
    
    # Lowest margin category
    lowest_margin_cat = cat_summary.sort_values("Profit_Margin_%", ascending=True).iloc[0]
    
    # Regional strength
    best_reg = reg_summary.sort_values("Revenue", ascending=False).iloc[0]
    worst_reg = reg_summary.sort_values("Revenue", ascending=True).iloc[0]
    
    # Top 10% customers
    cust_sorted = cust_agg.sort_values("Total_Revenue", ascending=False)
    top_10_pct_count = max(1, int(len(cust_sorted) * 0.10))
    top_10_pct_rev = cust_sorted.head(top_10_pct_count)["Total_Revenue"].sum()
    top_10_pct_rev_share = (top_10_pct_rev / tot_rev) * 100 if tot_rev > 0 else 0
    
    # Pareto 80% categories
    pareto_calc = cat_summary.sort_values("Profit", ascending=False).copy()
    pareto_calc["Cum_Pct"] = (pareto_calc["Profit"].cumsum() / pareto_calc["Profit"].sum()) * 100
    cats_for_80 = pareto_calc[pareto_calc["Cum_Pct"] <= 85]["Product_Category"].tolist()
    
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">1. Category Performance & Revenue Concentration</div>
        <div class="insight-body">
            <b>Finding:</b> <code>{best_cat['Product_Category']}</code> is the top revenue-generating category.<br>
            <b>Evidence:</b> Generated <b>${best_cat['Revenue']:,.2f}</b> ({best_cat_rev_pct:.1f}% of total sales) with a realized profit margin of <b>{best_cat['Profit_Margin_%']:.1f}%</b>.<br>
            <b>Business Impact:</b> Primary revenue driver of the business; maintaining catalog availability and customer satisfaction here is critical.<br>
            <b>Recommendation:</b> Protect high-margin inventory while bundling accessories to expand basket sizes.
        </div>
    </div>
    
    <div class="insight-box">
        <div class="insight-title">2. Profit Margin Leakage in Low-Margin Categories</div>
        <div class="insight-body">
            <b>Finding:</b> <code>{lowest_margin_cat['Product_Category']}</code> yields the lowest profit margin across the catalog.<br>
            <b>Evidence:</b> Profit margin is <b>{lowest_margin_cat['Profit_Margin_%']:.1f}%</b> compared to the catalog average of <b>{prof_margin:.1f}%</b>, driven by higher promotional discounts.<br>
            <b>Business Impact:</b> Generates gross sales volume but absorbs operational fulfillment costs with weak bottom-line return.<br>
            <b>Recommendation:</b> Re-evaluate supplier procurement terms, cap discount promotions at 10%, and introduce higher-margin private label SKUs.
        </div>
    </div>
    
    <div class="insight-box">
        <div class="insight-title">3. Customer Spending Concentration (80/20 Dynamic)</div>
        <div class="insight-body">
            <b>Finding:</b> Top 10% high-value customers generate an outsized proportion of total business revenue.<br>
            <b>Evidence:</b> <b>{top_10_pct_count}</b> customers account for <b>${top_10_pct_rev:,.2f}</b> (<b>{top_10_pct_rev_share:.1f}%</b> of total revenue).<br>
            <b>Business Impact:</b> High vulnerability to customer churn; loss of a small VIP cohort severely impacts quarterly revenue.<br>
            <b>Recommendation:</b> Implement a VIP loyalty tier, dedicated customer support, and tailored early-access product promotions to secure repeat lifetime value.
        </div>
    </div>
    
    <div class="insight-box">
        <div class="insight-title">4. Regional Growth Disparity</div>
        <div class="insight-body">
            <b>Finding:</b> <code>{best_reg['Region']}</code> region leads in overall sales volume, while <code>{worst_reg['Region']}</code> lags significantly.<br>
            <b>Evidence:</b> <code>{best_reg['Region']}</code> produced <b>${best_reg['Revenue']:,.2f}</b> ({best_reg['Revenue_Share_%']:.1f}%), while <code>{worst_reg['Region']}</code> contributed only <b>${worst_reg['Revenue']:,.2f}</b> ({worst_reg['Revenue_Share_%']:.1f}%).<br>
            <b>Business Impact:</b> Under-penetration in lower volume territories represents an untapped geographic expansion opportunity.<br>
            <b>Recommendation:</b> Reallocate digital marketing spend toward lagging metropolitan zones and optimize local delivery logistics.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # PROFIT MARGIN TARGET ANALYSIS (+15% Target Scenario Simulator)
    # -------------------------------------------------------------
    st.markdown('<div class="section-title">🎯 Profit Margin Target & Scenario Simulation</div>', unsafe_allow_html=True)
    st.markdown("""
    **Business Objective:** Identify data-driven strategic levers to work toward improving overall profit margin by **15% relative** (e.g., from current base to targeted margin).
    """)
    
    target_margin_pct = prof_margin * 1.15
    target_abs_gain = target_margin_pct - prof_margin
    
    sim_c1, sim_c2 = st.columns(2)
    with sim_c1:
        st.metric(
            label="Current Baseline Profit Margin",
            value=f"{prof_margin:.2f}%",
            delta=None
        )
    with sim_c2:
        st.metric(
            label="Target Profit Margin (+15% Relative Gain)",
            value=f"{target_margin_pct:.2f}%",
            delta=f"+{target_abs_gain:.2f}% absolute margin target",
            delta_color="normal"
        )
        
    st.markdown("#### Strategic Scenario Modeling Levers")
    st.markdown("Adjust parameters below to test feasibility under hypothetical operational optimizations:")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        sim_discount_reduction = st.slider(
            "Discount Policy Discipline (% Reduction in Average Discount Rate)",
            min_value=0.0, max_value=5.0, value=2.0, step=0.5,
            help="Simulates eliminating excessive markdowns and tightening discount rules."
        )
    with s_col2:
        sim_cost_opt = st.slider(
            "Procurement & Supply Chain Efficiency (% Reduction in Unit COGS)",
            min_value=0.0, max_value=5.0, value=2.5, step=0.5,
            help="Simulates renegotiated vendor volume rates and freight optimization."
        )
        
    # Calculate Simulated Financials
    # If discount is reduced by X percentage points, sales revenue increases:
    avg_disc_current = filtered_df["Discount_Percentage"].mean()
    effective_disc = max(0.0, avg_disc_current - (sim_discount_reduction / 100.0))
    
    sim_revenue = tot_rev * (1 + (sim_discount_reduction / 100.0) * 0.8)
    sim_cogs = (tot_rev - tot_prof) * (1 - (sim_cost_opt / 100.0))
    sim_profit = sim_revenue - sim_cogs
    sim_margin = (sim_profit / sim_revenue * 100) if sim_revenue > 0 else 0
    
    st.markdown("##### Simulated Outcome Results")
    res_c1, res_c2, res_c3 = st.columns(3)
    res_c1.metric("Simulated Revenue", f"${sim_revenue:,.0f}", f"+${sim_revenue - tot_rev:,.0f}")
    res_c2.metric("Simulated Profit", f"${sim_profit:,.0f}", f"+${sim_profit - tot_prof:,.0f}")
    res_c3.metric("Simulated Profit Margin", f"{sim_margin:.2f}%", f"{sim_margin - prof_margin:+.2f}% vs Base")
    
    if sim_margin >= target_margin_pct:
        st.success(f"✅ **Target Achieved!** Combined strategic levers achieve a {sim_margin:.2f}% profit margin, meeting and surpassing the +15% target.")
    else:
        gap = target_margin_pct - sim_margin
        st.info(f"ℹ️ **Scenario Progress:** Current scenario achieves {sim_margin:.2f}% margin (gap of {gap:.2f}% to reach target). Additional product mix shifting is recommended.")

st.sidebar.markdown("---")
st.sidebar.caption("E-Commerce Analytics Project | Antigravity AI")
