import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_superstore_data
from src.filters import render_sidebar_branding, render_sidebar_navigation, render_global_filters
from src.metrics import (
    calculate_total_sales,
    calculate_total_profit,
    calculate_profit_margin,
    calculate_total_orders,
    calculate_total_customers,
    calculate_aov,
    calculate_total_quantity,
    calculate_loss_orders_count,
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
    COLOR_SUCCESS,
    COLOR_DANGER
)

# Page configuration
st.set_page_config(
    page_title="Global Superstore Analytics",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_overview_dashboard(df: pd.DataFrame):
    """Renders the executive overview dashboard."""
    st.title("🌐 Global Superstore Executive Overview")
    st.caption("High-level executive monitoring of global sales, profitability, operational health, and growth dynamics.")

    if df.empty:
        st.warning("⚠️ No data available for the selected filters. Please expand your filter selections in the sidebar.")
        return

    # Compute Core KPIs
    sales = calculate_total_sales(df)
    profit = calculate_total_profit(df)
    margin = calculate_profit_margin(df)
    orders = calculate_total_orders(df)
    customers = calculate_total_customers(df)
    aov = calculate_aov(df)
    total_qty = calculate_total_quantity(df)
    loss_orders = calculate_loss_orders_count(df)

    # 1. KPI Cards Grid (6 Cards)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card("Total Sales", format_currency(sales), f"{format_number(total_qty)} units sold", "positive", "💰")
    with c2:
        render_kpi_card("Total Profit", format_currency(profit), "Net earnings", "positive" if profit >= 0 else "negative", "📈")
    with c3:
        render_kpi_card("Profit Margin", f"{margin:.2f}%", "Profit / Sales", "positive" if margin >= 10 else "negative", "📊")
    with c4:
        render_kpi_card("Total Orders", format_number(orders), f"{loss_orders:,} loss items", "neutral", "📦")
    with c5:
        render_kpi_card("Total Customers", format_number(customers), "Unique accounts", "neutral", "👥")
    with c6:
        render_kpi_card("Avg Order Value", format_currency(aov), "Sales / Order", "positive", "🎯")

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 2. Sales & Profit Trends Section
    render_section_header("📅 Sales & Profit Trends")
    
    col_trend_left, col_trend_right = st.columns([3, 2])

    with col_trend_left:
        df_monthly = df.copy()
        df_monthly['year_month'] = df_monthly['order_date'].dt.to_period('M').astype(str)
        monthly = df_monthly.groupby('year_month').agg({'sales': 'sum', 'profit': 'sum'}).reset_index().sort_values('year_month')

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly['year_month'],
            y=monthly['sales'],
            name='Monthly Sales ($)',
            mode='lines+markers',
            line=dict(color=COLOR_PRIMARY, width=3),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.1)',
            hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly['year_month'],
            y=monthly['profit'],
            name='Monthly Profit ($)',
            mode='lines+markers',
            line=dict(color=COLOR_SUCCESS, width=2.5),
            hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>"
        ))
        fig_trend.update_layout(
            title="Monthly Sales & Profit Trend (48-Month Timeline)",
            xaxis_title="Year-Month",
            yaxis_title="Amount ($ USD)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        fig_trend = apply_plotly_theme(fig_trend, height=290)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_trend_right:
        yearly_summary = df.groupby('order_year').agg({'sales': 'sum', 'profit': 'sum'}).reset_index().sort_values('order_year')

        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Bar(
            x=yearly_summary['order_year'].astype(str),
            y=yearly_summary['sales'],
            name='Sales',
            marker_color=COLOR_PRIMARY,
            text=yearly_summary['sales'].apply(lambda x: f"${x/1e6:.2f}M"),
            textposition='auto',
            hovertemplate="Year %{x}<br>Sales: $%{y:,.0f}<extra></extra>"
        ))
        fig_yearly.add_trace(go.Bar(
            x=yearly_summary['order_year'].astype(str),
            y=yearly_summary['profit'],
            name='Profit',
            marker_color=COLOR_SUCCESS,
            text=yearly_summary['profit'].apply(lambda x: f"${x/1e3:.0f}K"),
            textposition='auto',
            hovertemplate="Year %{x}<br>Profit: $%{y:,.0f}<extra></extra>"
        ))
        fig_yearly.update_layout(
            title="Annual Revenue & Profit Growth",
            barmode='group',
            xaxis_title="Year",
            yaxis_title="Amount ($ USD)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_yearly = apply_plotly_theme(fig_yearly, height=290)
        st.plotly_chart(fig_yearly, use_container_width=True)

    # 3. Performance Breakdown (Category, Region, Segment)
    render_section_header("📊 Category, Regional & Segment Breakdown")
    
    col_cat, col_reg, col_seg = st.columns(3)

    with col_cat:
        cat_summary = df.groupby('category').agg({'sales': 'sum', 'profit': 'sum'}).reset_index().sort_values('sales', ascending=False)
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            x=cat_summary['category'],
            y=cat_summary['sales'],
            name='Sales ($)',
            marker_color=COLOR_SECONDARY,
            text=cat_summary['sales'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
        ))
        fig_cat.update_layout(title="Sales by Category", xaxis_title="Category", yaxis_title="Total Sales ($ USD)")
        fig_cat = apply_plotly_theme(fig_cat, height=250)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_reg:
        reg_summary = df.groupby('region').agg({'profit': 'sum'}).reset_index().sort_values('profit', ascending=True).tail(6)
        reg_colors = [COLOR_DANGER if p < 0 else COLOR_SUCCESS for p in reg_summary['profit']]

        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            y=reg_summary['region'],
            x=reg_summary['profit'],
            orientation='h',
            marker_color=reg_colors,
            text=reg_summary['profit'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="Region: <b>%{y}</b><br>Profit: $%{x:,.2f}<extra></extra>"
        ))
        fig_reg.update_layout(title="Profit by Region (Top Regions)", xaxis_title="Net Profit ($ USD)", yaxis_title="Region")
        fig_reg = apply_plotly_theme(fig_reg, height=250)
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_seg:
        seg_summary = df.groupby('segment').agg({'sales': 'sum'}).reset_index().sort_values('sales', ascending=False)
        fig_seg = go.Figure()
        fig_seg.add_trace(go.Bar(
            x=seg_summary['segment'],
            y=seg_summary['sales'],
            name='Sales ($)',
            marker_color=COLOR_PRIMARY,
            text=seg_summary['sales'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="Segment: <b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
        ))
        fig_seg.update_layout(title="Sales by Customer Segment", xaxis_title="Segment", yaxis_title="Total Sales ($ USD)")
        fig_seg = apply_plotly_theme(fig_seg, height=250)
        st.plotly_chart(fig_seg, use_container_width=True)

    # 4. Executive Callout Box
    render_insight_box("""
        <b>💡 Executive Takeaways:</b><br>
        • <b>Top Revenue Category:</b> Technology leads with over <b>$4.74M</b> in revenue and the highest profit contribution.<br>
        • <b>Predictable Q4 Spikes:</b> Clear end-of-year sales seasonality peaking in November and December across all 4 operational years.<br>
        • <b>Consumer Segment Majority:</b> The Consumer segment represents over <b>51%</b> of total business sales ($6.51M).
    """)


def main():
    inject_custom_css()
    raw_df = load_superstore_data()
    
    # Render Original Sidebar Branding
    render_sidebar_branding()
    
    # Render Original Navigation
    selected_page = render_sidebar_navigation(current_page="Overview")
    
    # Render Original Global Filters
    filtered_df = render_global_filters(raw_df)

    # Route based on navigation selection
    if "Overview" in selected_page:
        render_overview_dashboard(filtered_df)
    elif "Product" in selected_page:
        from src.product_pricing import render_product_pricing_content
        render_product_pricing_content(filtered_df)
    elif "Geographic" in selected_page:
        from src.geographic_analysis import render_geographic_content
        render_geographic_content(filtered_df)
    elif "Customer" in selected_page:
        from src.customer_segment import render_customer_segment_content
        render_customer_segment_content(filtered_df)
    elif "Shipping" in selected_page:
        from src.shipping_operations import render_shipping_content
        render_shipping_content(filtered_df)
    elif "Data" in selected_page:
        from src.data_explorer import render_data_explorer_content
        render_data_explorer_content(filtered_df)

if __name__ == "__main__":
    main()
