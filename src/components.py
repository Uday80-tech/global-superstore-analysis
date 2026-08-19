import streamlit as st
import plotly.graph_objects as go

# Color Palette Constants (Original Theme)
COLOR_PRIMARY = "#6366f1"     # Indigo
COLOR_SECONDARY = "#38bdf8"   # Sky
COLOR_SUCCESS = "#10b981"     # Emerald Green
COLOR_DANGER = "#f43f5e"      # Rose / Red
COLOR_WARNING = "#f59e0b"     # Amber
COLOR_BG_CARD = "#1e293b"     # Slate 800
COLOR_TEXT_MUTED = "#94a3b8"  # Slate 400
COLOR_BORDER = "#334155"      # Slate 700

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#f8fafc"},
        "title": {"font": {"size": 15, "color": "#f8fafc"}},
        "xaxis": {
            "gridcolor": "#334155",
            "zerolinecolor": "#475569",
            "tickfont": {"color": "#94a3b8"}
        },
        "yaxis": {
            "gridcolor": "#334155",
            "zerolinecolor": "#475569",
            "tickfont": {"color": "#94a3b8"}
        },
        "hoverlabel": {
            "bgcolor": "#1e293b",
            "bordercolor": "#6366f1",
            "font": {"family": "Inter, sans-serif", "color": "#ffffff"}
        },
        "margin": {"l": 40, "r": 20, "t": 45, "b": 40}
    }
}


def inject_custom_css():
    """Injects high-aesthetic custom CSS into Streamlit with permanent sidebar and custom filter cards."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
            
            /* Main Background styling */
            .stApp {
                background: linear-gradient(135deg, #0b0f19 0%, #0f172a 50%, #111827 100%);
            }

            /* PERMANENT SIDEBAR: Prevent collapsing */
            [data-testid="stSidebarCollapseButton"] {
                display: none !important;
            }
            [data-testid="collapsedControl"] {
                display: none !important;
            }
            button[kind="header"] {
                display: none !important;
            }
            
            /* Hide Streamlit auto-generated MPA page links */
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
            
            /* Sidebar background and width */
            section[data-testid="stSidebar"] {
                background: #090e17 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
                min-width: 285px !important;
                max-width: 300px !important;
            }

            /* ── Custom Filter Popover Cards (Matching Reference UI) ──────── */
            [data-testid="stSidebar"] [data-testid="stPopover"] {
                margin-bottom: 7px !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stPopover"] > button,
            [data-testid="stSidebar"] [data-testid="stPopover"] button[kind="secondary"] {
                background: #0f172a !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 11px !important;
                padding: 7px 11px !important;
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                justify-content: flex-start !important;
                min-height: 52px !important;
                width: 100% !important;
                cursor: pointer !important;
                transition: all 0.18s ease !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stPopover"] > button:hover,
            [data-testid="stSidebar"] [data-testid="stPopover"] button[kind="secondary"]:hover {
                border-color: rgba(99, 102, 241, 0.5) !important;
                background: #141f36 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
            }

            /* Inner text layout for the filter card */
            [data-testid="stSidebar"] [data-testid="stPopover"] > button div[data-testid="stMarkdownContainer"],
            [data-testid="stSidebar"] [data-testid="stPopover"] > button p {
                white-space: pre-line !important;
                text-align: left !important;
                font-size: 0.83rem !important;
                line-height: 1.25 !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                margin: 0 !important;
            }

            /* Chevron downward arrow on the right */
            [data-testid="stSidebar"] [data-testid="stPopover"] > button::after {
                content: "⌄";
                font-size: 1.2rem;
                font-weight: 700;
                color: #94a3b8;
                margin-left: auto;
                padding-right: 2px;
                line-height: 1;
            }

            /* Badge 1: Order Year (Purple) */
            [data-testid="stSidebar"] [data-testid="stPopover"]:nth-of-type(1) > button::before {
                content: "📅";
                background: linear-gradient(135deg, #6366f1, #4f46e5);
                width: 34px;
                height: 34px;
                min-width: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.95rem;
                margin-right: 10px;
                box-shadow: 0 2px 6px rgba(99, 102, 241, 0.35);
            }

            /* Badge 2: Market (Cyan/Teal) */
            [data-testid="stSidebar"] [data-testid="stPopover"]:nth-of-type(2) > button::before {
                content: "🌐";
                background: linear-gradient(135deg, #06b6d4, #0891b2);
                width: 34px;
                height: 34px;
                min-width: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.95rem;
                margin-right: 10px;
                box-shadow: 0 2px 6px rgba(6, 182, 212, 0.35);
            }

            /* Badge 3: Region (Red/Coral) */
            [data-testid="stSidebar"] [data-testid="stPopover"]:nth-of-type(3) > button::before {
                content: "📍";
                background: linear-gradient(135deg, #f43f5e, #e11d48);
                width: 34px;
                height: 34px;
                min-width: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.95rem;
                margin-right: 10px;
                box-shadow: 0 2px 6px rgba(244, 63, 94, 0.35);
            }

            /* Badge 4: Category (Amber/Orange) */
            [data-testid="stSidebar"] [data-testid="stPopover"]:nth-of-type(4) > button::before {
                content: "📦";
                background: linear-gradient(135deg, #f59e0b, #d97706);
                width: 34px;
                height: 34px;
                min-width: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.95rem;
                margin-right: 10px;
                box-shadow: 0 2px 6px rgba(245, 158, 11, 0.35);
            }

            /* Badge 5: Sub-Category (Emerald/Green) */
            [data-testid="stSidebar"] [data-testid="stPopover"]:nth-of-type(5) > button::before {
                content: "🏷️";
                background: linear-gradient(135deg, #10b981, #059669);
                width: 34px;
                height: 34px;
                min-width: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.95rem;
                margin-right: 10px;
                box-shadow: 0 2px 6px rgba(16, 185, 129, 0.35);
            }

            /* Badge 6: Segment (Blue) */
            [data-testid="stSidebar"] [data-testid="stPopover"]:nth-of-type(6) > button::before {
                content: "👥";
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                width: 34px;
                height: 34px;
                min-width: 34px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.95rem;
                margin-right: 10px;
                box-shadow: 0 2px 6px rgba(59, 130, 246, 0.35);
            }

            /* ── Popover Body Panel ───────────────────────────────────────── */
            div[data-testid="stPopoverBody"] {
                background: #0f172a !important;
                border: 1px solid #334155 !important;
                border-radius: 12px !important;
                padding: 12px !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            }

            div[data-testid="stPopoverBody"] label {
                font-size: 0.82rem !important;
                color: #e2e8f0 !important;
            }

            div[data-testid="stPopoverBody"] button[kind="primaryFormSubmit"] {
                background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 8px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                margin-top: 8px !important;
                padding: 6px 12px !important;
                width: 100% !important;
            }

            div[data-testid="stPopoverBody"] input[type="text"] {
                background: rgba(30, 41, 59, 0.8) !important;
                border: 1px solid #475569 !important;
                border-radius: 7px !important;
                color: #f8fafc !important;
                font-size: 0.80rem !important;
                padding: 5px 8px !important;
            }

            /* ── Reset Filters Button (Matching Reference Image) ──────────── */
            [data-testid="stSidebar"] button[key="reset_filters_btn"],
            [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:last-child {
                background: rgba(99, 102, 241, 0.08) !important;
                border: 1px solid rgba(99, 102, 241, 0.35) !important;
                color: #a5b4fc !important;
                border-radius: 10px !important;
                font-size: 0.84rem !important;
                font-weight: 700 !important;
                padding: 9px 14px !important;
                width: 100% !important;
                transition: all 0.15s ease !important;
            }
            
            [data-testid="stSidebar"] button[key="reset_filters_btn"]:hover,
            [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:last-child:hover {
                background: rgba(99, 102, 241, 0.22) !important;
                border-color: #6366f1 !important;
                color: #ffffff !important;
                transform: translateY(-1px) !important;
            }

            /* ── KPI Card styling ─────────────────────────────────────────── */
            .kpi-card {
                background: linear-gradient(145deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
                padding: 18px 20px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
                margin-bottom: 12px;
            }
            .kpi-card:hover {
                transform: translateY(-3px);
                border-color: rgba(99, 102, 241, 0.4);
                box-shadow: 0 20px 30px -10px rgba(99, 102, 241, 0.2);
            }
            .kpi-title {
                color: #94a3b8;
                font-size: 0.82rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 5px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .kpi-value {
                color: #f8fafc;
                font-size: 1.75rem;
                font-weight: 700;
                letter-spacing: -0.02em;
                margin-bottom: 3px;
            }
            .kpi-subtitle {
                font-size: 0.78rem;
                color: #cbd5e1;
            }
            .badge-positive {
                color: #34d399;
                font-weight: 600;
            }
            .badge-negative {
                color: #fb7185;
                font-weight: 600;
            }
            .badge-neutral {
                color: #38bdf8;
                font-weight: 600;
            }

            /* Section headers */
            .section-header {
                font-size: 1.25rem;
                font-weight: 600;
                color: #f1f5f9;
                margin-top: 1.4rem;
                margin-bottom: 0.7rem;
                display: flex;
                align-items: center;
                gap: 8px;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                padding-bottom: 6px;
            }

            /* Insight Callout Box */
            .insight-box {
                background: rgba(99, 102, 241, 0.08);
                border-left: 4px solid #6366f1;
                border-radius: 0 10px 10px 0;
                padding: 12px 16px;
                margin: 14px 0;
                color: #e2e8f0;
                font-size: 0.90rem;
                line-height: 1.55;
            }

            /* Warning Callout Box */
            .warning-box {
                background: rgba(244, 63, 94, 0.08);
                border-left: 4px solid #f43f5e;
                border-radius: 0 10px 10px 0;
                padding: 12px 16px;
                margin: 14px 0;
                color: #fecdd3;
                font-size: 0.90rem;
                line-height: 1.55;
            }
        </style>
    """, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtitle: str = "", status: str = "neutral", icon: str = ""):
    """Renders the responsive, styled KPI card."""
    badge_class = "badge-neutral"
    if status == "positive":
        badge_class = "badge-positive"
    elif status == "negative":
        badge_class = "badge-negative"
        
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{icon} {title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle {badge_class}">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)


# Aliases for compatibility
render_kpi_card_v2 = render_kpi_card


def render_section_header(title: str):
    """Renders a styled section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def render_insight_box(content_html: str):
    """Renders the original insight callout box."""
    st.markdown(f'<div class="insight-box">{content_html}</div>', unsafe_allow_html=True)


def render_warning_box(content_html: str):
    """Renders the original warning callout box."""
    st.markdown(f'<div class="warning-box">{content_html}</div>', unsafe_allow_html=True)


def apply_plotly_theme(fig: go.Figure, height: int = 300) -> go.Figure:
    """Applies the cohesive sleek dark theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor=PLOTLY_TEMPLATE["layout"]["paper_bgcolor"],
        plot_bgcolor=PLOTLY_TEMPLATE["layout"]["plot_bgcolor"],
        font=PLOTLY_TEMPLATE["layout"]["font"],
        hoverlabel=PLOTLY_TEMPLATE["layout"]["hoverlabel"],
        margin=PLOTLY_TEMPLATE["layout"]["margin"],
        height=height
    )
    fig.update_xaxes(
        gridcolor=PLOTLY_TEMPLATE["layout"]["xaxis"]["gridcolor"],
        zerolinecolor=PLOTLY_TEMPLATE["layout"]["xaxis"]["zerolinecolor"]
    )
    fig.update_yaxes(
        gridcolor=PLOTLY_TEMPLATE["layout"]["yaxis"]["gridcolor"],
        zerolinecolor=PLOTLY_TEMPLATE["layout"]["yaxis"]["zerolinecolor"]
    )
    return fig
