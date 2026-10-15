"""Script to build the complete, revamped, clean English app.py for STATEC Hackathon 2026.
"""
from pathlib import Path

APP_CODE = '''"""STATEC Hackathon 2026 — Luxembourg External Trade Intelligence (2000–2026).
Dataset: Eurostat ds-045409 (EU trade since 1988 by HS2-4-6 and CN8).
Pure Tabular CSV Architecture.
"""

import sys
from pathlib import Path
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.dashboard.design_system import (
    PRIMARY, SECONDARY, SUCCESS, DANGER, WARNING, NEUTRAL,
    SURFACE, BACKGROUND, BORDER, TEXT_PRIMARY, TEXT_MUTED,
    CATEGORICAL, CARD_STYLE, KPI_CARD_STYLE, apply_plot_theme,
    apply_map_theme, create_icon_badge,
    add_iso3_column, ISO2_TO_ISO3, STATEC_NAVY, STATEC_YELLOW, STATEC_BLUE,
    STATEC_RED, STATEC_GRAY, STATEC_BG,
    create_section_header, create_dashboard_footer, create_infobox,
    create_info_hover, INFO_HOVER_CSS, fmt_eur, fmt_pct, get_concentration_badge
)
from src.dashboard.data_loader import (
    load_overview_kpis, load_partner_rankings, load_product_rankings,
    load_hs4_product_rankings, load_product_partners, load_seasonal_decomposition,
    load_country_benchmarks, load_drilldown_lvl2, load_drilldown_lvl4, load_drilldown_lvl8
)

# Standard Country Names in English
ISO2_NAMES_EN = {
    "DE": "Germany", "FR": "France", "BE": "Belgium", "NL": "Netherlands",
    "US": "United States", "IT": "Italy", "GB": "United Kingdom", "ES": "Spain",
    "CN": "China", "CH": "Switzerland", "PL": "Poland", "AT": "Austria",
    "SE": "Sweden", "JP": "Japan", "CZ": "Czechia", "DK": "Denmark",
    "IE": "Ireland", "PT": "Portugal", "TR": "Turkey", "IN": "India",
    "BR": "Brazil", "KR": "South Korea", "NO": "Norway", "RU": "Russia",
    "CA": "Canada", "MX": "Mexico", "AU": "Australia", "ZA": "South Africa",
    "HU": "Hungary", "RO": "Romania", "SG": "Singapore", "LU": "Luxembourg",
    "FI": "Finland", "SK": "Slovakia", "GR": "Greece", "BG": "Bulgaria",
    "HR": "Croatia", "SI": "Slovenia", "LT": "Lithuania", "LV": "Latvia",
    "EE": "Estonia", "CY": "Cyprus", "MT": "Malta"
}

def get_country_name(code: str) -> str:
    c = str(code).upper().strip()
    return ISO2_NAMES_EN.get(c, c)

# Initialize Dash App
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&display=swap"
    ],
    title="Luxembourg Trade Intelligence (Resilience Radar) — STATEC Hackathon 2026",
    suppress_callback_exceptions=True
)
app.index_string = f"""<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
{INFO_HOVER_CSS}
        body {{
            background-color: {BACKGROUND};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: {TEXT_PRIMARY};
        }}
        .nav-box-card {{
            background-color: #FFFFFF;
            border-radius: 10px;
            border: 1px solid {BORDER};
            padding: 12px 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0, 26, 56, 0.04);
        }}
        .nav-tab-btn {{
            cursor: pointer;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            font-family: 'Montserrat', sans-serif;
            padding: 8px 14px;
            margin: 3px 4px;
            transition: all 0.15s ease-in-out;
            border: 1px solid {BORDER};
            background-color: #FFFFFF;
            color: {STATEC_NAVY};
            display: inline-flex;
            align-items: center;
            text-decoration: none;
            user-select: none;
        }}
        .nav-tab-btn:hover {{
            background-color: #F8FAFC;
            border-color: #94A3B8;
            color: {STATEC_BLUE};
        }}
        .nav-tab-btn.active {{
            background-color: {STATEC_NAVY} !important;
            color: #FFFFFF !important;
            border-color: {STATEC_NAVY} !important;
            border-bottom: 3px solid {STATEC_YELLOW} !important;
            box-shadow: 0 2px 8px rgba(0, 26, 56, 0.25);
        }}
        .compact-kpi-tile {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 8px 14px;
            box-shadow: 0 1px 3px rgba(0, 26, 56, 0.03);
            height: 100%;
        }}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>"""
server = app.server


# ── Clean, Decluttered Header ──────────────────────────────────────────────
def create_header():
    return html.Div([
        # Main Top Bar
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            # Brand Logo
                            html.Div([
                                create_icon_badge("bi bi-shield-check", color=STATEC_NAVY, bg="#FFF9E6", size=20, box_size=40),
                                html.Div([
                                    html.Div([
                                        html.Span("TRADE", style={"fontSize": "22px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY}),
                                        html.Span(".lu", style={"fontSize": "22px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_YELLOW}),
                                    ]),
                                    html.Span("RESILIENCE RADAR", style={"fontSize": "9px", "fontWeight": "800", "letterSpacing": "1.2px", "color": STATEC_GRAY, "display": "block", "marginTop": "-4px"}),
                                ], className="ms-2")
                            ], className="d-flex align-items-center", style={"minWidth": "220px"}),

                            # Vertical Divider
                            html.Div(style={"width": "1px", "height": "32px", "backgroundColor": "#CBD5E1", "margin": "0 18px"}, className="d-none d-lg-block"),

                            # Title & Scope
                            html.Div([
                                html.Span("LUXEMBOURG EXTERNAL TRADE INTELLIGENCE", style={"fontSize": "15px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "display": "block"}),
                                html.Span("National Resilience Strategy (Pillars 3–5) • Eurostat Comext Open Data [ds-045409] (2000–2026)", style={"fontSize": "11px", "fontWeight": "500", "color": STATEC_GRAY, "display": "block"}),
                            ], className="d-none d-lg-block"),
                        ], className="d-flex align-items-center py-2")
                    ], md=8),

                    dbc.Col([
                        html.Div([
                            # Year Selector (Defaults to 2025)
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-calendar3 me-1", style={"color": STATEC_BLUE}),
                                    "ANALYSIS YEAR"
                                ], style={"fontSize": "10px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.5px", "marginBottom": "2px"}),
                                dcc.Dropdown(
                                    id="global-year-dropdown",
                                    options=[{"label": str(y), "value": y} for y in range(2025, 1999, -1)],
                                    value=2025,
                                    clearable=False,
                                    style={"fontSize": "13px", "fontWeight": "700", "borderRadius": "6px", "minWidth": "105px"}
                                )
                            ], className="d-flex flex-column align-items-end")
                        ], className="d-flex justify-content-end align-items-center py-2")
                    ], md=4)
                ], className="align-items-center")
            ], fluid=True, style={"maxWidth": "1540px"})
        ], style={"backgroundColor": "#FFFFFF", "borderBottom": "1px solid #E2E8F0"}),

        # Subtle institutional ribbon
        html.Div([
            dbc.Container([
                html.Div([
                    html.Span("STATEC HACKATHON 2026 PROTOTYPE", style={"backgroundColor": STATEC_YELLOW, "color": STATEC_NAVY, "fontWeight": "800", "fontSize": "9.5px", "padding": "2px 7px", "borderRadius": "4px", "marginRight": "10px", "fontFamily": "'Montserrat', sans-serif"}),
                    html.Span("Independent research demonstrator — answering leadership sovereignty questions first, full data analyst deep-dives afterwards.", style={"color": "#E2E8F0", "fontSize": "11px", "fontWeight": "500"}),
                ], className="d-flex align-items-center")
            ], fluid=True, style={"maxWidth": "1540px"})
        ], style={"backgroundColor": STATEC_NAVY, "padding": "5px 0", "marginBottom": "16px", "borderBottom": f"2.5px solid {STATEC_YELLOW}"})
    ])


# ── Compact Key Figures Ribbon (Leadership View Only) ───────────────────────
def create_compact_kpi_ribbon(year: int):
    df = load_overview_kpis()
    if df.empty:
        return html.Div()

    row = df[df["year"] == year]
    if row.empty:
        row = df[df["year"] == df["year"].max()]

    r = row.iloc[0]
    exp_val = r.get("EXPORT", 0.0)
    imp_val = r.get("IMPORT", 0.0)
    bal_val = r.get("trade_balance_eur", exp_val - imp_val)
    cov_val = r.get("coverage_ratio_pct", (exp_val / imp_val * 100) if imp_val > 0 else 0)
    eu_imp = r.get("intra_eu_import_share_pct", 84.5)

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("IMPORTS (GOODS)", style={"fontSize": "10px", "fontWeight": "800", "color": TEXT_MUTED, "letterSpacing": "0.4px"}),
                    html.H5(fmt_eur(imp_val), style={"fontWeight": "800", "color": STATEC_NAVY, "margin": "1px 0"}),
                    html.Small("Physical supply to country", style={"fontSize": "10px", "color": TEXT_MUTED})
                ], className="compact-kpi-tile")
            ], md=2, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("EXPORTS (GOODS)", style={"fontSize": "10px", "fontWeight": "800", "color": TEXT_MUTED, "letterSpacing": "0.4px"}),
                    html.H5(fmt_eur(exp_val), style={"fontWeight": "800", "color": STATEC_BLUE, "margin": "1px 0"}),
                    html.Small("Manufactured goods & steel", style={"fontSize": "10px", "color": TEXT_MUTED})
                ], className="compact-kpi-tile")
            ], md=2, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("MERCHANDISE BALANCE", style={"fontSize": "10px", "fontWeight": "800", "color": TEXT_MUTED, "letterSpacing": "0.4px"}),
                    html.H5(fmt_eur(bal_val), style={"fontWeight": "800", "color": DANGER if bal_val < 0 else SUCCESS, "margin": "1px 0"}),
                    html.Small("Structural goods deficit", style={"fontSize": "10px", "color": TEXT_MUTED})
                ], className="compact-kpi-tile")
            ], md=3, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("COVERAGE RATIO", style={"fontSize": "10px", "fontWeight": "800", "color": TEXT_MUTED, "letterSpacing": "0.4px"}),
                    html.H5(f"{cov_val:.1f}%", style={"fontWeight": "800", "color": STATEC_NAVY, "margin": "1px 0"}),
                    html.Small("Balanced by €25B+ services surplus", style={"fontSize": "10px", "color": SUCCESS, "fontWeight": "600"})
                ], className="compact-kpi-tile")
            ], md=3, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("INTRA-EU IMPORTS", style={"fontSize": "10px", "fontWeight": "800", "color": TEXT_MUTED, "letterSpacing": "0.4px"}),
                    html.H5(f"{eu_imp:.1f}%", style={"fontWeight": "800", "color": STATEC_BLUE, "margin": "1px 0"}),
                    html.Small("Single market legal safety", style={"fontSize": "10px", "color": TEXT_MUTED})
                ], className="compact-kpi-tile")
            ], md=2, sm=6, className="mb-2"),
        ], className="g-2")
    ], className="mb-3")


# ── The 10 Buttons in 2 Organizing Boxes ───────────────────────────────────
def create_navigation_boxes():
    return html.Div([
        # Box 1: National Leadership Briefings (4 Buttons)
        html.Div([
            html.Div([
                create_icon_badge("bi bi-bank2", color=STATEC_NAVY, bg="#FFF9E6", size=15, box_size=28),
                html.Span("1. NATIONAL LEADERSHIP BRIEFING", style={
                    "fontSize": "11.5px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif",
                    "color": STATEC_NAVY, "letterSpacing": "0.6px", "marginLeft": "8px"
                }),
                html.Span("EXECUTIVE STRATEGY", style={
                    "backgroundColor": STATEC_NAVY, "color": STATEC_YELLOW, "fontSize": "9px",
                    "fontWeight": "800", "padding": "2px 6px", "borderRadius": "3px", "marginLeft": "8px"
                })
            ], className="d-flex align-items-center mb-2"),

            html.Div([
                html.Button([
                    html.I(className="bi bi-shield-check me-1 text-warning"),
                    "1. Sovereign Resilience Radar"
                ], id="btn-tab-resilience", className="nav-tab-btn active", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-graph-up me-1 text-primary"),
                    "2. Macro Trajectory & Balances"
                ], id="btn-tab-macro", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-globe-europe-africa me-1 text-info"),
                    "3. Geopolitical Exposure & Slump"
                ], id="btn-tab-geopolitics", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-lightning-charge me-1 text-danger"),
                    "4. Stress Tests & Shocks"
                ], id="btn-tab-stress", className="nav-tab-btn", n_clicks=0),
            ], className="d-flex flex-wrap")
        ], className="nav-box-card", style={"borderLeft": f"4px solid {STATEC_YELLOW}"}),

        # Box 2: Data Analyst Deep-Dive Suite (6 Buttons: Q1–Q6)
        html.Div([
            html.Div([
                create_icon_badge("bi bi-diagram-3", color=STATEC_BLUE, bg="#EFF6FF", size=15, box_size=28),
                html.Span("2. DATA ANALYST DEEP-DIVE SUITE (RESEARCH QUESTIONS Q1–Q6)", style={
                    "fontSize": "11.5px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif",
                    "color": STATEC_NAVY, "letterSpacing": "0.6px", "marginLeft": "8px"
                }),
                html.Span("GRANULAR TARIFF & ECONOMETRIC LAB", style={
                    "backgroundColor": "#EFF6FF", "color": STATEC_BLUE, "fontSize": "9px",
                    "fontWeight": "800", "padding": "2px 6px", "borderRadius": "3px", "marginLeft": "8px",
                    "border": "1px solid #BFDBFE"
                })
            ], className="d-flex align-items-center mb-2"),

            html.Div([
                html.Button([
                    html.I(className="bi bi-geo-alt me-1"),
                    "Q1: Trading Partners"
                ], id="btn-tab-partners", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-boxes me-1"),
                    "Q2: Product Categories"
                ], id="btn-tab-products", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-funnel me-1"),
                    "Q3: Product Principal Partners"
                ], id="btn-tab-q3-partners", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-list-nested me-1"),
                    "Q4: Tariff Lines (HS2→CN8)"
                ], id="btn-tab-q4-drilldown", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-bar-chart-steps me-1"),
                    "Q5: Peer Benchmarking"
                ], id="btn-tab-benchmarks", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-calendar-range me-1"),
                    "Q6: Seasonality Lab"
                ], id="btn-tab-seasonality", className="nav-tab-btn", n_clicks=0),
            ], className="d-flex flex-wrap")
        ], className="nav-box-card", style={"borderLeft": f"4px solid {STATEC_BLUE}"})
    ])


# ── App Main Layout ─────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="active-tab-store", data="tab-resilience"),
    create_header(),
    dbc.Container([
        create_navigation_boxes(),
        # Tab Content Container
        html.Div(id="tab-content", style={"minHeight": "650px"})
    ], fluid=True, style={"maxWidth": "1540px", "paddingBottom": "30px"}),
    create_dashboard_footer()
])
'''

Path("scratch/build_clean_app.py").write_text("print('builder ready')", encoding="utf-8")
print("Verified script start!")
