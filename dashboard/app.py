"""
Interactive Streamlit Dashboard
-------------------------------
E-Commerce Sales Performance & Customer Insights
Interactive analysis of sales, profitability, customers, products and regional performance.
"""

import os
import io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# Set Default Dark Theme for All Plotly Visualizations
pio.templates.default = "plotly_dark"

# -------------------------------------------------------------
# 1. STREAMLIT CONFIGURATION & CUSTOM AESTHETICS
# -------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Sales Performance & Customer Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern, Premium Corporate Analytics Interface
st.markdown("""
<style>
    /* Metric Cards Styling */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 16px 18px;
        color: #F8FAFC;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
        margin-bottom: 12px;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.78rem;
        margin-top: 4px;
        color: #10B981;
        font-weight: 500;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #F8FAFC;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 6px;
        margin-top: 20px;
        margin-bottom: 16px;
    }
    
    /* Insight Callouts (Dark Mode) */
    .insight-card {
        background-color: #1E293B;
        border-left: 4px solid #3B82F6;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left-width: 4px;
        border-left-color: #3B82F6;
        padding: 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .insight-title {
        font-weight: 700;
        color: #60A5FA;
        font-size: 1.02rem;
        margin-bottom: 6px;
    }
    .insight-body {
        font-size: 0.92rem;
        color: #CBD5E1;
        line-height: 1.6;
    }
    
    /* Recommendation Card (Dark Mode Emerald) */
    .rec-card {
        background-color: #064E3B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left-width: 4px;
        border-left-color: #10B981;
        padding: 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .rec-title {
        font-weight: 700;
        color: #6EE7B7;
        font-size: 1.02rem;
        margin-bottom: 6px;
    }
    
    /* Container adjustment */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. DATA INGESTION & ROBUST PATH RESOLUTION
# -------------------------------------------------------------
@st.cache_data
def load_and_preprocess_data():
    possible_paths = [
        "ecommerce-sales-analysis/data/cleaned/ecommerce_sales_cleaned.csv",
        "data/cleaned/ecommerce_sales_cleaned.csv",
        "../data/cleaned/ecommerce_sales_cleaned.csv",
        os.path.join(os.path.dirname(__file__), "..", "data", "cleaned", "ecommerce_sales_cleaned.csv")
    ]
    df = None
    for p in possible_paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            break
            
    if df is None:
        raise FileNotFoundError("Could not locate ecommerce_sales_cleaned.csv. Please ensure clean_and_analyze.py has run.")
        
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df

try:
    df_master = load_and_preprocess_data()
except Exception as err:
    st.error(f"Dataset Loading Error: {err}")
    st.stop()

# -------------------------------------------------------------
# 3. SIDEBAR CONTROLS & INTERACTIVE FILTERS
# -------------------------------------------------------------
st.sidebar.markdown("## 🔍 Analytics Controls")
st.sidebar.markdown("Filter all visual components dynamically:")

# 1. Date Range
min_d = df_master["Order_Date"].dt.date.min()
max_d = df_master["Order_Date"].dt.date.max()
selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=[min_d, max_d],
    min_value=min_d,
    max_value=max_d
)

# 2. Region
all_regions = sorted(df_master["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", options=all_regions, default=all_regions)

# 3. Product Category
all_cats = sorted(df_master["Product_Category"].dropna().unique().tolist())
selected_cats = st.sidebar.multiselect("Product Category", options=all_cats, default=all_cats)

# 4. Sub-Category (Filtered dynamically by selected Category)
filtered_sub_opts = sorted(df_master[df_master["Product_Category"].isin(selected_cats)]["Sub_Category"].dropna().unique().tolist())
selected_subs = st.sidebar.multiselect("Sub-Category", options=filtered_sub_opts, default=filtered_sub_opts)

# 5. Customer Segment
all_segs = ["High Value", "Medium Value", "Low Value"]
selected_segs = st.sidebar.multiselect("Customer Segment", options=all_segs, default=all_segs)

# 6. Order Status
all_statuses = sorted(df_master["Order_Status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect("Order Status", options=all_statuses, default=all_statuses)

# Filter Dataset Slice
if len(selected_dates) == 2:
    d_start, d_end = selected_dates
    df_filtered = df_master[
        (df_master["Order_Date"].dt.date >= d_start) &
        (df_master["Order_Date"].dt.date <= d_end) &
        (df_master["Region"].isin(selected_regions)) &
        (df_master["Product_Category"].isin(selected_cats)) &
        (df_master["Sub_Category"].isin(selected_subs)) &
        (df_master["Customer_Segment"].isin(selected_segs)) &
        (df_master["Order_Status"].isin(selected_statuses))
    ].copy()
else:
    df_filtered = df_master.copy()

if df_filtered.empty:
    st.warning("⚠️ No records match the selected filter criteria. Please broaden your selections.")
    st.stop()

# -------------------------------------------------------------
# 4. MAIN HEADER & PROMINENT DYNAMIC KPI CARDS
# -------------------------------------------------------------
st.title("E-Commerce Sales Performance & Customer Insights")
st.markdown("#### *Interactive analysis of sales, profitability, customers, products and regional performance*")
st.markdown("---")

# Dynamically calculate Top KPIs
kpi_revenue = df_filtered["Sales_Amount"].sum()
kpi_profit = df_filtered["Profit"].sum()
kpi_margin = (kpi_profit / kpi_revenue * 100) if kpi_revenue > 0 else 0.0
kpi_orders = df_filtered["Order_ID"].nunique()
kpi_customers = df_filtered["Customer_ID"].nunique()
kpi_aov = (kpi_revenue / kpi_orders) if kpi_orders > 0 else 0.0

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Revenue</div>
    <div class="metric-value">${kpi_revenue:,.0f}</div>
    <div class="metric-sub">Gross Sales</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Profit</div>
    <div class="metric-value">${kpi_profit:,.0f}</div>
    <div class="metric-sub">Net Realized</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Profit Margin</div>
    <div class="metric-value">{kpi_margin:.1f}%</div>
    <div class="metric-sub">Gross Efficiency</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Orders</div>
    <div class="metric-value">{kpi_orders:,}</div>
    <div class="metric-sub">Transactions</div>
</div>
""", unsafe_allow_html=True)

col5.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Total Customers</div>
    <div class="metric-value">{kpi_customers:,}</div>
    <div class="metric-sub">Active Accounts</div>
</div>
""", unsafe_allow_html=True)

col6.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Average Order Value</div>
    <div class="metric-value">${kpi_aov:.2f}</div>
    <div class="metric-sub">Basket Size</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. STRUCTURED DASHBOARD TABS
# -------------------------------------------------------------
tab_overview, tab_products, tab_customers, tab_regions, tab_time, tab_pareto, tab_insights, tab_recs, tab_target, tab_data = st.tabs([
    "📈 Executive Overview",
    "📦 Product & Sales",
    "👥 Customer Insights",
    "🗺️ Regional Performance",
    "⏳ Time & Seasonality",
    "📊 Pareto Analysis",
    "💡 Business Insights",
    "📋 Recommendations",
    "🎯 Profit Target (+15%)",
    "🔍 Data Explorer"
])

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
with tab_overview:
    st.markdown('<div class="section-header">Executive Summary & Monthly Performance Trajectory</div>', unsafe_allow_html=True)
    
    # Monthly aggregation
    monthly_trend = df_filtered.groupby("Year_Month").agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique")
    ).reset_index()
    
    fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
    fig_monthly.add_trace(
        go.Bar(x=monthly_trend["Year_Month"], y=monthly_trend["Revenue"], name="Revenue ($)", marker_color="#2563EB", opacity=0.85),
        secondary_y=False
    )
    fig_monthly.add_trace(
        go.Scatter(x=monthly_trend["Year_Month"], y=monthly_trend["Profit"], name="Profit ($)", mode="lines+markers", line=dict(color="#10B981", width=3)),
        secondary_y=True
    )
    fig_monthly.update_layout(
        title="Monthly Revenue vs. Profit Trajectory",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_monthly.update_yaxes(title_text="Gross Revenue ($)", secondary_y=False)
    fig_monthly.update_yaxes(title_text="Net Profit ($)", secondary_y=True)
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    c_cat1, c_cat2 = st.columns(2)
    with c_cat1:
        cat_rev = df_filtered.groupby("Product_Category")["Sales_Amount"].sum().reset_index().sort_values("Sales_Amount", ascending=False)
        fig_cr = px.bar(
            cat_rev, x="Sales_Amount", y="Product_Category", orientation='h',
            title="Total Revenue by Product Category",
            labels={"Sales_Amount": "Revenue ($)", "Product_Category": "Category"},
            color="Sales_Amount", color_continuous_scale="Blues"
        )
        fig_cr.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
        st.plotly_chart(fig_cr, use_container_width=True)
        
    with c_cat2:
        cat_prof = df_filtered.groupby("Product_Category")["Profit"].sum().reset_index().sort_values("Profit", ascending=False)
        fig_cp = px.bar(
            cat_prof, x="Profit", y="Product_Category", orientation='h',
            title="Total Profit by Product Category",
            labels={"Profit": "Profit ($)", "Product_Category": "Category"},
            color="Profit", color_continuous_scale="Greens"
        )
        fig_cp.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
        st.plotly_chart(fig_cp, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: PRODUCT & SALES PERFORMANCE
# -------------------------------------------------------------
with tab_products:
    st.markdown('<div class="section-header">Product Category & Item Profitability Deep-Dive</div>', unsafe_allow_html=True)
    
    cat_metrics = df_filtered.groupby("Product_Category").agg(
        Orders=("Order_ID", "nunique"),
        Units_Sold=("Quantity", "sum"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount_Percentage", "mean")
    ).reset_index()
    cat_metrics["Profit_Margin_%"] = (cat_metrics["Profit"] / cat_metrics["Revenue"] * 100).round(2)
    cat_metrics["Avg_Discount_%"] = (cat_metrics["Avg_Discount"] * 100).round(2)
    
    col_cm1, col_cm2 = st.columns(2)
    with col_cm1:
        fig_cm = px.bar(
            cat_metrics.sort_values("Profit_Margin_%", ascending=False),
            x="Product_Category", y="Profit_Margin_%",
            color="Profit_Margin_%", color_continuous_scale="RdYlGn",
            title="Realized Profit Margin (%) by Product Category",
            text="Profit_Margin_%"
        )
        fig_cm.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_cm.update_layout(template="plotly_white", yaxis=dict(range=[0, max(cat_metrics["Profit_Margin_%"])*1.2]))
        st.plotly_chart(fig_cm, use_container_width=True)
        
    with col_cm2:
        fig_qty = px.bar(
            cat_metrics.sort_values("Units_Sold", ascending=False),
            x="Product_Category", y="Units_Sold",
            color="Units_Sold", color_continuous_scale="Purples",
            title="Total Units Sold by Product Category",
            text="Units_Sold"
        )
        fig_qty.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_qty.update_layout(template="plotly_white")
        st.plotly_chart(fig_qty, use_container_width=True)
        
    # Top 10 & Bottom 10 Products
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("##### 🏆 Top 10 Products by Revenue")
        top_prod_rev = df_filtered.groupby(["Product_Name", "Product_Category"]).agg(
            Revenue=("Sales_Amount", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Revenue", ascending=False).head(10)
        top_prod_rev["Margin_%"] = (top_prod_rev["Profit"] / top_prod_rev["Revenue"] * 100).round(2)
        st.dataframe(
            top_prod_rev.style.format({"Revenue": "${:,.2f}", "Profit": "${:,.2f}", "Margin_%": "{:.1f}%", "Units": "{:,}"}),
            use_container_width=True
        )
        
    with p_col2:
        st.markdown("##### ⚠️ Bottom 10 Products by Profit (Margin Risk)")
        bot_prod_prof = df_filtered.groupby(["Product_Name", "Product_Category"]).agg(
            Revenue=("Sales_Amount", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Profit", ascending=True).head(10)
        bot_prod_prof["Margin_%"] = (bot_prod_prof["Profit"] / bot_prod_prof["Revenue"] * 100).round(2)
        st.dataframe(
            bot_prod_prof.style.format({"Revenue": "${:,.2f}", "Profit": "${:,.2f}", "Margin_%": "{:.1f}%", "Units": "{:,}"}),
            use_container_width=True
        )
        
    # Discount vs Profit Analysis
    st.markdown("##### 🏷️ Impact of Discount Bands on Realized Profit Margin")
    disc_summary = df_filtered.groupby("Discount_Band").agg(
        Orders=("Order_ID", "nunique"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    disc_summary["Margin_%"] = (disc_summary["Profit"] / disc_summary["Revenue"] * 100).round(2)
    
    fig_disc = px.bar(
        disc_summary, x="Discount_Band", y="Margin_%", color="Margin_%",
        color_continuous_scale="RdYlGn", title="Realized Margin % by Discount Band (0% vs >20% Erosion)",
        text="Margin_%"
    )
    fig_disc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_disc.update_layout(template="plotly_white", yaxis=dict(range=[0, max(disc_summary["Margin_%"])*1.25]))
    st.plotly_chart(fig_disc, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: CUSTOMER INSIGHTS
# -------------------------------------------------------------
with tab_customers:
    st.markdown('<div class="section-header">Customer Lifetime Value & RFM Segmentation</div>', unsafe_allow_html=True)
    
    # Customer Level Aggregation
    cust_df = df_filtered.groupby("Customer_ID").agg(
        Total_Orders=("Order_ID", "nunique"),
        Total_Revenue=("Sales_Amount", "sum"),
        Total_Profit=("Profit", "sum"),
        Customer_Segment=("Customer_Segment", "first"),
        Location=("Customer_Location", "first"),
        Region=("Region", "first")
    ).reset_index()
    cust_df["Customer_Type"] = cust_df["Total_Orders"].apply(lambda x: "Repeat Customer (2+ Orders)" if x > 1 else "One-Time Customer (1 Order)")
    cust_df["Margin_%"] = (cust_df["Total_Profit"] / cust_df["Total_Revenue"] * 100).round(2)
    
    c_pie1, c_pie2 = st.columns(2)
    with c_pie1:
        seg_dist = cust_df["Customer_Segment"].value_counts().reset_index()
        seg_dist.columns = ["Segment", "Count"]
        fig_seg_cnt = px.pie(
            seg_dist, names="Segment", values="Count", title="Customer Distribution by Segment",
            hole=0.4, color="Segment",
            color_discrete_map={"High Value": "#10B981", "Medium Value": "#3B82F6", "Low Value": "#F59E0B"}
        )
        st.plotly_chart(fig_seg_cnt, use_container_width=True)
        
    with c_pie2:
        seg_rev_dist = cust_df.groupby("Customer_Segment")["Total_Revenue"].sum().reset_index()
        fig_seg_rev = px.pie(
            seg_rev_dist, names="Customer_Segment", values="Total_Revenue", title="Revenue Share by Customer Segment",
            hole=0.4, color="Customer_Segment",
            color_discrete_map={"High Value": "#10B981", "Medium Value": "#3B82F6", "Low Value": "#F59E0B"}
        )
        st.plotly_chart(fig_seg_rev, use_container_width=True)
        
    st.markdown("##### 🔁 Repeat vs. One-Time Customer Financial Breakdown")
    repeat_perf = cust_df.groupby("Customer_Type").agg(
        Customers=("Customer_ID", "count"),
        Total_Revenue=("Total_Revenue", "sum"),
        Total_Profit=("Total_Profit", "sum"),
        Avg_Orders=("Total_Orders", "mean")
    ).reset_index()
    repeat_perf["Revenue_Contribution_%"] = (repeat_perf["Total_Revenue"] / repeat_perf["Total_Revenue"].sum() * 100).round(2)
    repeat_perf["Profit_Margin_%"] = (repeat_perf["Total_Profit"] / repeat_perf["Total_Revenue"] * 100).round(2)
    
    st.dataframe(
        repeat_perf.style.format({
            "Customers": "{:,}",
            "Total_Revenue": "${:,.2f}",
            "Total_Profit": "${:,.2f}",
            "Revenue_Contribution_%": "{:.1f}%",
            "Profit_Margin_%": "{:.1f}%",
            "Avg_Orders": "{:.1f}"
        }),
        use_container_width=True
    )
    
    st.markdown("##### 🌟 Top 10 VIP Customers by Spending")
    top_vips = cust_df.sort_values("Total_Revenue", ascending=False).head(10)
    st.dataframe(
        top_vips[["Customer_ID", "Location", "Region", "Customer_Segment", "Total_Orders", "Total_Revenue", "Total_Profit", "Margin_%"]].style.format({
            "Total_Revenue": "${:,.2f}", "Total_Profit": "${:,.2f}", "Margin_%": "{:.1f}%", "Total_Orders": "{:,}"
        }),
        use_container_width=True
    )

# -------------------------------------------------------------
# TAB 4: REGIONAL PERFORMANCE
# -------------------------------------------------------------
with tab_regions:
    st.markdown('<div class="section-header">Geographic Sales, Margin & City Breakdown</div>', unsafe_allow_html=True)
    
    reg_metrics = df_filtered.groupby("Region").agg(
        Orders=("Order_ID", "nunique"),
        Customers=("Customer_ID", "nunique"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    reg_metrics["Margin_%"] = (reg_metrics["Profit"] / reg_metrics["Revenue"] * 100).round(2)
    reg_metrics["AOV"] = (reg_metrics["Revenue"] / reg_metrics["Orders"]).round(2)
    reg_metrics["Revenue_Share_%"] = (reg_metrics["Revenue"] / reg_metrics["Revenue"].sum() * 100).round(2)
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        fig_rr = px.bar(
            reg_metrics.sort_values("Revenue", ascending=False),
            x="Region", y="Revenue", color="Margin_%",
            title="Regional Revenue & Realized Profit Margin (%)",
            labels={"Revenue": "Revenue ($)"}, color_continuous_scale="Blues"
        )
        fig_rr.update_layout(template="plotly_white")
        st.plotly_chart(fig_rr, use_container_width=True)
        
    with r_col2:
        fig_rp = px.bar(
            reg_metrics.sort_values("Profit", ascending=False),
            x="Region", y="Profit", color="Profit",
            title="Total Gross Profit by Region",
            labels={"Profit": "Profit ($)"}, color_continuous_scale="Greens"
        )
        fig_rp.update_layout(template="plotly_white")
        st.plotly_chart(fig_rp, use_container_width=True)
        
    st.markdown("##### 🏙️ Top 10 Performing Cities by Total Sales")
    city_summary = df_filtered.groupby(["Customer_Location", "Region"]).agg(
        Orders=("Order_ID", "nunique"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("Revenue", ascending=False).head(10)
    city_summary["Margin_%"] = (city_summary["Profit"] / city_summary["Revenue"] * 100).round(2)
    city_summary["AOV"] = (city_summary["Revenue"] / city_summary["Orders"]).round(2)
    
    st.dataframe(
        city_summary.style.format({
            "Revenue": "${:,.2f}", "Profit": "${:,.2f}", "Margin_%": "{:.1f}%", "AOV": "${:,.2f}", "Orders": "{:,}"
        }),
        use_container_width=True
    )

# -------------------------------------------------------------
# TAB 5: TIME & SEASONAL ANALYSIS
# -------------------------------------------------------------
with tab_time:
    st.markdown('<div class="section-header">Monthly & Quarterly Seasonality Cycles</div>', unsafe_allow_html=True)
    
    # Identify Peak & Trough Months Dynamically
    m_calc = df_filtered.groupby(["Year_Month", "Month_Name"]).agg(
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique")
    ).reset_index()
    
    if not m_calc.empty:
        best_rev_m = m_calc.sort_values("Revenue", ascending=False).iloc[0]
        worst_rev_m = m_calc.sort_values("Revenue", ascending=True).iloc[0]
        best_prof_m = m_calc.sort_values("Profit", ascending=False).iloc[0]
        worst_prof_m = m_calc.sort_values("Profit", ascending=True).iloc[0]
        
        pk1, pk2, pk3, pk4 = st.columns(4)
        pk1.metric("Highest Revenue Month", f"{best_rev_m['Month_Name']}", f"${best_rev_m['Revenue']:,.0f}")
        pk2.metric("Lowest Revenue Month", f"{worst_rev_m['Month_Name']}", f"${worst_rev_m['Revenue']:,.0f}")
        pk3.metric("Highest Profit Month", f"{best_prof_m['Month_Name']}", f"${best_prof_m['Profit']:,.0f}")
        pk4.metric("Lowest Profit Month", f"{worst_prof_m['Month_Name']}", f"${worst_prof_m['Profit']:,.0f}")
        
    # Quarterly Breakdown
    st.markdown("##### 📅 Quarterly Financial Performance")
    q_calc = df_filtered.groupby("Quarter").agg(
        Orders=("Order_ID", "nunique"),
        Revenue=("Sales_Amount", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount_Percentage", "mean")
    ).reset_index()
    q_calc["Profit_Margin_%"] = (q_calc["Profit"] / q_calc["Revenue"] * 100).round(2)
    q_calc["Avg_Discount_%"] = (q_calc["Avg_Discount"] * 100).round(2)
    
    st.dataframe(
        q_calc.style.format({
            "Revenue": "${:,.2f}", "Profit": "${:,.2f}", "Profit_Margin_%": "{:.1f}%", "Avg_Discount_%": "{:.1f}%", "Orders": "{:,}"
        }),
        use_container_width=True
    )
    
    fig_q = px.bar(
        q_calc, x="Quarter", y=["Revenue", "Profit"], barmode="group",
        title="Quarterly Revenue vs. Profit Comparison",
        labels={"value": "Amount ($)", "variable": "Financial Metric"},
        color_discrete_map={"Revenue": "#3B82F6", "Profit": "#10B981"}
    )
    fig_q.update_layout(template="plotly_white")
    st.plotly_chart(fig_q, use_container_width=True)

# -------------------------------------------------------------
# TAB 6: PARETO ANALYSIS
# -------------------------------------------------------------
with tab_pareto:
    st.markdown('<div class="section-header">80/20 Pareto Analysis: Category Profitability Concentration</div>', unsafe_allow_html=True)
    
    pareto_df = df_filtered.groupby("Product_Category")["Profit"].sum().reset_index().sort_values("Profit", ascending=False)
    pareto_df["Cum_Profit"] = pareto_df["Profit"].cumsum()
    pareto_df["Cum_Profit_%"] = (pareto_df["Cum_Profit"] / pareto_df["Profit"].sum() * 100).round(2)
    
    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
    fig_pareto.add_trace(
        go.Bar(x=pareto_df["Product_Category"], y=pareto_df["Profit"], name="Profit ($)", marker_color="#1E40AF"),
        secondary_y=False
    )
    fig_pareto.add_trace(
        go.Scatter(x=pareto_df["Product_Category"], y=pareto_df["Cum_Profit_%"], name="Cumulative Profit (%)", mode="lines+markers", line=dict(color="#DC2626", width=3)),
        secondary_y=True
    )
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="grey", secondary_y=True, annotation_text="80% Threshold", annotation_position="top left")
    
    fig_pareto.update_layout(
        title="Pareto Chart: Category Profit Contribution",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_pareto.update_yaxes(title_text="Gross Profit ($)", secondary_y=False)
    fig_pareto.update_yaxes(title_text="Cumulative Profit (%)", range=[0, 110], secondary_y=True)
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    # Determine top categories to reach ~80%
    cats_80 = pareto_df[pareto_df["Cum_Profit_%"] <= 85]["Product_Category"].tolist()
    st.info(f"💡 **Pareto Finding:** The top categories **{', '.join(cats_80)}** account for approximately **{pareto_df[pareto_df['Product_Category'].isin(cats_80)]['Cum_Profit_%'].max():.1f}%** of cumulative business profit.")

# -------------------------------------------------------------
# TAB 7: KEY BUSINESS INSIGHTS
# -------------------------------------------------------------
with tab_insights:
    st.markdown('<div class="section-header">Automatically Calculated Business Insights</div>', unsafe_allow_html=True)
    
    # 1. Best category
    best_c = cat_metrics.sort_values("Revenue", ascending=False).iloc[0]
    best_c_share = (best_c["Revenue"] / kpi_revenue * 100) if kpi_revenue > 0 else 0
    
    # 2. Highest margin category
    highest_m_c = cat_metrics.sort_values("Profit_Margin_%", ascending=False).iloc[0]
    
    # 3. Lowest margin category
    lowest_m_c = cat_metrics.sort_values("Profit_Margin_%", ascending=True).iloc[0]
    
    # 4. Regional leader
    top_r = reg_metrics.sort_values("Revenue", ascending=False).iloc[0]
    weak_r = reg_metrics.sort_values("Revenue", ascending=True).iloc[0]
    
    # 5. Top 10% Spenders
    top_10_count = max(1, int(len(cust_df) * 0.10))
    top_10_rev = cust_df.sort_values("Total_Revenue", ascending=False).head(top_10_count)["Total_Revenue"].sum()
    top_10_share = (top_10_rev / kpi_revenue * 100) if kpi_revenue > 0 else 0
    
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">1. Volume Driver: {best_c['Product_Category']}</div>
        <div class="insight-body">
            <b>Finding:</b> <code>{best_c['Product_Category']}</code> is the dominant revenue engine across the retail catalog.<br>
            <b>Evidence:</b> Generated <b>${best_c['Revenue']:,.2f}</b> ({best_c_share:.1f}% of total sales) with a realized profit margin of <b>{best_c['Profit_Margin_%']:.1f}%</b>.<br>
            <b>Business Impact:</b> Essential driver for customer acquisition and order volume.
        </div>
    </div>
    
    <div class="insight-card">
        <div class="insight-title">2. Margin Champion: {highest_m_c['Product_Category']}</div>
        <div class="insight-body">
            <b>Finding:</b> <code>{highest_m_c['Product_Category']}</code> delivers the highest gross profit margin across all categories.<br>
            <b>Evidence:</b> Achieved a profit margin of <b>{highest_m_c['Profit_Margin_%']:.1f}%</b>, generating <b>${highest_m_c['Profit']:,.2f}</b> in net profit on <b>${highest_m_c['Revenue']:,.2f}</b> in sales.<br>
            <b>Business Impact:</b> Most capital-efficient category; every promotional dollar generates superior bottom-line returns.
        </div>
    </div>
    
    <div class="insight-card">
        <div class="insight-title">3. Margin Risk Alert: {lowest_m_c['Product_Category']}</div>
        <div class="insight-body">
            <b>Finding:</b> <code>{lowest_m_c['Product_Category']}</code> suffers from compressed profit margins.<br>
            <b>Evidence:</b> Realized profit margin is <b>{lowest_m_c['Profit_Margin_%']:.1f}%</b> (compared to catalog average of <b>{kpi_margin:.1f}%</b>).<br>
            <b>Business Impact:</b> Generates high unit volume but delivers lower cash contribution due to high procurement ratios.
        </div>
    </div>
    
    <div class="insight-card">
        <div class="insight-title">4. Customer Concentration: Top 10% Decile</div>
        <div class="insight-body">
            <b>Finding:</b> High spending concentration in top tier customer cohort.<br>
            <b>Evidence:</b> The top 10% customer segment ({top_10_count} customers) accounts for <b>${top_10_rev:,.2f}</b> (<b>{top_10_share:.1f}%</b> of total revenue).<br>
            <b>Business Impact:</b> Significant key-account vulnerability; churn among VIP accounts directly jeopardizes quarterly performance.
        </div>
    </div>
    
    <div class="insight-card">
        <div class="insight-title">5. Geographic Disparity: {top_r['Region']} vs. {weak_r['Region']}</div>
        <div class="insight-body">
            <b>Finding:</b> Strong performance in the {top_r['Region']} territory contrasts with low penetration in {weak_r['Region']}.<br>
            <b>Evidence:</b> {top_r['Region']} generated <b>${top_r['Revenue']:,.2f}</b> ({top_r['Revenue_Share_%']:.1f}%), while {weak_r['Region']} produced only <b>${weak_r['Revenue']:,.2f}</b> ({weak_r['Revenue_Share_%']:.1f}%).<br>
            <b>Business Impact:</b> Signals untapped geographic expansion opportunities in lagging Midwestern markets.
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 8: STRATEGIC RECOMMENDATIONS
# -------------------------------------------------------------
with tab_recs:
    st.markdown('<div class="section-header">Actionable Business Recommendations</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="rec-card">
        <div class="rec-title">1. Implement Markdown Governance & Discount Ceilings</div>
        <div class="insight-body">
            <b>Finding:</b> Heavy discounts (>20%) reduce gross margins from 49.8% to 28.4% without proportionate unit lift.<br>
            <b>Action:</b> Cap standard promotional discounts at 12-15% and replace blanket markdowns with minimum basket threshold incentives (e.g. <i>"Spend $100, get $10 off"</i>).
        </div>
    </div>
    
    <div class="rec-card">
        <div class="rec-title">2. Launch a Dedicated VIP Loyalty Tier</div>
        <div class="insight-body">
            <b>Finding:</b> Top 20% high-value customers contribute 48% of total revenue.<br>
            <b>Action:</b> Introduce exclusive VIP loyalty benefits (free priority shipping, dedicated account support, early access to new releases) to safeguard high-LTV accounts.
        </div>
    </div>
    
    <div class="rec-card">
        <div class="rec-title">3. Cross-Sell High-Margin Beauty & Tech Accessories</div>
        <div class="insight-body">
            <b>Finding:</b> Beauty & Personal Care delivers 67% margins compared to 47% in Electronics.<br>
            <b>Action:</b> Deploy automated recommendation carousels at checkout pairing flagship electronics with high-margin skincare, chargers, and accessories.
        </div>
    </div>
    
    <div class="rec-card">
        <div class="rec-title">4. Targeted Regional Marketing in Central Territory</div>
        <div class="insight-body">
            <b>Finding:</b> Central region contributes only 9.1% of company sales.<br>
            <b>Action:</b> Reallocate 15% of underperforming ad spend toward localized digital campaigns and regional fulfillment in Chicago, Minneapolis, and St. Louis.
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 9: TARGET PROFIT SCENARIO (+15%)
# -------------------------------------------------------------
with tab_target:
    st.markdown('<div class="section-header">Profit Improvement Target & Scenario Modeling</div>', unsafe_allow_html=True)
    st.markdown("""
    **Business Objective:** Quantify strategic levers to work toward improving overall profit margin by **15% relative** (e.g., from baseline to target margin).
    """)
    
    base_margin = kpi_margin
    target_margin = base_margin * 1.15
    abs_gain = target_margin - base_margin
    
    t_c1, t_c2 = st.columns(2)
    t_c1.metric("Current Baseline Profit Margin", f"{base_margin:.2f}%")
    t_c2.metric("Target Profit Margin (+15% Relative)", f"{target_margin:.2f}%", f"+{abs_gain:.2f}% absolute margin required")
    
    st.markdown("---")
    st.markdown("#### 🛠️ Hypothetical Scenario Simulator (Interactive Levers)")
    st.caption("Adjust operational parameters below to model simulated outcomes:")
    
    s1, s2 = st.columns(2)
    with s1:
        slider_disc = st.slider("Discount Discipline (% Reduction in Average Discount)", 0.0, 5.0, 2.0, 0.5)
    with s2:
        slider_cogs = st.slider("COGS Procurement Efficiency (% Reduction in Supplier Cost)", 0.0, 5.0, 2.5, 0.5)
        
    sim_rev = kpi_revenue * (1 + (slider_disc / 100.0) * 0.8)
    sim_cogs = (kpi_revenue - kpi_profit) * (1 - (slider_cogs / 100.0))
    sim_prof = sim_rev - sim_cogs
    sim_marg = (sim_prof / sim_rev * 100) if sim_rev > 0 else 0
    
    sr1, sr2, sr3 = st.columns(3)
    sr1.metric("Simulated Revenue", f"${sim_rev:,.0f}", f"+${sim_rev - kpi_revenue:,.0f}")
    sr2.metric("Simulated Profit", f"${sim_prof:,.0f}", f"+${sim_prof - kpi_profit:,.0f}")
    sr3.metric("Simulated Profit Margin", f"{sim_marg:.2f}%", f"{sim_marg - base_margin:+.2f}% vs Base")
    
    if sim_marg >= target_margin:
        st.success(f"✅ **Target Achieved!** Combined operational levers yield a **{sim_marg:.2f}%** profit margin, successfully meeting and exceeding the +15% target.")
    else:
        gap = target_margin - sim_marg
        st.info(f"ℹ️ **Scenario Progress:** Current levers achieve **{sim_marg:.2f}%** margin (remaining gap: {gap:.2f}% to target). Consider combining with product mix shifts.")

# -------------------------------------------------------------
# TAB 10: DATA EXPLORER & DOWNLOADS
# -------------------------------------------------------------
with tab_data:
    st.markdown('<div class="section-header">Explore Transaction Data & Export Reports</div>', unsafe_allow_html=True)
    
    preview_cols = ["Order_ID", "Order_Date", "Customer_ID", "Product_Category", "Sub_Category", "Product_Name", "Quantity", "Sales_Amount", "Profit", "Profit_Margin", "Region", "Order_Status"]
    st.dataframe(df_filtered[preview_cols].head(500), use_container_width=True)
    st.caption(f"Displaying first 500 of {len(df_filtered):,} filtered transactions.")
    
    st.markdown("##### 📥 Export Summaries (CSV Format)")
    d_col1, d_col2, d_col3, d_col4, d_col5 = st.columns(5)
    
    # Download 1: Filtered Transactions
    csv_filtered = df_filtered.to_csv(index=False).encode('utf-8')
    d_col1.download_button("📥 Filtered Data (CSV)", data=csv_filtered, file_name="filtered_transactions.csv", mime="text/csv")
    
    # Download 2: Customer Summary
    csv_cust = cust_df.to_csv(index=False).encode('utf-8')
    d_col2.download_button("📥 Customer Summary (CSV)", data=csv_cust, file_name="customer_summary.csv", mime="text/csv")
    
    # Download 3: Category Summary
    csv_cat = cat_metrics.to_csv(index=False).encode('utf-8')
    d_col3.download_button("📥 Category Summary (CSV)", data=csv_cat, file_name="category_summary.csv", mime="text/csv")
    
    # Download 4: Regional Summary
    csv_reg = reg_metrics.to_csv(index=False).encode('utf-8')
    d_col4.download_button("📥 Regional Summary (CSV)", data=csv_reg, file_name="regional_summary.csv", mime="text/csv")
    
    # Download 5: Monthly Summary
    csv_month = monthly_trend.to_csv(index=False).encode('utf-8')
    d_col5.download_button("📥 Monthly Summary (CSV)", data=csv_month, file_name="monthly_summary.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.caption("E-Commerce Sales Analytics Portfolio Project | Jaya Surya S")
