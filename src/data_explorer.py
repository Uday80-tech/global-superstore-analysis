import streamlit as st
import pandas as pd
import os
import sys

# Add project root to Python path

from src.data_loader import load_superstore_data
from src.filters import render_sidebar_branding, render_sidebar_navigation, render_global_filters
from src.components import inject_custom_css, render_kpi_card, render_section_header


def render_data_explorer_content(df: pd.DataFrame):
    """Renders Data Explorer with original design."""
    st.title("🔍 Data Explorer & Export")
    st.caption("Interactive dataset viewer, schema information, missing value audit, and filtered CSV export.")

    if df.empty:
        st.warning("⚠️ No records match the selected filter criteria.")
        return

    # Dataset Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Filtered Records", f"{len(df):,}", "Active in view", "positive", "📊")
    with c2:
        render_kpi_card("Total Columns", f"{len(df.columns)} Columns", "Cleaned schema", "neutral", "🗂️")
    with c3:
        total_missing = int(df.isnull().sum().sum())
        render_kpi_card("Missing Values", f"{total_missing:,}", "0 across active data", "positive" if total_missing == 0 else "neutral", "🧹")
    with c4:
        render_kpi_card("Date Range", f"{df['order_year'].min()} – {df['order_year'].max()}", "4 Operational Years", "neutral", "📅")

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 1. Interactive Dataset Browser
    render_section_header("📋 Interactive Dataset Browser")
    col_search, col_limit = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("🔎 Search (Product, Customer, Country, City, Order ID):", placeholder="e.g. Apple, Staples, London, California...")
    with col_limit:
        row_limit = st.selectbox("Display Limit:", [25, 50, 100, 500, 1000, "All"], index=0)

    # Column Selection
    all_cols = list(df.columns)
    default_cols = ['order_id', 'order_date', 'customer_name', 'segment', 'category', 'sub_category', 'product_name', 'sales', 'quantity', 'discount', 'profit', 'region', 'country']
    selected_cols = st.multiselect("Select Columns to Display:", options=all_cols, default=[c for c in default_cols if c in all_cols])

    # Apply search filter
    display_df = df.copy()
    if search_query:
        mask = False
        text_cols = ['product_name', 'customer_name', 'city', 'country', 'state', 'order_id', 'sub_category', 'category']
        for col in text_cols:
            if col in display_df.columns:
                mask = mask | display_df[col].astype(str).str.contains(search_query, case=False, na=False)
        display_df = display_df[mask]

    # Limit rows
    if row_limit != "All":
        view_df = display_df[selected_cols].head(int(row_limit))
    else:
        view_df = display_df[selected_cols]

    st.dataframe(view_df, use_container_width=True, hide_index=True)

    # CSV Download Button
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download Filtered Data as CSV ({len(display_df):,} records)",
        data=csv_data,
        file_name="global_superstore_filtered.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # 2. Schema Information & Data Dictionary Tabs
    render_section_header("📑 Dataset Schema & Quality Audit")
    tab_cols, tab_stats, tab_dict = st.tabs(["🏷️ Column Information & Missing Values", "📊 Summary Statistics", "📖 Data Dictionary"])

    with tab_cols:
        col_info = []
        for col in df.columns:
            null_cnt = int(df[col].isnull().sum())
            col_info.append({
                "Column Name": col,
                "Data Type": str(df[col].dtype),
                "Non-Null Count": len(df) - null_cnt,
                "Missing Values": null_cnt,
                "Missing (%)": f"{(null_cnt / len(df) * 100):.2f}%",
                "Unique Values": int(df[col].nunique())
            })
        st.dataframe(pd.DataFrame(col_info), use_container_width=True, hide_index=True)

    with tab_stats:
        num_cols = ['sales', 'profit', 'discount', 'quantity', 'profit_margin', 'shipping_cost', 'delivery_days']
        present_num = [c for c in num_cols if c in df.columns]
        if present_num:
            stats_df = df[present_num].describe().T
            st.dataframe(stats_df.style.format('{:,.2f}'), use_container_width=True)

    with tab_dict:
        dict_data = [
            {"Column": "order_id", "Description": "Unique transaction order identifier"},
            {"Column": "order_date", "Description": "Order date (2011-01-01 to 2014-12-31)"},
            {"Column": "ship_date", "Description": "Shipping / dispatch date"},
            {"Column": "delivery_days", "Description": "Turnaround duration: (ship_date - order_date) in days"},
            {"Column": "ship_mode", "Description": "Fulfillment tier: Standard Class, Second Class, First Class, Same Day"},
            {"Column": "customer_id", "Description": "Unique customer account identifier"},
            {"Column": "customer_name", "Description": "Full name of customer"},
            {"Column": "segment", "Description": "Customer group: Consumer, Corporate, Home Office"},
            {"Column": "city", "Description": "City of order origin"},
            {"Column": "state", "Description": "State or province"},
            {"Column": "country", "Description": "Country location (147 countries)"},
            {"Column": "region", "Description": "13 Operational global regions"},
            {"Column": "market", "Description": "7 Global markets (APAC, EU, US, LATAM, EMEA, Africa, Canada)"},
            {"Column": "product_id", "Description": "Unique product SKU identifier"},
            {"Column": "category", "Description": "Main department: Technology, Furniture, Office Supplies"},
            {"Column": "sub_category", "Description": "Product line (Phones, Copiers, Tables, Chairs, etc.)"},
            {"Column": "product_name", "Description": "Catalog product title"},
            {"Column": "sales", "Description": "Gross revenue transaction amount ($ USD)"},
            {"Column": "quantity", "Description": "Number of units ordered"},
            {"Column": "discount", "Description": "Discount rate applied (0.0 to 0.85)"},
            {"Column": "profit", "Description": "Net profit or loss generated ($ USD)"},
            {"Column": "shipping_cost", "Description": "Freight shipping expenditure ($ USD)"},
            {"Column": "order_priority", "Description": "Priority rating: Critical, High, Medium, Low"},
            {"Column": "profit_margin", "Description": "Profit margin percentage: (Profit / Sales) * 100"}
        ]
        st.dataframe(pd.DataFrame(dict_data), use_container_width=True, hide_index=True)
