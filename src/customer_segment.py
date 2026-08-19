import streamlit as st
import pandas as pd
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
    calculate_total_customers,
    calculate_total_orders,
    calculate_aov,
    format_currency,
    format_number
)
from src.components import (
    inject_custom_css,
    render_kpi_card,
    render_section_header,
    render_insight_box,
    apply_plotly_theme,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS
)


def render_customer_segment_content(df: pd.DataFrame):
    """Renders Customer & Segment analysis with original design."""
    st.title("👥 Customer & Segment Insights")
    st.caption("Customer demographics, segment revenue contribution, loyalty, and top accounts.")

    if df.empty:
        st.warning("⚠️ No records match the selected filter criteria.")
        return

    # Calculate KPIs
    customers = calculate_total_customers(df)
    orders = calculate_total_orders(df)
    aov = calculate_aov(df)
    sales = calculate_total_sales(df)
    profit = calculate_total_profit(df)
    avg_spend = sales / customers if customers > 0 else 0

    seg_agg = df.groupby('segment').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    top_seg = seg_agg.sort_values('sales', ascending=False).iloc[0]['segment'] if not seg_agg.empty else "N/A"

    # 1. Top KPI Row (4 Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Customers", format_number(customers), "Unique accounts", "neutral", "👥")
    with c2:
        render_kpi_card("Top Segment", top_seg, "Majority sales & volume", "positive", "⭐")
    with c3:
        render_kpi_card("Overall AOV", format_currency(aov), "Sales / Order", "positive", "🎯")
    with c4:
        render_kpi_card("Avg Spend / Customer", format_currency(avg_spend), "Total Sales / Customers", "neutral", "💳")

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 2. Segment Performance Breakdown (Sales, Profit & AOV)
    render_section_header("📊 Segment Breakdown & Performance")
    col_seg_s, col_seg_p, col_seg_aov = st.columns(3)
    seg_agg['aov'] = seg_agg['sales'] / seg_agg['order_id']

    with col_seg_s:
        fig_s = px.bar(
            seg_agg,
            x='segment',
            y='sales',
            text=seg_agg['sales'].apply(lambda x: f"${x:,.0f}"),
            color='segment',
            color_discrete_map={'Consumer': COLOR_PRIMARY, 'Corporate': COLOR_SECONDARY, 'Home Office': COLOR_SUCCESS},
            title="Sales by Segment"
        )
        fig_s.update_layout(xaxis_title="Segment", yaxis_title="Sales ($ USD)", showlegend=False)
        fig_s = apply_plotly_theme(fig_s, height=270)
        st.plotly_chart(fig_s, use_container_width=True)

    with col_seg_p:
        fig_p = px.bar(
            seg_agg,
            x='segment',
            y='profit',
            text=seg_agg['profit'].apply(lambda x: f"${x:,.0f}"),
            color='segment',
            color_discrete_map={'Consumer': COLOR_PRIMARY, 'Corporate': COLOR_SECONDARY, 'Home Office': COLOR_SUCCESS},
            title="Profit by Segment"
        )
        fig_p.update_layout(xaxis_title="Segment", yaxis_title="Profit ($ USD)", showlegend=False)
        fig_p = apply_plotly_theme(fig_p, height=270)
        st.plotly_chart(fig_p, use_container_width=True)

    with col_seg_aov:
        fig_aov = px.bar(
            seg_agg,
            x='segment',
            y='aov',
            text=seg_agg['aov'].apply(lambda x: f"${x:.2f}"),
            color='segment',
            color_discrete_map={'Consumer': COLOR_PRIMARY, 'Corporate': COLOR_SECONDARY, 'Home Office': COLOR_SUCCESS},
            title="AOV by Segment"
        )
        fig_aov.update_layout(xaxis_title="Segment", yaxis_title="AOV ($ USD)", showlegend=False)
        fig_aov = apply_plotly_theme(fig_aov, height=270)
        st.plotly_chart(fig_aov, use_container_width=True)

    # 3. Top Customers Leaderboard
    render_section_header("🏆 Top Customers Leaderboards")
    col_t10_s, col_t10_p = st.columns(2)

    cust_agg = df.groupby(['customer_id', 'customer_name', 'segment']).agg({
        'sales': 'sum',
        'profit': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    cust_agg['margin'] = (cust_agg['profit'] / cust_agg['sales']) * 100

    with col_t10_s:
        st.markdown("##### 💰 Top 10 Customers by Sales")
        top10_s = cust_agg.sort_values('sales', ascending=False).head(10)
        st.dataframe(
            top10_s[['customer_name', 'segment', 'sales', 'profit', 'order_id']].rename(columns={
                'customer_name': 'Customer Name',
                'segment': 'Segment',
                'sales': 'Sales ($)',
                'profit': 'Profit ($)',
                'order_id': 'Orders'
            }).style.format({
                'Sales ($)': '${:,.2f}',
                'Profit ($)': '${:,.2f}',
                'Orders': '{:,}'
            }),
            use_container_width=True,
            hide_index=True
        )

    with col_t10_p:
        st.markdown("##### 💎 Top 10 Customers by Profit")
        top10_p = cust_agg.sort_values('profit', ascending=False).head(10)
        st.dataframe(
            top10_p[['customer_name', 'segment', 'sales', 'profit', 'order_id']].rename(columns={
                'customer_name': 'Customer Name',
                'segment': 'Segment',
                'sales': 'Sales ($)',
                'profit': 'Profit ($)',
                'order_id': 'Orders'
            }).style.format({
                'Sales ($)': '${:,.2f}',
                'Profit ($)': '${:,.2f}',
                'Orders': '{:,}'
            }),
            use_container_width=True,
            hide_index=True
        )

    render_insight_box("""
        <b>👥 Customer Segment Insights:</b><br>
        • <b>Consumer Anchor:</b> The Consumer segment represents over <b>51%</b> of total sales ($6.51M) and profit ($749.2K).<br>
        • <b>Balanced Profit Margins:</b> Profit margins remain consistent across segments (Consumer ~11.5%, Corporate ~11.5%, Home Office ~12.0%).<br>
        • <b>High Customer Retention:</b> Top accounts place repeat high-volume orders across multiple categories.
    """)
