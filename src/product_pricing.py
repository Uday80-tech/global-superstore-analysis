import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add project root to Python path

from src.data_loader import load_superstore_data
from src.filters import render_sidebar_branding, render_sidebar_navigation, render_global_filters
from src.metrics import (
    calculate_total_sales,
    calculate_total_profit,
    calculate_profit_margin,
    format_currency,
    format_number
)
from src.components import (
    inject_custom_css,
    render_kpi_card,
    render_section_header,
    render_warning_box,
    apply_plotly_theme,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING
)


def render_product_pricing_content(df: pd.DataFrame):
    """Renders the Product & Pricing analysis with original design."""
    st.title("📦 Product & Pricing Analysis")
    st.caption("Deep-dive evaluation of product categories, sub-category profit margins, discount impact, and top/bottom items.")

    if df.empty:
        st.warning("⚠️ No records match the selected filter criteria.")
        return

    # Calculate KPIs
    sales = calculate_total_sales(df)
    profit = calculate_total_profit(df)
    margin = calculate_profit_margin(df)
    avg_discount = float(df['discount'].mean() * 100) if 'discount' in df.columns else 0.0
    products_count = df['product_name'].nunique()
    subcats_count = df['sub_category'].nunique()

    # 1. KPI Cards Grid (6 Cards)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card("Total Sales", format_currency(sales), "Gross revenue", "positive", "💰")
    with c2:
        render_kpi_card("Total Profit", format_currency(profit), "Net earnings", "positive" if profit >= 0 else "negative", "📈")
    with c3:
        render_kpi_card("Profit Margin", f"{margin:.2f}%", "Profit / Sales", "positive" if margin >= 10 else "negative", "📊")
    with c4:
        render_kpi_card("Avg. Discount", f"{avg_discount:.2f}%", "Average discount rate", "neutral", "🏷️")
    with c5:
        render_kpi_card("Total Products", format_number(products_count), "Catalog SKUs", "neutral", "📦")
    with c6:
        render_kpi_card("Sub-Categories", str(subcats_count), "Product families", "neutral", "📑")

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 2. Category Performance (Sales & Profit)
    render_section_header("📦 Category Performance")
    col_c_sales, col_c_profit = st.columns(2)
    cat_agg = df.groupby('category').agg({'sales': 'sum', 'profit': 'sum'}).reset_index().sort_values('sales', ascending=False)

    with col_c_sales:
        fig_cs = px.bar(
            cat_agg,
            x='category',
            y='sales',
            text=cat_agg['sales'].apply(lambda x: f"${x:,.0f}"),
            color='category',
            color_discrete_map={'Technology': COLOR_PRIMARY, 'Furniture': COLOR_SECONDARY, 'Office Supplies': COLOR_SUCCESS},
            title="Sales by Category"
        )
        fig_cs.update_layout(xaxis_title="Category", yaxis_title="Sales ($ USD)", showlegend=False)
        fig_cs = apply_plotly_theme(fig_cs, height=270)
        st.plotly_chart(fig_cs, use_container_width=True)

    with col_c_profit:
        fig_cp = px.bar(
            cat_agg,
            x='category',
            y='profit',
            text=cat_agg['profit'].apply(lambda x: f"${x:,.0f}"),
            color='category',
            color_discrete_map={'Technology': COLOR_PRIMARY, 'Furniture': COLOR_SECONDARY, 'Office Supplies': COLOR_SUCCESS},
            title="Profit by Category"
        )
        fig_cp.update_layout(xaxis_title="Category", yaxis_title="Profit ($ USD)", showlegend=False)
        fig_cp = apply_plotly_theme(fig_cp, height=270)
        st.plotly_chart(fig_cp, use_container_width=True)

    # 3. Sub-Category Performance (Profit & Margins)
    render_section_header("🏷️ Sub-Category Performance & Margins")
    col_sub_p, col_sub_m = st.columns(2)

    sub_agg = df.groupby('sub_category').agg({'sales': 'sum', 'profit': 'sum'}).reset_index()
    sub_agg['margin'] = (sub_agg['profit'] / sub_agg['sales']) * 100

    with col_sub_p:
        sub_p_sorted = sub_agg.sort_values('profit', ascending=True)
        colors_sub_p = [COLOR_DANGER if p < 0 else COLOR_SUCCESS for p in sub_p_sorted['profit']]
        fig_sub_p = go.Figure()
        fig_sub_p.add_trace(go.Bar(
            y=sub_p_sorted['sub_category'],
            x=sub_p_sorted['profit'],
            orientation='h',
            marker_color=colors_sub_p,
            text=sub_p_sorted['profit'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="Sub-Category: <b>%{y}</b><br>Profit: $%{x:,.2f}<extra></extra>"
        ))
        fig_sub_p.update_layout(title="Profit by Sub-Category", xaxis_title="Net Profit ($ USD)", yaxis_title="Sub-Category")
        fig_sub_p = apply_plotly_theme(fig_sub_p, height=330)
        st.plotly_chart(fig_sub_p, use_container_width=True)

    with col_sub_m:
        sub_m_sorted = sub_agg.sort_values('margin', ascending=True)
        colors_sub_m = [COLOR_DANGER if m < 0 else COLOR_SECONDARY for m in sub_m_sorted['margin']]
        fig_sub_m = go.Figure()
        fig_sub_m.add_trace(go.Bar(
            y=sub_m_sorted['sub_category'],
            x=sub_m_sorted['margin'],
            orientation='h',
            marker_color=colors_sub_m,
            text=sub_m_sorted['margin'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto',
            hovertemplate="Sub-Category: <b>%{y}</b><br>Margin: %{x:.2f}%<extra></extra>"
        ))
        fig_sub_m.update_layout(title="Profit Margin by Sub-Category (%)", xaxis_title="Profit Margin (%)", yaxis_title="Sub-Category")
        fig_sub_m = apply_plotly_theme(fig_sub_m, height=330)
        st.plotly_chart(fig_sub_m, use_container_width=True)

    # 4. Discount vs Profit Dynamics
    render_section_header("💸 Discount vs. Profit Dynamics")
    sample_df = df.sample(min(3000, len(df)), random_state=42) if len(df) > 3000 else df
    fig_scat = px.scatter(
        sample_df,
        x='discount',
        y='profit',
        color='category',
        color_discrete_map={'Technology': COLOR_PRIMARY, 'Furniture': COLOR_WARNING, 'Office Supplies': COLOR_SUCCESS},
        hover_data=['sub_category', 'sales', 'order_id'],
        opacity=0.65,
        title="Discount Rate vs. Profit"
    )
    fig_scat.add_hline(y=0, line_dash="dash", line_color="#ef4444", annotation_text="Break-Even ($0)")
    fig_scat.update_layout(xaxis_title="Discount Rate (0.2 = 20%)", yaxis_title="Profit ($ USD)")
    fig_scat = apply_plotly_theme(fig_scat, height=300)
    st.plotly_chart(fig_scat, use_container_width=True)

    # 5. Top & Bottom Products Leaderboard
    render_section_header("🏆 Top & Bottom Products Performance")
    prod_agg = df.groupby(['product_id', 'product_name', 'category', 'sub_category']).agg({
        'sales': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()

    tab_s, tab_p, tab_l = st.tabs([
        "💰 Top 10 Products by Sales",
        "💎 Top 10 Products by Profit",
        "⚠️ Bottom 10 Products by Profit (Loss Leaders)"
    ])

    with tab_s:
        top10_s = prod_agg.sort_values('sales', ascending=False).head(10)
        st.dataframe(
            top10_s[['product_name', 'category', 'sub_category', 'sales', 'profit', 'quantity']].rename(columns={
                'product_name': 'Product Name',
                'category': 'Category',
                'sub_category': 'Sub-Category',
                'sales': 'Sales ($)',
                'profit': 'Profit ($)',
                'quantity': 'Units'
            }).style.format({'Sales ($)': '${:,.2f}', 'Profit ($)': '${:,.2f}', 'Units': '{:,}'}),
            use_container_width=True,
            hide_index=True
        )

    with tab_p:
        top10_p = prod_agg.sort_values('profit', ascending=False).head(10)
        st.dataframe(
            top10_p[['product_name', 'category', 'sub_category', 'sales', 'profit', 'quantity']].rename(columns={
                'product_name': 'Product Name',
                'category': 'Category',
                'sub_category': 'Sub-Category',
                'sales': 'Sales ($)',
                'profit': 'Profit ($)',
                'quantity': 'Units'
            }).style.format({'Sales ($)': '${:,.2f}', 'Profit ($)': '${:,.2f}', 'Units': '{:,}'}),
            use_container_width=True,
            hide_index=True
        )

    with tab_l:
        bot10_p = prod_agg.sort_values('profit', ascending=True).head(10)
        st.dataframe(
            bot10_p[['product_name', 'category', 'sub_category', 'sales', 'profit', 'quantity']].rename(columns={
                'product_name': 'Product Name',
                'category': 'Category',
                'sub_category': 'Sub-Category',
                'sales': 'Sales ($)',
                'profit': 'Net Loss ($)',
                'quantity': 'Units'
            }).style.format({'Sales ($)': '${:,.2f}', 'Net Loss ($)': '${:,.2f}', 'Units': '{:,}'}),
            use_container_width=True,
            hide_index=True
        )

    render_warning_box("""
        <b>⚠️ Product Pricing Insights:</b><br>
        • <b>Tables Deficit:</b> <i>Tables</i> is the only net loss-making sub-category globally (-$64K loss) driven by excessive promotional discounting.<br>
        • <b>High-Discount Risk:</b> Orders discounted over <b>20%</b> frequently produce negative profits.
    """)
