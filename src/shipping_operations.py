import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add project root to Python path

from src.data_loader import load_superstore_data
from src.filters import render_sidebar_branding, render_sidebar_navigation, render_global_filters
from src.metrics import format_currency, format_number
from src.components import (
    inject_custom_css,
    render_kpi_card,
    render_section_header,
    render_insight_box,
    apply_plotly_theme,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)


def render_shipping_content(df: pd.DataFrame):
    """Renders Shipping & Operations analysis with original design."""
    st.title("🚚 Shipping & Operations Analysis")
    st.caption("Fulfillment turnaround times, shipping mode efficiency, and logistics economics.")

    if df.empty:
        st.warning("⚠️ No records match the selected filter criteria.")
        return

    # Calculate KPIs
    avg_delivery = float(df['delivery_days'].mean()) if 'delivery_days' in df.columns else 0.0
    total_shipping_cost = float(df['shipping_cost'].sum()) if 'shipping_cost' in df.columns else 0.0
    
    ship_mode_agg = df.groupby('ship_mode').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order_id': 'nunique',
        'delivery_days': 'mean',
        'shipping_cost': 'sum'
    }).reset_index()

    fastest_mode = ship_mode_agg.sort_values('delivery_days').iloc[0]['ship_mode'] if not ship_mode_agg.empty else "N/A"
    most_used_mode = ship_mode_agg.sort_values('sales', ascending=False).iloc[0]['ship_mode'] if not ship_mode_agg.empty else "N/A"

    # 1. Top KPI Row (4 Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Avg Delivery Time", f"{avg_delivery:.1f} Days", "Overall turnaround", "neutral", "⏱️")
    with c2:
        render_kpi_card("Fastest Ship Mode", fastest_mode, "< 1 Day turnaround", "positive", "⚡")
    with c3:
        render_kpi_card("Primary Ship Mode", most_used_mode, "Handles ~60% of volume", "neutral", "🚛")
    with c4:
        render_kpi_card("Total Shipping Cost", format_currency(total_shipping_cost), "Logistics budget", "neutral", "📦")

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 2. Delivery Speed & Shipping Mode Volume
    render_section_header("⏱️ Delivery Speed & Volume by Ship Mode")
    col_days, col_pie = st.columns(2)

    with col_days:
        ship_sorted = ship_mode_agg.sort_values('delivery_days', ascending=True)
        fig_days = go.Figure()
        fig_days.add_trace(go.Bar(
            x=ship_sorted['ship_mode'],
            y=ship_sorted['delivery_days'],
            marker_color=['#10b981', '#38bdf8', '#6366f1', '#f59e0b'],
            text=ship_sorted['delivery_days'].apply(lambda x: f"{x:.1f} d"),
            textposition='auto',
            hovertemplate="Ship Mode: <b>%{x}</b><br>Avg Days: %{y:.2f}<extra></extra>"
        ))
        fig_days.update_layout(title="Average Delivery Days by Ship Mode", xaxis_title="Shipping Mode", yaxis_title="Days")
        fig_days = apply_plotly_theme(fig_days, height=270)
        st.plotly_chart(fig_days, use_container_width=True)

    with col_pie:
        fig_pie = px.pie(
            ship_mode_agg,
            names='ship_mode',
            values='sales',
            hole=0.55,
            color='ship_mode',
            color_discrete_map={'Standard Class': '#6366f1', 'Second Class': '#38bdf8', 'First Class': '#10b981', 'Same Day': '#f59e0b'},
            title="Sales Volume by Ship Mode"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie = apply_plotly_theme(fig_pie, height=270)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 3. Order Priority & Profit Economics
    render_section_header("🎯 Order Priority & Shipping Economics")
    col_prio, col_profit_m = st.columns(2)

    with col_prio:
        if 'order_priority' in df.columns:
            prio_agg = df.groupby('order_priority').agg({'shipping_cost': 'mean'}).reset_index()
            fig_prio = px.bar(
                prio_agg,
                x='order_priority',
                y='shipping_cost',
                color='order_priority',
                color_discrete_map={'Critical': '#f43f5e', 'High': '#f59e0b', 'Medium': '#6366f1', 'Low': '#38bdf8'},
                text=prio_agg['shipping_cost'].apply(lambda x: f"${x:.2f}"),
                title="Avg Shipping Cost by Order Priority"
            )
            fig_prio.update_layout(xaxis_title="Order Priority", yaxis_title="Avg Shipping Cost ($)", showlegend=False)
            fig_prio = apply_plotly_theme(fig_prio, height=270)
            st.plotly_chart(fig_prio, use_container_width=True)

    with col_profit_m:
        fig_sp = go.Figure()
        fig_sp.add_trace(go.Bar(
            x=ship_mode_agg['ship_mode'],
            y=ship_mode_agg['profit'],
            marker_color=['#10b981', '#38bdf8', '#6366f1', '#f59e0b'],
            text=ship_mode_agg['profit'].apply(lambda x: f"${x/1e3:.0f}K"),
            textposition='auto',
            hovertemplate="Mode: <b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>"
        ))
        fig_sp.update_layout(title="Total Profit by Shipping Mode", xaxis_title="Shipping Mode", yaxis_title="Profit ($ USD)")
        fig_sp = apply_plotly_theme(fig_sp, height=270)
        st.plotly_chart(fig_sp, use_container_width=True)

    render_insight_box("""
        <b>🚛 Operational Insights:</b><br>
        • <b>Standard Class Backbone:</b> Fulfills ~60% of all orders within a reliable ~5.0 day delivery window.<br>
        • <b>Rapid Tiers:</b> Same Day delivers in 0.04 days (hours), First Class in 2.18 days, Second Class in 3.23 days.<br>
        • <b>Stable Margins:</b> Average unit profit is consistent ($27.70 – $28.94) across fulfillment options.
    """)
