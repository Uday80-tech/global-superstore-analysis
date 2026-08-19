import streamlit as st
import pandas as pd
from typing import List

# ─────────────────────────────────────────────────────────────────────────────
# Core Filter Logic
# ─────────────────────────────────────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    selected_years: List[int] = None,
    selected_markets: List[str] = None,
    selected_regions: List[str] = None,
    selected_categories: List[str] = None,
    selected_subcategories: List[str] = None,
    selected_segments: List[str] = None
) -> pd.DataFrame:
    """
    Filters the dataset based on selected criteria.
    An empty list for any dimension means 'All' (no filtering applied).
    """
    out = df.copy()
    if selected_years:
        out = out[out['order_year'].isin(selected_years)]
    if selected_markets:
        out = out[out['market'].isin(selected_markets)]
    if selected_regions:
        out = out[out['region'].isin(selected_regions)]
    if selected_categories:
        out = out[out['category'].isin(selected_categories)]
    if selected_subcategories:
        out = out[out['sub_category'].isin(selected_subcategories)]
    if selected_segments:
        out = out[out['segment'].isin(selected_segments)]
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Custom Filter Card Block with Popover
# ─────────────────────────────────────────────────────────────────────────────

def _render_custom_filter_card(
    state_key: str,
    title: str,
    all_placeholder: str,
    options: list,
    trigger: int,
) -> list:
    """
    Renders a custom styled filter card that matches the reference UI:
      • Closed state: Compact card with colored badge, title, subtitle (e.g. 'All Years' / '2 Selected'), and chevron
      • Open state: Searchable multi-select checkbox list with 'Select All' and 'Apply' button
    """
    skey = f"{state_key}_{trigger}"

    if skey not in st.session_state:
        st.session_state[skey] = []

    current: list = st.session_state[skey]

    # Compute subtitle for the closed state
    if not current:
        subtitle = all_placeholder
    elif len(current) == 1:
        subtitle = str(current[0])
    elif len(current) == len(options) and len(options) > 0:
        subtitle = all_placeholder
    else:
        subtitle = f"{len(current)} Selected"

    # Button label formatted with Title and Subtitle (CSS formats title bold & subtitle muted)
    button_label = f"{title}\n{subtitle}"

    with st.sidebar.popover(button_label, use_container_width=True):
        with st.form(key=f"frm_{skey}", border=False):
            st.markdown(f"<div style='font-weight:700; color:#f8fafc; font-size:0.88rem; margin-bottom:8px;'>Filter by {title}</div>", unsafe_allow_html=True)
            
            # Search input
            search_query = st.text_input(
                "Search",
                placeholder=f"Search {title.lower()}...",
                label_visibility="collapsed",
                key=f"srch_{skey}"
            )

            # Filter visible options by search
            visible_opts = [o for o in options if search_query.lower() in str(o).lower()] if search_query else options

            # Select All toggle
            is_all_selected = (not current) or (len(current) == len(options))
            select_all = st.checkbox("Select All", value=is_all_selected, key=f"all_{skey}")

            st.markdown("<hr style='margin:4px 0 8px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

            # Scrollable options list container
            checks = {}
            for opt in visible_opts:
                is_checked = (not current) or (opt in current)
                checks[opt] = st.checkbox(str(opt), value=is_checked, key=f"opt_{skey}_{opt}")

            # Apply Button
            if st.form_submit_button("✓  Apply Selection", use_container_width=True):
                if select_all:
                    st.session_state[skey] = []  # Empty means all
                else:
                    chosen = [o for o in visible_opts if checks.get(o, False)]
                    st.session_state[skey] = chosen
                st.rerun()

    return st.session_state[skey]


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar Branding
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar_branding():
    """Renders the top branding area of the sidebar."""
    st.sidebar.markdown("""
        <div style="text-align:left; padding:4px 0 12px 0;">
            <h2 style="margin:0; color:#6366f1; font-weight:700; font-size:1.15rem; letter-spacing:-0.01em;">
                🌐 GLOBAL SUPERSTORE ANALYSIS
            </h2>
            <p style="margin:2px 0 0 0; color:#94a3b8; font-size:0.75rem; letter-spacing:0.06em; text-transform:uppercase;">
                Executive Analytics
            </p>
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar Navigation (6 Exact Options)
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar_navigation(current_page: str = "Overview") -> str:
    """
    Renders the unified 6-option navigation menu.
    """
    nav_options = [
        "🏠 Overview",
        "📦 Product & Pricing",
        "🌍 Geographic Analysis",
        "👥 Customer & Segment",
        "🚚 Shipping & Operations",
        "🔍 Data Explorer"
    ]

    page_map = {
        "overview": 0,
        "product": 1,
        "pricing": 1,
        "geographic": 2,
        "customer": 3,
        "segment": 3,
        "shipping": 4,
        "operations": 4,
        "data": 5,
        "explorer": 5
    }
    default_idx = 0
    for kw, idx in page_map.items():
        if kw in current_page.lower():
            default_idx = idx
            break

    st.sidebar.markdown("<div style='font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;'>NAVIGATION</div>", unsafe_allow_html=True)
    page_selection = st.sidebar.radio(
        label="Navigate to page:",
        options=nav_options,
        index=default_idx,
        label_visibility="collapsed"
    )
    return page_selection


# ─────────────────────────────────────────────────────────────────────────────
# Global Filters Panel (Matching User's Reference Image)
# ─────────────────────────────────────────────────────────────────────────────

def render_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders the 6 custom global filter cards matching the reference image.
    """
    all_years = sorted(df['order_year'].dropna().unique().tolist())
    all_markets = sorted(df['market'].dropna().unique().tolist())
    all_regions = sorted(df['region'].dropna().unique().tolist())
    all_categories = sorted(df['category'].dropna().unique().tolist())
    all_subcats = sorted(df['sub_category'].dropna().unique().tolist())
    all_segments = sorted(df['segment'].dropna().unique().tolist())

    if "filter_reset_trigger" not in st.session_state:
        st.session_state["filter_reset_trigger"] = 0
    trigger = st.session_state["filter_reset_trigger"]

    st.sidebar.markdown("---")
    
    # Header with glowing purple filter icon matching reference image
    st.sidebar.markdown("""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
            <div style="color:#818cf8; font-size:1.15rem; line-height:1; display:flex; align-items:center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
                </svg>
            </div>
            <span style="color:#818cf8; font-weight:700; font-size:0.88rem; letter-spacing:0.06em; text-transform:uppercase;">GLOBAL FILTERS</span>
        </div>
    """, unsafe_allow_html=True)

    # 1. Order Year Card
    sel_years = _render_custom_filter_card("fy", "Order Year", "All Years", all_years, trigger)

    # 2. Market Card
    sel_markets = _render_custom_filter_card("fm", "Market", "All Markets", all_markets, trigger)

    # 3. Region Card (Cascades from Market)
    region_pool = (
        sorted(df[df['market'].isin(sel_markets)]['region'].dropna().unique().tolist())
        if sel_markets else all_regions
    )
    rkey = f"fr_{trigger}"
    if rkey in st.session_state:
        st.session_state[rkey] = [r for r in st.session_state[rkey] if r in region_pool]
    sel_regions = _render_custom_filter_card("fr", "Region", "All Regions", region_pool, trigger)

    # 4. Category Card
    sel_categories = _render_custom_filter_card("fc", "Category", "All Categories", all_categories, trigger)

    # 5. Sub-Category Card (Cascades from Category)
    subcat_pool = (
        sorted(df[df['category'].isin(sel_categories)]['sub_category'].dropna().unique().tolist())
        if sel_categories else all_subcats
    )
    skey = f"fs_{trigger}"
    if skey in st.session_state:
        st.session_state[skey] = [s for s in st.session_state[skey] if s in subcat_pool]
    sel_subcats = _render_custom_filter_card("fs", "Sub-Category", "All Sub-Categories", subcat_pool, trigger)

    # 6. Segment Card
    sel_segments = _render_custom_filter_card("fg", "Segment", "All Segments", all_segments, trigger)

    # ── Reset Filters Button ─────────────────────────────────────────────────
    st.sidebar.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 Reset Filters", use_container_width=True, key="reset_filters_btn"):
        for sk in ["fy", "fm", "fr", "fc", "fs", "fg"]:
            full_k = f"{sk}_{trigger}"
            if full_k in st.session_state:
                del st.session_state[full_k]
        st.session_state["filter_reset_trigger"] += 1
        st.rerun()

    # ── Apply Filters to DataFrame ───────────────────────────────────────────
    filtered_df = apply_filters(
        df,
        selected_years=sel_years,
        selected_markets=sel_markets,
        selected_regions=sel_regions,
        selected_categories=sel_categories,
        selected_subcategories=sel_subcats,
        selected_segments=sel_segments
    )

    # ── Status Footer Area ───────────────────────────────────────────────────
    st.sidebar.markdown("---")
    pct = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0.0
    st.sidebar.markdown(f"""
        <div style="font-size:0.73rem; color:#64748b; line-height:1.55;">
            <div style="color:#94a3b8; font-weight:600;">Active: <span style="color:#c7d2fe;">{len(filtered_df):,}</span> / {len(df):,} records</div>
            <div>Data coverage: {pct:.1f}%</div>
            <div style="margin-top:4px;"><span style="color:#34d399; font-weight:600;">🟢 Dashboard Live</span></div>
        </div>
    """, unsafe_allow_html=True)

    return filtered_df
