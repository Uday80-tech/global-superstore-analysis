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


def render_geographic_content(df: pd.DataFrame):
    """Renders the Geographic Analysis with original design."""
    st.title("🌍 Geographic Analysis")
    st.caption("Comprehensive spatial intelligence across global markets, regions, countries, states, and cities.")

    if df.empty:
        st.warning("⚠️ No records match the selected filter criteria.")
        return

    # Calculate KPIs
    markets_count = df['market'].nunique()
    countries_count = df['country'].nunique()
    total_sales = calculate_total_sales(df)
    total_profit = calculate_total_profit(df)

    c_agg = df.groupby('country').agg({'sales': 'sum', 'profit': 'sum'}).reset_index()
    top_c_sales = c_agg.sort_values('sales', ascending=False).iloc[0] if not c_agg.empty else None
    top_c_profit = c_agg.sort_values('profit', ascending=False).iloc[0] if not c_agg.empty else None

    top_s_country = top_c_sales['country'] if top_c_sales is not None else "N/A"
    top_s_amount  = format_currency(top_c_sales['sales']) if top_c_sales is not None else ""
    top_p_country = top_c_profit['country'] if top_c_profit is not None else "N/A"
    top_p_amount  = format_currency(top_c_profit['profit']) if top_c_profit is not None else ""

    # 1. Top KPI Row (6 Cards)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card("Markets", str(markets_count), "7 Global Zones", "neutral", "🌐")
    with c2:
        render_kpi_card("Countries", str(countries_count), "Territories Served", "neutral", "📍")
    with c3:
        render_kpi_card("Total Sales", format_currency(total_sales), "Global turnover", "positive", "💰")
    with c4:
        render_kpi_card("Total Profit", format_currency(total_profit), "Net earnings", "positive" if total_profit >= 0 else "negative", "📈")
    with c5:
        render_kpi_card("Top Country · Sales", top_s_country, top_s_amount, "positive", "🏆")
    with c6:
        render_kpi_card("Top Country · Profit", top_p_country, top_p_amount, "positive", "💎")

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 2. Market & Regional Performance
    render_section_header("🌐 Market & Regional Performance")
    col_mkt, col_reg = st.columns(2)

    with col_mkt:
        mkt_summary = df.groupby('market').agg({'sales': 'sum'}).reset_index().sort_values('sales', ascending=False)
        fig_mkt = px.bar(
            mkt_summary,
            x='market',
            y='sales',
            text=mkt_summary['sales'].apply(lambda x: f"${x:,.0f}"),
            color='market',
            color_discrete_sequence=px.colors.qualitative.Prism,
            title="Sales by Market"
        )
        fig_mkt.update_layout(xaxis_title="Market", yaxis_title="Sales ($ USD)", showlegend=False)
        fig_mkt = apply_plotly_theme(fig_mkt, height=270)
        st.plotly_chart(fig_mkt, use_container_width=True)

    with col_reg:
        reg_summary = df.groupby('region').agg({'profit': 'sum'}).reset_index().sort_values('profit', ascending=True)
        colors_reg = [COLOR_DANGER if p < 0 else COLOR_SUCCESS for p in reg_summary['profit']]
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            y=reg_summary['region'],
            x=reg_summary['profit'],
            orientation='h',
            marker_color=colors_reg,
            text=reg_summary['profit'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="Region: <b>%{y}</b><br>Profit: $%{x:,.2f}<extra></extra>"
        ))
        fig_reg.update_layout(title="Profit by Region", xaxis_title="Profit ($ USD)", yaxis_title="Region")
        fig_reg = apply_plotly_theme(fig_reg, height=270)
        st.plotly_chart(fig_reg, use_container_width=True)

    # 3. Global Map
    render_section_header("🗺️ Worldwide Sales Distribution")
    fig_map = px.choropleth(
        c_agg,
        locations="country",
        locationmode="country names",
        color="sales",
        hover_name="country",
        hover_data={"sales": ":$,.0f", "profit": ":$,.0f", "country": False},
        color_continuous_scale="Viridis",
        title="Global Sales by Country"
    )
    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="#334155",
        showland=True,
        landcolor="#1e293b",
        showocean=True,
        oceancolor="#0b0f19",
        bgcolor="rgba(0,0,0,0)"
    )
    fig_map = apply_plotly_theme(fig_map, height=360)
    st.plotly_chart(fig_map, use_container_width=True)

    # 4. Top Countries Leaderboard
    render_section_header("🏆 Top Country Performance")
    col_t10_s, col_t10_p = st.columns(2)

    with col_t10_s:
        st.markdown("##### 💰 Top 10 Countries by Sales")
        top10_cs = c_agg.sort_values('sales', ascending=False).head(10)
        st.dataframe(
            top10_cs.rename(columns={'country': 'Country', 'sales': 'Sales ($)', 'profit': 'Profit ($)'}).style.format({
                'Sales ($)': '${:,.2f}',
                'Profit ($)': '${:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

    with col_t10_p:
        st.markdown("##### 💎 Top 10 Countries by Profit")
        top10_cp = c_agg.sort_values('profit', ascending=False).head(10)
        st.dataframe(
            top10_cp.rename(columns={'country': 'Country', 'sales': 'Sales ($)', 'profit': 'Profit ($)'}).style.format({
                'Sales ($)': '${:,.2f}',
                'Profit ($)': '${:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

    render_insight_box("""
        <b>📍 Geographic Key Observations:</b><br>
        • <b>United States Dominance:</b> Leads globally in both Gross Revenue ($2.30M) and Net Profit ($286.4K).<br>
        • <b>Regional Leaders:</b> Central, North, and North Asia generate the highest absolute margins.<br>
        • <b>Southeast Asia Squeeze:</b> Ranked 5th in sales ($884K) but produces only $17.8K profit due to heavy discounting.
    """)
