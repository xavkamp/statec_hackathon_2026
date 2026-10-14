"""Interactive Dash Application for STATEC Hackathon 2026.
Luxembourg External Trade Intelligence (2000-2026).
Eurostat Dataset: ds-045409
Pure Tabular CSV Pipeline.
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
    CATEGORICAL, PLOT_LAYOUT, CARD_STYLE, KPI_CARD_STYLE, apply_plot_theme,
    add_iso3_column, ISO2_TO_ISO3
)
from src.dashboard.data_loader import (
    load_overview_kpis, load_partner_rankings, load_product_rankings,
    load_hs4_product_rankings, load_product_partners, load_seasonal_decomposition,
    load_country_benchmarks, load_drilldown_lvl2, load_drilldown_lvl4, load_drilldown_lvl8
)


# Initialize Dash App
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    ],
    title="Luxembourg Trade Intelligence (2000-2026) — STATEC",
    suppress_callback_exceptions=True
)
server = app.server

# ── Helper formatters ────────────────────────────────────────────────────────
def fmt_eur(val: float) -> str:
    """Format euro value in Millions or Billions."""
    if pd.isna(val) or val is None:
        return "—"
    abs_v = abs(val)
    sign = "-" if val < 0 else ""
    if abs_v >= 1e9:
        return f"{sign}€{abs_v/1e9:.2f}B"
    elif abs_v >= 1e6:
        return f"{sign}€{abs_v/1e6:.1f}M"
    else:
        return f"{sign}€{abs_v:,.0f}"


def get_concentration_badge(hhi: float):
    """Return colored badge for Herfindahl-Hirschman Index concentration."""
    if pd.isna(hhi):
        return html.Span("N/A", className="badge bg-secondary")
    if hhi >= 2500:
        return html.Span(f"HHI {hhi:.0f} • High Concentration", style={
            "backgroundColor": "#FEE2E2", "color": "#B91C1C", "padding": "4px 10px",
            "borderRadius": "20px", "fontWeight": "600", "fontSize": "11px", "border": "1px solid #FCA5A5"
        })
    elif hhi >= 1500:
        return html.Span(f"HHI {hhi:.0f} • Moderate Concentration", style={
            "backgroundColor": "#FEF3C7", "color": "#B45309", "padding": "4px 10px",
            "borderRadius": "20px", "fontWeight": "600", "fontSize": "11px", "border": "1px solid #FCD34D"
        })
    else:
        return html.Span(f"HHI {hhi:.0f} • Diversified", style={
            "backgroundColor": "#D1FAE5", "color": "#047857", "padding": "4px 10px",
            "borderRadius": "20px", "fontWeight": "600", "fontSize": "11px", "border": "1px solid #6EE7B7"
        })


# ── Header & KPI Ribbon Layout ──────────────────────────────────────────────
def create_header():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("STATEC", style={
                            "backgroundColor": "#0284C7", "color": "white", "padding": "5px 10px",
                            "borderRadius": "6px", "fontWeight": "800", "fontSize": "13px",
                            "marginRight": "12px", "letterSpacing": "1.5px"
                        }),
                        html.Span("LUXEMBOURG EXTERNAL TRADE INTELLIGENCE", style={
                            "fontSize": "19px", "fontWeight": "800", "color": TEXT_PRIMARY, "letterSpacing": "0.3px"
                        }),
                    ], className="d-flex align-items-center mb-1"),
                    html.P(
                        "Eurostat Comext [ds-045409] • Multi-dimensional Merchandise Trade in Goods (2000–2026)",
                        className="text-muted mb-0", style={"fontSize": "13px"}
                    )
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.Label("Analysis Year:", style={
                            "fontSize": "12px", "fontWeight": "700", "color": TEXT_MUTED, "marginBottom": "4px"
                        }),
                        dcc.Dropdown(
                            id="global-year-dropdown",
                            options=[{"label": str(y), "value": y} for y in range(2025, 1999, -1)],
                            value=2024,
                            clearable=False,
                            style={"fontSize": "13px", "borderRadius": "8px", "minWidth": "110px"}
                        )
                    ], className="d-flex flex-column align-items-end")
                ], md=4, className="d-flex justify-content-end align-items-center")
            ], className="w-100 align-items-center")
        ], fluid=True),
        color="white",
        className="border-bottom py-3 shadow-sm",
        style={"marginBottom": "24px"}
    )


def create_kpi_ribbon():
    return html.Div(id="kpi-ribbon-container", className="mb-4")


# ── Audience Mode Selector ──────────────────────────────────────────────────
def create_audience_mode_selector():
    return dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div([
                                html.Span("🏛️", style={"fontSize": "26px", "marginRight": "14px"}),
                                html.Div([
                                    html.Div([
                                        html.Strong("NATIONAL LEADERSHIP BRIEFING", style={"fontSize": "15px", "color": TEXT_PRIMARY, "letterSpacing": "0.3px"}),
                                        html.Span("EXECUTIVE • PRIORITY OVERVIEW", className="badge bg-primary ms-2", style={"fontSize": "10px", "fontWeight": "700", "verticalAlign": "middle"})
                                    ], className="d-flex align-items-center"),
                                    html.P(
                                        "Answers Pressing Questions First: Sovereign economic resilience, critical supply chain bottlenecks, and macro health.",
                                        className="text-muted mb-0", style={"fontSize": "12px", "marginTop": "2px"}
                                    )
                                ])
                            ], className="d-flex align-items-center"),
                        ], id="btn-mode-leaders", n_clicks=0, style={
                            "cursor": "pointer", "padding": "16px 20px", "borderRadius": "12px",
                            "border": f"2px solid {PRIMARY}", "backgroundColor": "#F0F9FF",
                            "transition": "all 0.2s ease-in-out", "boxShadow": "0 2px 6px rgba(2, 132, 199, 0.12)"
                        })
                    ], md=6, className="mb-2 mb-md-0"),

                    dbc.Col([
                        html.Div([
                            html.Div([
                                html.Span("🔬", style={"fontSize": "26px", "marginRight": "14px"}),
                                html.Div([
                                    html.Div([
                                        html.Strong("DATA ANALYST DEEP-DIVE SUITE", style={"fontSize": "15px", "color": TEXT_PRIMARY, "letterSpacing": "0.3px"}),
                                        html.Span("ADVANCED DRILL-DOWN", className="badge bg-secondary ms-2", style={"fontSize": "10px", "fontWeight": "700", "verticalAlign": "middle"})
                                    ], className="d-flex align-items-center"),
                                    html.P(
                                        "Explore Details Afterwards: Granular tariff lines (HS2→CN8), full world maps, seasonal modeling & peer benchmarks.",
                                        className="text-muted mb-0", style={"fontSize": "12px", "marginTop": "2px"}
                                    )
                                ])
                            ], className="d-flex align-items-center"),
                        ], id="btn-mode-analysts", n_clicks=0, style={
                            "cursor": "pointer", "padding": "16px 20px", "borderRadius": "12px",
                            "border": f"1px solid {BORDER}", "backgroundColor": SURFACE,
                            "transition": "all 0.2s ease-in-out"
                        })
                    ], md=6),
                ])
            ], style=CARD_STYLE, className="py-3 px-3 mb-3")
        ], md=12)
    ])


# ── App Main Layout ─────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="current-audience-mode", data="leaders"),
    dcc.Store(id="active-tab-store", data="tab-resilience"),
    create_header(),
    dbc.Container([
        create_kpi_ribbon(),
        create_audience_mode_selector(),

        # Dynamic Sub-tabs container based on audience
        html.Div(id="sub-tabs-container", className="mb-4"),

        # Tab Content Container
        html.Div(id="tab-content", style={"minHeight": "650px"})
    ], fluid=True, style={"maxWidth": "1540px", "paddingBottom": "60px"})
], style={"backgroundColor": BACKGROUND, "minHeight": "100vh", "fontFamily": "'Inter', -apple-system, sans-serif"})


# ── KPI Ribbon Callback ────────────────────────────────────────────────────
@callback(
    Output("kpi-ribbon-container", "children"),
    Input("global-year-dropdown", "value")
)
def update_kpis(selected_year):
    kpis_df = load_overview_kpis()
    if kpis_df.empty:
        return html.Div()

    row = kpis_df[kpis_df["year"] == selected_year]
    if row.empty:
        row = kpis_df.iloc[-1]
    else:
        row = row.iloc[0]

    exp_val = row.get("EXPORT", 0)
    imp_val = row.get("IMPORT", 0)
    bal_val = row.get("trade_balance_eur", 0)
    cov_val = row.get("coverage_ratio_pct", 0)
    intra_eu_exp = row.get("intra_eu_export_share_pct", np.nan)
    intra_eu_imp = row.get("intra_eu_import_share_pct", np.nan)

    exp_yoy = row.get("export_yoy_growth_pct", 0)
    imp_yoy = row.get("import_yoy_growth_pct", 0)

    def render_badge(val, is_pct=True):
        if pd.isna(val):
            return ""
        color = SUCCESS if val >= 0 else DANGER
        icon = "▲" if val >= 0 else "▼"
        suffix = "%" if is_pct else ""
        return html.Span(
            f"{icon} {abs(val):.1f}{suffix} YoY",
            style={"color": color, "fontSize": "12px", "fontWeight": "700", "marginLeft": "8px"}
        )

    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("TOTAL MERCHANDISE EXPORTS", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.Div([
                    html.H3(fmt_eur(exp_val), style={"fontWeight": "800", "color": PRIMARY, "margin": "4px 0 0 0"}),
                    render_badge(exp_yoy)
                ], className="d-flex align-items-baseline"),
                html.Small(f"Intra-EU Share: {intra_eu_exp:.1f}%" if not pd.isna(intra_eu_exp) else "Physical goods exports", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),

        dbc.Col([
            html.Div([
                html.Span("TOTAL MERCHANDISE IMPORTS", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.Div([
                    html.H3(fmt_eur(imp_val), style={"fontWeight": "800", "color": SECONDARY, "margin": "4px 0 0 0"}),
                    render_badge(imp_yoy)
                ], className="d-flex align-items-baseline"),
                html.Small(f"Intra-EU Share: {intra_eu_imp:.1f}%" if not pd.isna(intra_eu_imp) else "Physical goods imports", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),

        dbc.Col([
            html.Div([
                html.Span("MERCHANDISE TRADE BALANCE", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.H3(fmt_eur(bal_val), style={"fontWeight": "800", "color": DANGER if bal_val < 0 else SUCCESS, "margin": "4px 0 0 0"}),
                html.Small("Structural physical goods deficit" if bal_val < 0 else "Trade surplus", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),

        dbc.Col([
            html.Div([
                html.Span("EXPORT COVERAGE RATIO", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.H3(f"{cov_val:.1f}%", style={"fontWeight": "800", "color": TEXT_PRIMARY, "margin": "4px 0 0 0"}),
                html.Small(f"Goods exports fund {cov_val:.0f}c per €1 imported", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),
    ])


# ── Audience Switcher Callback ─────────────────────────────────────────────
@callback(
    Output("current-audience-mode", "data"),
    Output("btn-mode-leaders", "style"),
    Output("btn-mode-analysts", "style"),
    Input("btn-mode-leaders", "n_clicks"),
    Input("btn-mode-analysts", "n_clicks"),
    State("current-audience-mode", "data"),
    prevent_initial_call=True
)
def switch_audience_mode(n_lead, n_ana, current_mode):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_mode, dash.no_update, dash.no_update
    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    new_mode = "leaders" if btn_id == "btn-mode-leaders" else "analysts"

    active_lead_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "12px",
        "border": f"2px solid {PRIMARY}", "backgroundColor": "#F0F9FF",
        "transition": "all 0.2s ease-in-out", "boxShadow": "0 2px 6px rgba(2, 132, 199, 0.12)"
    }
    inactive_lead_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "12px",
        "border": f"1px solid {BORDER}", "backgroundColor": SURFACE,
        "transition": "all 0.2s ease-in-out"
    }

    active_ana_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "12px",
        "border": f"2px solid {SECONDARY}", "backgroundColor": "#EEF2FF",
        "transition": "all 0.2s ease-in-out", "boxShadow": "0 2px 6px rgba(79, 70, 229, 0.12)"
    }
    inactive_ana_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "12px",
        "border": f"1px solid {BORDER}", "backgroundColor": SURFACE,
        "transition": "all 0.2s ease-in-out"
    }

    if new_mode == "leaders":
        return "leaders", active_lead_style, inactive_ana_style
    else:
        return "analysts", inactive_lead_style, active_ana_style


# ── Sub-tabs Render Callback ───────────────────────────────────────────────
@callback(
    Output("sub-tabs-container", "children"),
    Input("current-audience-mode", "data"),
    Input("active-tab-store", "data")
)
def render_sub_tabs(mode, active_tab_store):
    if mode == "leaders":
        default_tab = active_tab_store if active_tab_store in ["tab-resilience", "tab-macro", "tab-geopolitics"] else "tab-resilience"
        return dbc.Tabs(id="sub-tabs", active_tab=default_tab, children=[
            dbc.Tab(label="🛡️ 1. Sovereign Supply Chain & Resilience Radar", tab_id="tab-resilience", label_style={"fontWeight": "700", "fontSize": "13px", "color": "#B45309"}),
            dbc.Tab(label="💶 2. Macroeconomic Health & Sovereignty", tab_id="tab-macro", label_style={"fontWeight": "600", "fontSize": "13px"}),
            dbc.Tab(label="🌍 3. Geopolitical Exposure & Seasonal Shocks", tab_id="tab-geopolitics", label_style={"fontWeight": "600", "fontSize": "13px"}),
        ])
    else:
        default_tab = active_tab_store if active_tab_store in ["tab-partners", "tab-products", "tab-drilldown", "tab-seasonality", "tab-benchmarks"] else "tab-partners"
        return dbc.Tabs(id="sub-tabs", active_tab=default_tab, children=[
            dbc.Tab(label="🌐 1. Trading Partners (Q1)", tab_id="tab-partners", label_style={"fontWeight": "600", "fontSize": "13px"}),
            dbc.Tab(label="📦 2. Product Categories & Shift (Q2)", tab_id="tab-products", label_style={"fontWeight": "600", "fontSize": "13px"}),
            dbc.Tab(label="🔍 3. Hierarchical Flow Drill-Down HS2→CN8 (Q3 & Q4)", tab_id="tab-drilldown", label_style={"fontWeight": "600", "fontSize": "13px"}),
            dbc.Tab(label="📈 4. Seasonality & Trend Lab (Q6)", tab_id="tab-seasonality", label_style={"fontWeight": "600", "fontSize": "13px"}),
            dbc.Tab(label="📊 5. Regional Peer Benchmarks (Q5)", tab_id="tab-benchmarks", label_style={"fontWeight": "600", "fontSize": "13px"}),
        ])


# ── Tab Content Router Callback ────────────────────────────────────────────
@callback(
    Output("tab-content", "children"),
    Input("sub-tabs", "active_tab"),
    Input("global-year-dropdown", "value")
)
def render_tab_content(active_tab, selected_year):
    if active_tab == "tab-resilience":
        return render_tab_resilience(selected_year)
    elif active_tab == "tab-macro" or active_tab == "tab-overview":
        return render_tab_overview()
    elif active_tab == "tab-geopolitics":
        return render_tab_geopolitics(selected_year)
    elif active_tab == "tab-partners":
        return render_tab_partners(selected_year)
    elif active_tab == "tab-products":
        return render_tab_products(selected_year)
    elif active_tab == "tab-drilldown":
        return render_tab_drilldown(selected_year)
    elif active_tab == "tab-benchmarks":
        return render_tab_benchmarks(selected_year)
    elif active_tab == "tab-seasonality":
        return render_tab_seasonality()
    return html.Div("Loading perspective...")


# ───────────────────────────────────────────────────────────────────────────
# TAB 1: MACRO OVERVIEW
# ───────────────────────────────────────────────────────────────────────────
def render_tab_overview():
    kpis_df = load_overview_kpis()
    if kpis_df.empty:
        return html.Div("Overview data not available.")

    # 1. Trajectory chart
    fig_trajectory = go.Figure()
    fig_trajectory.add_trace(go.Scatter(
        x=kpis_df["year"], y=kpis_df["EXPORT"] / 1e9,
        name="Exports", mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=6),
        hovertemplate="Exports: €%{y:.2f}B (%{x})<extra></extra>"
    ))
    fig_trajectory.add_trace(go.Scatter(
        x=kpis_df["year"], y=kpis_df["IMPORT"] / 1e9,
        name="Imports", mode="lines+markers",
        line=dict(color=SECONDARY, width=3),
        marker=dict(size=6),
        hovertemplate="Imports: €%{y:.2f}B (%{x})<extra></extra>"
    ))
    apply_plot_theme(fig_trajectory, title="Evolution of Luxembourg Merchandise Trade Flows (2000–2026)", y_title="Billion Euros (€B)", dtick_x=2, hovermode="x unified")

    # 2. Balance Bar Chart
    colors = [SUCCESS if v >= 0 else DANGER for v in kpis_df["trade_balance_eur"]]
    fig_balance = go.Figure(go.Bar(
        x=kpis_df["year"], y=kpis_df["trade_balance_eur"] / 1e9,
        marker_color=colors,
        hovertemplate="Trade Balance %{x}: €%{y:.2f}B<extra></extra>"
    ))
    apply_plot_theme(fig_balance, title="Annual Merchandise Trade Balance (Deficit / Surplus)", y_title="Billion Euros (€B)", dtick_x=2)

    # 3. European Integration Share
    fig_eu = go.Figure()
    if "intra_eu_export_share_pct" in kpis_df.columns:
        fig_eu.add_trace(go.Scatter(
            x=kpis_df["year"], y=kpis_df["intra_eu_export_share_pct"],
            name="Intra-EU Export Share %", line=dict(color=PRIMARY, width=2.5), mode="lines+markers"
        ))
        fig_eu.add_trace(go.Scatter(
            x=kpis_df["year"], y=kpis_df["intra_eu_import_share_pct"],
            name="Intra-EU Import Share %", line=dict(color=SECONDARY, width=2.5), mode="lines+markers"
        ))
    apply_plot_theme(fig_eu, title="European Integration: Share of Trade with EU Partners (%)", y_title="Share of Total (%)", dtick_x=2)
    fig_eu.update_yaxes(range=[55, 95])

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_trajectory, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=8),
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_balance, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=4),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_eu, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=12)
        ]),
        html.Div([
            html.H6("Key Macro Insights (2000–2026)", style={"fontWeight": "700", "color": TEXT_PRIMARY}),
            html.Ul([
                html.Li("Trade Growth: Luxembourg's merchandise trade expanded from €9.1B exports / €12.2B imports in 2000 to over €16.5B exports / €25.7B imports by recent peaks (volume expanded by ~89%)."),
                html.Li("Structural Deficit: Physical merchandise exhibits an annual deficit between €7B and €9.2B, typical for highly specialized financial and services hubs whose massive service surpluses offset goods deficits."),
                html.Li("Intense Regional Integration: 80% to 90% of Luxembourg's external trade in goods is conducted with European Union partners, with direct neighbors (Belgium, Germany, France) forming the undisputed bedrock."),
            ], style={"fontSize": "13px", "color": TEXT_MUTED, "marginBottom": "0"})
        ], style={**CARD_STYLE, "backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}"})
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 3: GEOPOLITICAL EXPOSURE & SEASONAL SHOCKS (Leadership Pillar)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_geopolitics(selected_year):
    partners_df = load_partner_rankings()
    if partners_df.empty:
        return html.Div("Geopolitical data not available.")

    sub = partners_df[(partners_df["year"] == selected_year) & (partners_df["flow"] == "IMPORT")].copy()
    if sub.empty:
        sub = partners_df[(partners_df["year"] == partners_df["year"].max()) & (partners_df["flow"] == "IMPORT")].copy()

    eu_codes = {'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'}
    neighbors = {'BE', 'DE', 'FR'}
    tot_imp = sub['value_eur'].sum()
    neigh_val = sub[sub['partner_code'].isin(neighbors)]['value_eur'].sum()
    other_eu_val = sub[sub['partner_code'].isin(eu_codes - neighbors)]['value_eur'].sum()
    row_val = max(0, tot_imp - (neigh_val + other_eu_val))

    # 1. Donut Chart of Regional Import Exposure
    fig_donut = go.Figure(go.Pie(
        labels=["Direct Neighbors (BE, DE, FR)", "Other EU Member States", "Rest of World (US, CN, GB, etc.)"],
        values=[neigh_val, other_eu_val, row_val],
        hole=0.55,
        marker_colors=[PRIMARY, "#38BDF8", "#94A3B8"],
        textinfo="label+percent",
        hovertemplate="%{label}<br>Value: €%{value:,.0f}<br>Share: %{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRIMARY),
        showlegend=False
    )

    # 2. Top Non-EU Strategic Partners Bar Chart
    non_eu_sub = sub[~sub['partner_code'].isin(eu_codes)].sort_values('value_eur', ascending=False).head(8)
    fig_non_eu = go.Figure(go.Bar(
        x=non_eu_sub['value_eur'] / 1e6,
        y=non_eu_sub['partner_name'],
        orientation='h',
        marker_color="#8B5CF6",
        text=non_eu_sub['market_share_pct'].apply(lambda p: f"{p:.2f}%"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.1f}M (%{text} of all imports)<extra></extra>"
    ))
    apply_plot_theme(fig_non_eu, title="Top Non-EU Strategic Suppliers (Third-Country Exposure)", x_title="Million Euros (€M)")
    fig_non_eu.update_layout(margin=dict(l=10, r=40, t=35, b=30), yaxis=dict(autorange="reversed"))

    # 3. Seasonal timeline chart for leadership (August slump highlight)
    sea_df = load_seasonal_decomposition()
    sea_tot = sea_df[(sea_df["product_code"] == "TOTAL") & (sea_df["flow"] == "IMPORT")].sort_values("date").copy()
    fig_aug = go.Figure()
    if not sea_tot.empty:
        factors = sea_tot.groupby("month")["seasonal_factor"].first().reset_index()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        factors["month_name"] = factors["month"].apply(lambda m: months[m - 1])
        colors = [DANGER if m == 8 else (SUCCESS if f > 1.05 else PRIMARY) for m, f in zip(factors["month"], factors["seasonal_factor"])]
        fig_aug = go.Figure(go.Bar(
            x=factors["month_name"],
            y=(factors["seasonal_factor"] - 1.0) * 100,
            marker_color=colors,
            text=factors["seasonal_factor"].apply(lambda f: f"{(f - 1.0)*100:+.1f}%"),
            textposition="outside",
            hovertemplate="Month %{x}: %{y:+.1f}% vs Annual Average<extra></extra>"
        ))
        fig_aug.add_hline(y=0, line_dash="solid", line_color=NEUTRAL)
        apply_plot_theme(fig_aug, title="Cyclical Seasonality Shock: Deviation from Annual Trend (%)", y_title="% Deviation from Annual Trend")
        fig_aug.update_yaxes(range=[-20, 15])

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Geopolitical Exposure & Seasonal Supply Chain Shocks", style={"fontWeight": "800", "color": TEXT_PRIMARY}),
                    html.P(
                        "Analyzing Luxembourg's geographic concentration across immediate neighbors, third-country dependencies (US, China, UK), and annual cyclical supply slumps.",
                        className="text-muted", style={"fontSize": "13px"}
                    )
                ], className="mb-3")
            ], md=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Merchandise Import Concentration: Regional Breakdown", style={"fontWeight": "700"}),
                    html.P(f"In {selected_year}, over 73% of physical goods imports came from Belgium, Germany, and France.", className="text-muted", style={"fontSize": "12px"}),
                    dcc.Graph(figure=fig_donut, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=6),
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_non_eu, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_aug, config={"displayModeBar": False}),
                    html.Div([
                        html.Strong("Operational Warning for Leadership: ", style={"color": DANGER, "fontSize": "12px"}),
                        html.Span(
                            "The sharp -14.4% trade contraction every August is driven by industrial shutdowns and Luxembourg's 'congé collectif'. Critical supply stockpiles (especially hospital pharmaceuticals, construction materials, and winter fuels) must be buffered in June/July prior to the annual August dip.",
                            style={"fontSize": "12px", "color": TEXT_MUTED}
                        )
                    ], className="mt-2 p-2 rounded", style={"backgroundColor": "#FEF2F2", "border": "1px solid #FEE2E2"})
                ], style=CARD_STYLE)
            ], md=12)
        ])
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 1 (ANALYST): TRADING PARTNERS (Q1)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_partners(selected_year):
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Trade Flow Direction:", style={"fontWeight": "700", "fontSize": "12px", "color": TEXT_MUTED}),
                            dbc.RadioItems(
                                id="partner-flow-radio",
                                options=[
                                    {"label": "Exports (Destinations)", "value": "EXPORT"},
                                    {"label": "Imports (Suppliers)", "value": "IMPORT"},
                                ],
                                value="EXPORT",
                                inline=True,
                                style={"fontSize": "13px"}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Map Scope (Zoom):", style={"fontWeight": "700", "fontSize": "12px", "color": TEXT_MUTED}),
                            dbc.RadioItems(
                                id="partner-map-scope",
                                options=[
                                    {"label": "🇪🇺 Europe", "value": "europe"},
                                    {"label": "🌍 World", "value": "world"},
                                    {"label": "🌎 Americas", "value": "north america"},
                                    {"label": "🌏 Asia", "value": "asia"},
                                ],
                                value="europe",
                                inline=True,
                                style={"fontSize": "13px"}
                            )
                        ], md=5),
                        dbc.Col([
                            html.Label("Color Metric:", style={"fontWeight": "700", "fontSize": "12px", "color": TEXT_MUTED}),
                            dbc.RadioItems(
                                id="partner-map-metric",
                                options=[
                                    {"label": "Value (€)", "value": "value_eur"},
                                    {"label": "Share (%)", "value": "market_share_pct"},
                                ],
                                value="value_eur",
                                inline=True,
                                style={"fontSize": "13px"}
                            )
                        ], md=3),
                    ], className="mb-2 align-items-center"),

                    dcc.Graph(
                        id="partner-map-graph",
                        config={"displayModeBar": True, "scrollZoom": True},
                        style={"height": "420px"}
                    ),

                    # Interactive Country Spotlight on Map Click
                    html.Div(id="partner-click-spotlight", className="mt-2")
                ], style=CARD_STYLE)
            ], md=8),
            dbc.Col([
                html.Div([
                    html.H6(id="partner-top10-title", style={"fontWeight": "700", "marginBottom": "12px"}),
                    dcc.Graph(id="partner-top10-graph", config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=4),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Historical Partner Share Evolution (2000–2026)", style={"fontWeight": "700", "marginBottom": "4px"}),
                    html.P("Tracking structural market share shifts among Luxembourg's top trading partners over 25 years. Click any country on the map to highlight its trend line.", className="text-muted", style={"fontSize": "12px"}),
                    dcc.Graph(id="partner-history-graph", config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=12)
        ])
    ])


@callback(
    Output("partner-map-graph", "figure"),
    Output("partner-top10-title", "children"),
    Output("partner-top10-graph", "figure"),
    Output("partner-history-graph", "figure"),
    Input("partner-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    Input("partner-map-scope", "value"),
    Input("partner-map-metric", "value"),
    Input("partner-map-graph", "clickData")
)
def update_partner_tab(flow, year, scope, metric, click_data):
    partners_df = load_partner_rankings()
    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].copy()
    if sub.empty:
        # Fallback to latest available year
        avail_years = partners_df["year"].unique()
        if len(avail_years) > 0:
            sub = partners_df[(partners_df["year"] == max(avail_years)) & (partners_df["flow"] == flow)].copy()

    # Determine clicked partner
    clicked_code = None
    if click_data and "points" in click_data and click_data["points"]:
        pt = click_data["points"][0]
        if "customdata" in pt and pt["customdata"]:
            clicked_code = pt["customdata"][0]
        elif "location" in pt:
            for c2, c3 in ISO2_TO_ISO3.items():
                if c3 == pt["location"]:
                    clicked_code = c2
                    break

    # 1. World/Europe Choropleth Map with ISO3 mapping
    sub = add_iso3_column(sub)
    sub_valid = sub.dropna(subset=["iso3"]).copy()

    metric_col = metric if metric in sub_valid.columns else "value_eur"
    color_title = "Value (€)" if metric_col == "value_eur" else "Share (%)"

    fig_map = px.choropleth(
        sub_valid,
        locations="iso3",
        color=metric_col,
        hover_name="partner_name",
        custom_data=["partner_code", "partner_name", "value_eur", "market_share_pct", "rank"],
        color_continuous_scale="Blues" if flow == "EXPORT" else "Purples",
        projection="natural earth" if scope == "world" else "mercator"
    )
    fig_map.update_traces(
        hovertemplate="<b>%{customdata[1]}</b> (%{customdata[0]})<br>" +
                      f"{flow.capitalize()}: €%{{customdata[2]:,.0f}}<br>" +
                      "Market Share: %{customdata[3]:.2f}%<br>" +
                      "National Rank: #%{customdata[4]}<br>" +
                      "<i>💡 Click country to inspect bilateral flows</i><extra></extra>"
    )
    fig_map.update_geos(
        showcoastlines=True, coastlinecolor="#CBD5E1",
        showland=True, landcolor="#F8FAFC",
        showocean=True, oceancolor="#F1F5F9",
        showcountries=True, countrycolor="#E2E8F0",
        scope=scope if scope else "europe"
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(title=color_title, len=0.6, thickness=12, y=0.5),
        clickmode="event+select"
    )

    # 2. Top 10 Partners
    top10 = sub.sort_values("rank").head(10).copy()
    top10 = top10.sort_values("value_eur", ascending=True)

    bar_colors = []
    for c in top10["partner_code"]:
        if clicked_code and c == clicked_code:
            bar_colors.append(WARNING)  # Highlight clicked country
        else:
            bar_colors.append(PRIMARY if flow == "EXPORT" else SECONDARY)

    fig_top10 = go.Figure(go.Bar(
        x=top10["value_eur"] / 1e9,
        y=top10["partner_name"],
        orientation="h",
        marker_color=bar_colors,
        text=top10["market_share_pct"].apply(lambda p: f"{p:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.2f}B (%{text})<extra></extra>"
    ))
    apply_plot_theme(fig_top10, x_title="Billion Euros (€B)")
    fig_top10.update_layout(margin=dict(l=10, r=40, t=10, b=30), yaxis=dict(autorange="reversed"))

    # 3. Evolution over time
    top_codes = ["DE", "BE", "FR", "NL", "IT", "US", "GB", "CN"]
    if clicked_code and clicked_code not in top_codes:
        top_codes.append(clicked_code)

    hist_sub = partners_df[(partners_df["partner_code"].isin(top_codes)) & (partners_df["flow"] == flow)].copy()

    fig_hist = go.Figure()
    for i, code in enumerate(top_codes):
        p_data = hist_sub[hist_sub["partner_code"] == code].sort_values("year")
        if not p_data.empty:
            p_name = p_data["partner_name"].iloc[0]
            is_clicked = (code == clicked_code)
            line_width = 4.5 if is_clicked else 2.5
            fig_hist.add_trace(go.Scatter(
                x=p_data["year"], y=p_data["market_share_pct"],
                name=f"{'⭐ ' if is_clicked else ''}{p_name} ({code})",
                mode="lines+markers",
                line=dict(color=WARNING if is_clicked else CATEGORICAL[i % len(CATEGORICAL)], width=line_width),
                marker=dict(size=8 if is_clicked else 5),
                hovertemplate=f"{p_name}: %{{y:.1f}}% in %{{x}}<extra></extra>"
            ))
    apply_plot_theme(fig_hist, x_title="Year", y_title="Share of Total Trade (%)", dtick_x=2, hovermode="x unified")

    top10_title = f"Top 10 {flow.capitalize()} Partners ({year})"
    return fig_map, top10_title, fig_top10, fig_hist


# Callback for Click Spotlight on Map
@callback(
    Output("partner-click-spotlight", "children"),
    Input("partner-map-graph", "clickData"),
    Input("partner-flow-radio", "value"),
    Input("global-year-dropdown", "value")
)
def update_partner_click_spotlight(click_data, flow, year):
    partners_df = load_partner_rankings()
    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].copy()
    if sub.empty:
        sub = partners_df[(partners_df["year"] == partners_df["year"].max()) & (partners_df["flow"] == flow)].copy()

    selected_code = None
    if click_data and "points" in click_data and click_data["points"]:
        pt = click_data["points"][0]
        if "customdata" in pt and pt["customdata"]:
            selected_code = pt["customdata"][0]
        elif "location" in pt:
            for c2, c3 in ISO2_TO_ISO3.items():
                if c3 == pt["location"]:
                    selected_code = c2
                    break

    is_custom_click = bool(selected_code and not sub[sub["partner_code"] == selected_code].empty)
    if not is_custom_click:
        top_row = sub.sort_values("rank").iloc[0]
        selected_code = top_row["partner_code"]

    partner_row = sub[sub["partner_code"] == selected_code].iloc[0]
    p_name = partner_row["partner_name"]
    p_val = partner_row["value_eur"]
    p_share = partner_row["market_share_pct"]
    p_rank = int(partner_row["rank"])

    return html.Div([
        html.Div([
            html.Div([
                html.Span(
                    "📍 SELECTED PARTNER ON MAP:" if is_custom_click else "📍 LEAD PARTNER (CLICK ANY COUNTRY ON MAP TO INSPECT):",
                    style={"fontSize": "11px", "fontWeight": "800", "color": TEXT_MUTED, "letterSpacing": "0.5px"}
                ),
                html.H5(f"{p_name} ({selected_code})", style={"fontWeight": "800", "color": PRIMARY if flow == 'EXPORT' else SECONDARY, "margin": "2px 0 0 0"}),
            ]),
            html.Div([
                html.Div([
                    html.Span("FLOW VALUE", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_MUTED}),
                    html.H6(fmt_eur(p_val), style={"fontWeight": "800", "margin": "0", "color": TEXT_PRIMARY})
                ], className="me-4 text-center"),
                html.Div([
                    html.Span("MARKET SHARE", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_MUTED}),
                    html.H6(f"{p_share:.2f}%", style={"fontWeight": "800", "margin": "0", "color": TEXT_PRIMARY})
                ], className="me-4 text-center"),
                html.Div([
                    html.Span("NATIONAL RANK", style={"fontSize": "10px", "fontWeight": "700", "color": TEXT_MUTED}),
                    html.H6(f"#{p_rank}", style={"fontWeight": "800", "margin": "0", "color": PRIMARY if p_rank <= 3 else TEXT_PRIMARY})
                ], className="me-2 text-center"),
            ], className="d-flex align-items-center ms-auto flex-wrap")
        ], className="d-flex align-items-center justify-content-between flex-wrap p-2 px-3 rounded", style={"backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}"})
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 3: PRODUCT CATEGORIES (Q2)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_products(selected_year):
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Label("Trade Flow Direction:", style={"fontWeight": "700", "fontSize": "13px", "marginRight": "14px"}),
                        dbc.RadioItems(
                            id="prod-flow-radio",
                            options=[
                                {"label": "Exports", "value": "EXPORT"},
                                {"label": "Imports", "value": "IMPORT"},
                            ],
                            value="EXPORT",
                            inline=True,
                            style={"fontSize": "13px", "marginRight": "24px"}
                        ),
                        html.Label("Granularity:", style={"fontWeight": "700", "fontSize": "13px", "marginRight": "14px"}),
                        dbc.RadioItems(
                            id="prod-granularity-radio",
                            options=[
                                {"label": "2-Digit (HS2 Chapters)", "value": 2},
                                {"label": "4-Digit (HS4 Subheadings)", "value": 4},
                            ],
                            value=2,
                            inline=True,
                            style={"fontSize": "13px"}
                        )
                    ], className="d-flex align-items-center mb-3 flex-wrap"),
                    html.H6(id="prod-treemap-title", style={"fontWeight": "700"}),
                    dcc.Graph(id="prod-treemap-graph", config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=7),
            dbc.Col([
                html.Div([
                    html.H6(id="prod-top10-title", style={"fontWeight": "700", "marginBottom": "12px"}),
                    dcc.Graph(id="prod-top10-graph", config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=5),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(id="prod-shift-title", style={"fontWeight": "700", "marginBottom": "4px"}),
                    html.P("Evolution of key product lines: Tracking long-term structural changes across Luxembourg's manufacturing and merchandise trade.", className="text-muted", style={"fontSize": "12px"}),
                    dcc.Graph(id="prod-shift-graph", config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=12)
        ])
    ])


@callback(
    Output("prod-treemap-title", "children"),
    Output("prod-treemap-graph", "figure"),
    Output("prod-top10-title", "children"),
    Output("prod-top10-graph", "figure"),
    Output("prod-shift-title", "children"),
    Output("prod-shift-graph", "figure"),
    Input("prod-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    Input("prod-granularity-radio", "value")
)
def update_product_tab(flow, year, granularity):
    if granularity == 4:
        hs4_df = load_hs4_product_rankings()
        sub = hs4_df[(hs4_df["year"] == year) & (hs4_df["flow"] == flow)].copy()
        if sub.empty and not hs4_df.empty:
            sub = hs4_df[(hs4_df["year"] == hs4_df["year"].max()) & (hs4_df["flow"] == flow)].copy()

        # 1. Multi-level Treemap: Section -> HS2 Chapter -> HS4 Subheading
        sub["short_name"] = "HS " + sub["hs4_code"].astype(str) + ": " + sub["hs4_name"].apply(lambda s: (s[:28] + "..") if len(s) > 28 else s)
        sub["chapter_label"] = "Chapter " + sub["hs2_parent"].astype(str)
        fig_tree = px.treemap(
            sub,
            path=["hs_section", "chapter_label", "short_name"],
            values="value_eur",
            color="value_eur",
            color_continuous_scale="Blues" if flow == "EXPORT" else "Purples",
            hover_data={"value_eur": ":,.0f", "product_share_pct": ":.2f%", "share_in_chapter_pct": ":.1f%"}
        )
        fig_tree.update_layout(margin=dict(l=0, r=0, t=10, b=0))

        # 2. Top 15 HS4 Subheadings Bar Chart
        top15 = sub.sort_values("overall_rank").head(15).copy()
        top15 = top15.sort_values("value_eur", ascending=True)

        fig_top = go.Figure(go.Bar(
            x=top15["value_eur"] / 1e6,
            y=top15["short_name"],
            orientation="h",
            marker_color=PRIMARY if flow == "EXPORT" else SECONDARY,
            text=top15.apply(lambda r: f"{r['product_share_pct']:.1f}% ({r['share_in_chapter_pct']:.0f}% of Ch.{r['hs2_parent']})", axis=1),
            textposition="outside",
            hovertemplate="%{y}: €%{x:.0f}M (%{text})<extra></extra>"
        ))
        apply_plot_theme(fig_top, x_title="Million Euros (€M)")
        fig_top.update_layout(margin=dict(l=10, r=75, t=10, b=30), yaxis=dict(autorange="reversed"))

        # 3. Top HS4 Shift over time
        top_codes = top15.sort_values("value_eur", ascending=False).head(8)["hs4_code"].tolist()
        hist_sub = hs4_df[(hs4_df["hs4_code"].isin(top_codes)) & (hs4_df["flow"] == flow)].copy()

        fig_shift = go.Figure()
        for i, code in enumerate(top_codes):
            c_data = hist_sub[hist_sub["hs4_code"] == code].sort_values("year")
            if not c_data.empty:
                c_name = c_data["hs4_name"].iloc[0].split(";")[0].title()[:24]
                fig_shift.add_trace(go.Scatter(
                    x=c_data["year"], y=c_data["value_eur"] / 1e6,
                    name=f"HS {code}: {c_name}", mode="lines+markers",
                    line=dict(color=CATEGORICAL[i % len(CATEGORICAL)], width=2.5),
                    marker=dict(size=5),
                    hovertemplate=f"HS {code} ({c_name}): €%{{y:.0f}}M in %{{x}}<extra></extra>"
                ))
        apply_plot_theme(fig_shift, x_title="Year", y_title="Million Euros (€M)", dtick_x=1, hovermode="x unified")

        tree_title = f"Hierarchical 4-Digit Product Treemap (Click to Zoom) ({flow.capitalize()} {year})"
        bar_title = f"Top 15 Traded 4-Digit Goods ({year})"
        shift_title = f"Evolution of Top 4-Digit Products Over Time (Million €)"
        return tree_title, fig_tree, bar_title, fig_top, shift_title, fig_shift

    # Standard 2-digit macro view
    prods_df = load_product_rankings()
    sub = prods_df[(prods_df["year"] == year) & (prods_df["flow"] == flow)].copy()
    if sub.empty:
        avail_years = prods_df["year"].unique()
        if len(avail_years) > 0:
            sub = prods_df[(prods_df["year"] == max(avail_years)) & (prods_df["flow"] == flow)].copy()

    # 1. Treemap
    sub["short_name"] = sub["hs2_name"].apply(lambda s: (s[:32] + "..") if len(s) > 32 else s)
    fig_tree = px.treemap(
        sub,
        path=["hs_section", "short_name"],
        values="value_eur",
        color="value_eur",
        color_continuous_scale="Blues" if flow == "EXPORT" else "Purples",
        hover_data={"value_eur": ":,.0f", "product_share_pct": ":.2f%"}
    )
    fig_tree.update_layout(margin=dict(l=0, r=0, t=10, b=0))

    # 2. Top 10 HS2 Chapters Bar Chart
    top10 = sub.sort_values("rank").head(10).copy()
    top10 = top10.sort_values("value_eur", ascending=True)

    fig_top10 = go.Figure(go.Bar(
        x=top10["value_eur"] / 1e6,
        y=top10["short_name"],
        orientation="h",
        marker_color=PRIMARY if flow == "EXPORT" else SECONDARY,
        text=top10["product_share_pct"].apply(lambda p: f"{p:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.0f}M (%{text})<extra></extra>"
    ))
    apply_plot_theme(fig_top10, x_title="Million Euros (€M)")
    fig_top10.update_layout(margin=dict(l=10, r=40, t=10, b=30), yaxis=dict(autorange="reversed"))

    # 3. Structural Shifts
    key_chapters = ["72", "73", "84", "85", "87", "39", "30", "27"]
    hist_sub = prods_df[(prods_df["hs2_code"].isin(key_chapters)) & (prods_df["flow"] == flow)].copy()

    fig_shift = go.Figure()
    for i, code in enumerate(key_chapters):
        c_data = hist_sub[hist_sub["hs2_code"] == code].sort_values("year")
        if not c_data.empty:
            c_name = c_data["hs2_name"].iloc[0].split(";")[0].title()[:24]
            fig_shift.add_trace(go.Scatter(
                x=c_data["year"], y=c_data["product_share_pct"],
                name=f"HS {code}: {c_name}", mode="lines+markers",
                line=dict(color=CATEGORICAL[i % len(CATEGORICAL)], width=2.5),
                marker=dict(size=5),
                hovertemplate=f"HS {code} ({c_name}): %{{y:.1f}}% in %{{x}}<extra></extra>"
            ))
    apply_plot_theme(fig_shift, x_title="Year", y_title="Share of Total (%)", dtick_x=2, hovermode="x unified")

    tree_title = f"Product Tree by HS Section & Chapter ({flow.capitalize()} {year})"
    bar_title = f"Top 10 Traded Product Chapters ({year})"
    shift_title = "Structural Shifts in Product Composition (2000 vs Recent)"
    return tree_title, fig_tree, bar_title, fig_top10, shift_title, fig_shift



# ───────────────────────────────────────────────────────────────────────────
# TAB 4: PRODUCT & PARTNER DEEP-DIVE (Q3 & Q4)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_drilldown(selected_year):
    # Load product partner list
    pp_df = load_product_partners()
    product_options = []
    if not pp_df.empty:
        distinct_prods = pp_df[["hs2_code", "hs2_name"]].drop_duplicates().sort_values("hs2_code")
        product_options = [{"label": f"HS {r['hs2_code']}: {r['hs2_name'][:50]}", "value": r['hs2_code']} for _, r in distinct_prods.iterrows()]

    # Load partner list
    lvl2_df = load_drilldown_lvl2()
    partner_options = []
    if not lvl2_df.empty:
        distinct_partners = lvl2_df[["partner_code", "partner_name"]].drop_duplicates().sort_values("partner_name")
        partner_options = [{"label": f"{r['partner_name']} ({r['partner_code']})", "value": r['partner_code']} for _, r in distinct_partners.iterrows()]

    return html.Div([
        # Sub-tabs within Tab 4
        dbc.Tabs(id="drilldown-subtabs", active_tab="subtab-q3", children=[
            dbc.Tab(label="Part A: Principal Partners for a Product (Q3)", tab_id="subtab-q3", label_style={"fontWeight": "600"}),
            dbc.Tab(label="Part B: Hierarchical Partner Drill-down HS2→CN8 (Q4)", tab_id="subtab-q4", label_style={"fontWeight": "600"}),
        ], className="mb-4"),

        # Sub-tab Content
        html.Div(id="drilldown-subtab-content")
    ])


@callback(
    Output("drilldown-subtab-content", "children"),
    Input("drilldown-subtabs", "active_tab"),
    Input("global-year-dropdown", "value")
)
def render_drilldown_subtab(subtab, year):
    if subtab == "subtab-q3":
        pp_df = load_product_partners()
        product_options = []
        if not pp_df.empty:
            distinct_prods = pp_df[["hs2_code", "hs2_name"]].drop_duplicates().sort_values("hs2_code")
            product_options = [{"label": f"HS {r['hs2_code']}: {r['hs2_name'][:50]}", "value": r['hs2_code']} for _, r in distinct_prods.iterrows()]

        default_prod = "84" if any(p["value"] == "84" for p in product_options) else (product_options[0]["value"] if product_options else None)

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Principal Trading Partners for a Specific Product Category (Q3)", style={"fontWeight": "700"}),
                        html.P(
                            "Select any 2-digit HS Product Chapter to discover Luxembourg's principal supplier or destination nations, market shares, and supplier concentration (HHI).",
                            className="text-muted", style={"fontSize": "12px"}
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Product Category (HS2):", style={"fontSize": "12px", "fontWeight": "700"}),
                                dcc.Dropdown(
                                    id="q3-product-dropdown",
                                    options=product_options,
                                    value=default_prod,
                                    clearable=False,
                                    style={"fontSize": "13px"}
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Trade Flow Direction:", style={"fontSize": "12px", "fontWeight": "700"}),
                                dbc.RadioItems(
                                    id="q3-flow-radio",
                                    options=[
                                        {"label": "Imports (Suppliers)", "value": "IMPORT"},
                                        {"label": "Exports (Destinations)", "value": "EXPORT"},
                                    ],
                                    value="IMPORT",
                                    inline=True,
                                    style={"fontSize": "13px", "marginTop": "6px"}
                                )
                            ], md=6),
                        ], className="mb-3"),

                        html.Div(id="q3-badge-container", className="mb-3"),
                        dcc.Graph(id="q3-partner-bar-graph", config={"displayModeBar": False}),
                    ], style=CARD_STYLE)
                ], md=7),
                dbc.Col([
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Geographic Partner Distribution", style={"fontWeight": "700", "marginBottom": "0"}),
                            ], md=7),
                            dbc.Col([
                                dbc.RadioItems(
                                    id="q3-map-scope",
                                    options=[
                                        {"label": "🇪🇺 Europe", "value": "europe"},
                                        {"label": "🌍 World", "value": "world"},
                                    ],
                                    value="europe",
                                    inline=True,
                                    style={"fontSize": "12px"}
                                )
                            ], md=5, className="text-end"),
                        ], className="align-items-center mb-2"),
                        dcc.Graph(id="q3-partner-map-graph", config={"displayModeBar": True, "scrollZoom": True}, style={"height": "350px"}),
                        html.Div(id="q3-map-spotlight", className="mt-2")
                    ], style=CARD_STYLE)
                ], md=5),
            ])
        ])

    else:
        # Sub-tab Q4
        lvl2_df = load_drilldown_lvl2()
        partner_options = []
        if not lvl2_df.empty:
            distinct_partners = lvl2_df[["partner_code", "partner_name"]].drop_duplicates().sort_values("partner_name")
            partner_options = [{"label": f"{r['partner_name']} ({r['partner_code']})", "value": r['partner_code']} for _, r in distinct_partners.iterrows()]

        default_partner = "DE" if any(p["value"] == "DE" for p in partner_options) else (partner_options[0]["value"] if partner_options else None)

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Hierarchical Flow Drill-Down for a Partner Country (Q4)", style={"fontWeight": "700"}),
                        html.P(
                            "Navigate increasingly granular tariff lines from 2-digit (HS2 Chapters) to 4-digit (HS4 Subheadings) and 8-digit (CN8 Detailed Lines) with dynamic significance filtering.",
                            className="text-muted", style={"fontSize": "12px"}
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Trading Partner:", style={"fontSize": "12px", "fontWeight": "700"}),
                                dcc.Dropdown(
                                    id="q4-partner-dropdown",
                                    options=partner_options,
                                    value=default_partner,
                                    clearable=False,
                                    style={"fontSize": "13px"}
                                )
                            ], md=4),
                            dbc.Col([
                                html.Label("Flow Direction:", style={"fontSize": "12px", "fontWeight": "700"}),
                                dbc.RadioItems(
                                    id="q4-flow-radio",
                                    options=[
                                        {"label": "Imports", "value": "IMPORT"},
                                        {"label": "Exports", "value": "EXPORT"},
                                    ],
                                    value="IMPORT",
                                    inline=True,
                                    style={"fontSize": "13px", "marginTop": "6px"}
                                )
                            ], md=4),
                            dbc.Col([
                                html.Label("Granularity Level:", style={"fontSize": "12px", "fontWeight": "700"}),
                                dbc.RadioItems(
                                    id="q4-level-radio",
                                    options=[
                                        {"label": "2-Digit (HS2)", "value": 2},
                                        {"label": "4-Digit (HS4)", "value": 4},
                                        {"label": "8-Digit (CN8)", "value": 8},
                                    ],
                                    value=2,
                                    inline=True,
                                    style={"fontSize": "13px", "marginTop": "6px"}
                                )
                            ], md=4),
                        ], className="mb-3"),

                        dcc.Graph(id="q4-drilldown-bar-graph", config={"displayModeBar": False}),
                    ], style=CARD_STYLE)
                ], md=12)
            ])
        ])


# Callback for Q3 (Principal partners for a product)
@callback(
    Output("q3-badge-container", "children"),
    Output("q3-partner-bar-graph", "figure"),
    Output("q3-partner-map-graph", "figure"),
    Output("q3-map-spotlight", "children"),
    Input("q3-product-dropdown", "value"),
    Input("q3-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    Input("q3-map-scope", "value"),
    Input("q3-partner-map-graph", "clickData")
)
def update_q3_product_partners(product_code, flow, year, map_scope, click_data):
    if not product_code:
        return html.Div(), go.Figure(), go.Figure(), html.Div()

    pp_df = load_product_partners()
    # Normalize product_code string
    product_code = str(product_code).zfill(2)
    sub = pp_df[(pp_df["hs2_code"] == product_code) & (pp_df["flow"] == flow) & (pp_df["year"] == year)].copy()
    if sub.empty:
        # Fallback to latest available year in product partners
        avail_years = pp_df["year"].unique()
        if len(avail_years) > 0:
            year_used = max(avail_years)
            sub = pp_df[(pp_df["hs2_code"] == product_code) & (pp_df["flow"] == flow) & (pp_df["year"] == year_used)].copy()
        else:
            return html.Div("No data for this product."), go.Figure(), go.Figure(), html.Div()

    if sub.empty:
        return html.Div("No data found for this selection."), go.Figure(), go.Figure(), html.Div()

    # Product metadata
    prod_name = sub["hs2_name"].iloc[0]
    total_val = sub["total_eur"].iloc[0]
    hhi_score = sub["hhi"].iloc[0]

    # Look up top 3 HS4 subheadings for this chapter
    hs4_df = load_hs4_product_rankings()
    sub_hs4 = hs4_df[(hs4_df["hs2_parent"] == product_code) & (hs4_df["flow"] == flow) & (hs4_df["year"] == year)].copy()
    if sub_hs4.empty and not hs4_df.empty:
        sub_hs4 = hs4_df[(hs4_df["hs2_parent"] == product_code) & (hs4_df["flow"] == flow) & (hs4_df["year"] == hs4_df["year"].max())].copy()

    hs4_pills = []
    if not sub_hs4.empty:
        top3_hs4 = sub_hs4.sort_values("value_eur", ascending=False).head(3)
        hs4_pills = [
            html.Div([
                html.Span("Leading 4-Digit Lines:", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "marginRight": "8px"}),
            ] + [
                html.Span(
                    f"HS {r['hs4_code']}: {r['hs4_name'][:25]} ({r['share_in_chapter_pct']:.0f}% of ch.)",
                    style={
                        "backgroundColor": "#F8FAFC", "color": TEXT_PRIMARY, "padding": "3px 9px",
                        "borderRadius": "12px", "fontSize": "11px", "fontWeight": "600",
                        "marginRight": "6px", "border": f"1px solid {BORDER}", "marginBottom": "4px"
                    }
                ) for _, r in top3_hs4.iterrows()
            ], className="d-flex align-items-center flex-wrap mt-2")
        ]

    # Badge ribbon
    badge_html = html.Div([
        html.Div([
            html.Span(f"Total {flow.capitalize()}: {fmt_eur(total_val)}", style={
                "backgroundColor": "#EFF6FF", "color": "#1D4ED8", "padding": "5px 12px",
                "borderRadius": "20px", "fontWeight": "700", "fontSize": "12px", "marginRight": "10px",
                "border": "1px solid #BFDBFE"
            }),
            get_concentration_badge(hhi_score),
        ], className="d-flex align-items-center"),
    ] + hs4_pills)

    # Determine clicked partner
    clicked_p_code = None
    if click_data and "points" in click_data and click_data["points"]:
        pt = click_data["points"][0]
        if "customdata" in pt and pt["customdata"]:
            clicked_p_code = pt["customdata"][0]
        elif "location" in pt:
            for c2, c3 in ISO2_TO_ISO3.items():
                if c3 == pt["location"]:
                    clicked_p_code = c2
                    break

    # Top 10 partners bar chart
    top10 = sub.sort_values("value_eur", ascending=False).head(10).copy()
    top10 = top10.sort_values("value_eur", ascending=True)

    bar_colors = []
    for c in top10["partner_code"]:
        if clicked_p_code and c == clicked_p_code:
            bar_colors.append(WARNING)
        else:
            bar_colors.append(PRIMARY if flow == "EXPORT" else SECONDARY)

    fig_bar = go.Figure(go.Bar(
        x=top10["value_eur"] / 1e6,
        y=top10["partner_name"],
        orientation="h",
        marker_color=bar_colors,
        text=top10["partner_share_pct"].apply(lambda p: f"{p:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.1f}M (%{text})<extra></extra>"
    ))
    apply_plot_theme(fig_bar, title=f"Top 10 Partners for HS {product_code}: {prod_name[:35]}", x_title="Million Euros (€M)")
    fig_bar.update_layout(margin=dict(l=10, r=40, t=35, b=30), yaxis=dict(autorange="reversed"))

    # Map of partners with ISO3 mapping
    sub = add_iso3_column(sub)
    sub_valid = sub.dropna(subset=["iso3"]).copy()

    fig_map = px.choropleth(
        sub_valid,
        locations="iso3",
        color="value_eur",
        hover_name="partner_name",
        custom_data=["partner_code", "partner_name", "value_eur", "partner_share_pct", "rank"],
        color_continuous_scale="Blues" if flow == "EXPORT" else "Purples",
        projection="natural earth" if map_scope == "world" else "mercator"
    )
    fig_map.update_traces(
        hovertemplate="<b>%{customdata[1]}</b> (%{customdata[0]})<br>" +
                      f"{flow.capitalize()}: €%{{customdata[2]:,.0f}}<br>" +
                      "Product Category Share: %{customdata[3]:.1f}%<br>" +
                      "Supplier Rank: #%{customdata[4]}<br>" +
                      "<i>💡 Click country to inspect</i><extra></extra>"
    )
    fig_map.update_geos(
        showcoastlines=True, coastlinecolor="#CBD5E1",
        showland=True, landcolor="#F8FAFC",
        showocean=True, oceancolor="#F1F5F9",
        showcountries=True, countrycolor="#E2E8F0",
        scope=map_scope if map_scope else "europe"
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(title="€ Value", len=0.6, thickness=10, y=0.5),
        clickmode="event+select"
    )

    # Spotlight text below map
    if clicked_p_code and not sub[sub["partner_code"] == clicked_p_code].empty:
        r_match = sub[sub["partner_code"] == clicked_p_code].iloc[0]
        spotlight_elem = html.Div([
            html.Strong(f"📍 {r_match['partner_name']} ({clicked_p_code}): ", style={"color": PRIMARY if flow == 'EXPORT' else SECONDARY, "fontSize": "12px"}),
            html.Span(f"{fmt_eur(r_match['value_eur'])} ({r_match['partner_share_pct']:.1f}% of HS {product_code} {flow.lower()}s, Rank #{int(r_match['rank'])})", style={"fontSize": "12px", "color": TEXT_PRIMARY})
        ], className="p-2 rounded mt-1", style={"backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}"})
    else:
        top_match = sub.sort_values("value_eur", ascending=False).iloc[0] if not sub.empty else None
        if top_match is not None:
            spotlight_elem = html.Div([
                html.Span(f"📍 Lead Partner: {top_match['partner_name']} ({top_match['partner_code']}) — {fmt_eur(top_match['value_eur'])} ({top_match['partner_share_pct']:.1f}%). ", style={"fontSize": "11px", "color": TEXT_MUTED}),
                html.Span("💡 Click any country on the map to inspect its supply share.", style={"fontSize": "11px", "color": PRIMARY, "fontWeight": "600"})
            ], className="p-2 rounded mt-1", style={"backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}"})
        else:
            spotlight_elem = html.Div()

    return badge_html, fig_bar, fig_map, spotlight_elem


# Callback for Q4 (Hierarchical partner drilldown)
@callback(
    Output("q4-drilldown-bar-graph", "figure"),
    Input("q4-partner-dropdown", "value"),
    Input("q4-flow-radio", "value"),
    Input("q4-level-radio", "value")
)
def update_q4_drilldown_chart(partner, flow, level):
    if not partner:
        return go.Figure()

    if level == 2:
        df = load_drilldown_lvl2()
        sub = df[(df["partner_code"] == partner) & (df["flow"] == flow)].copy()
        sub = sub.sort_values("value_eur", ascending=True).tail(15)
        y_col = "product_name"
    elif level == 4:
        df = load_drilldown_lvl4()
        sub = df[(df["partner_code"] == partner) & (df["flow"] == flow)].copy()
        sub = sub.sort_values("value_eur", ascending=True).tail(15)
        sub["short_name"] = sub["product_code"].astype(str) + ": " + sub["product_name"].apply(lambda s: s[:45] + ".." if len(s) > 45 else s)
        y_col = "short_name"
    else:
        df = load_drilldown_lvl8()
        sub = df[(df["partner_code"] == partner) & (df["flow"] == flow)].copy()
        sub = sub.sort_values("value_eur", ascending=True).tail(15)
        sub["short_name"] = sub["product_code"].astype(str) + ": " + sub["product_name"].apply(lambda s: s[:45] + ".." if len(s) > 45 else s)
        y_col = "short_name"

    if sub.empty:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=sub["value_eur"] / 1e6,
        y=sub[y_col],
        orientation="h",
        marker_color=PRIMARY if flow == "EXPORT" else SECONDARY,
        text=sub["value_eur"].apply(lambda v: fmt_eur(v)),
        textposition="outside",
        hovertemplate="%{y}<br>Value: €%{x:.2f}M<extra></extra>"
    ))
    apply_plot_theme(fig, title=f"Top Significant Flows for {partner} ({level}-digit level)", x_title="Million Euros (€M)")
    fig.update_layout(margin=dict(l=10, r=50, t=35, b=30), yaxis=dict(autorange="reversed"))
    return fig


# ───────────────────────────────────────────────────────────────────────────
# TAB 5: PEER BENCHMARKS (Q5)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_benchmarks(selected_year):
    bench_df = load_country_benchmarks()
    if bench_df.empty:
        return html.Div("No benchmark data.")

    # 1. Growth Index since 2000 (Base 2000 = 100)
    fig_growth = go.Figure()
    countries = bench_df["reporter_code"].unique()
    for i, c in enumerate(countries):
        c_df = bench_df[bench_df["reporter_code"] == c].sort_values("year")
        c_name = c_df["reporter_name"].iloc[0]
        is_lu = (c == "LU")
        fig_growth.add_trace(go.Scatter(
            x=c_df["year"], y=c_df["volume_index_2000"],
            name=f"{c_name} ({c})", mode="lines+markers",
            line=dict(color=PRIMARY if is_lu else CATEGORICAL[i % len(CATEGORICAL)], width=4 if is_lu else 2),
            marker=dict(size=6 if is_lu else 4),
            hovertemplate=f"{c_name}: %{{y:.1f}} in %{{x}}<extra></extra>"
        ))
    apply_plot_theme(fig_growth, title="Trade Volume Expansion Index (2000 = 100)", y_title="Index (2000 = 100)", dtick_x=2, hovermode="x unified")

    # 2. Coverage Ratio Comparison (Exports / Imports)
    sub_yr = bench_df[bench_df["year"] == selected_year].sort_values("coverage_ratio_pct", ascending=True)
    if sub_yr.empty:
        sub_yr = bench_df[bench_df["year"] == bench_df["year"].max()].sort_values("coverage_ratio_pct", ascending=True)

    fig_cov = go.Figure(go.Bar(
        x=sub_yr["coverage_ratio_pct"],
        y=sub_yr["reporter_name"],
        orientation="h",
        marker_color=[PRIMARY if c == "LU" else NEUTRAL for c in sub_yr["reporter_code"]],
        text=sub_yr["coverage_ratio_pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}% coverage<extra></extra>"
    ))
    fig_cov.add_vline(x=100, line_dash="dash", line_color=DANGER, annotation_text="Trade Balance (100%)", annotation_position="top right")
    apply_plot_theme(fig_cov, title=f"Merchandise Coverage Ratio (Exports / Imports %) in {selected_year}", x_title="Coverage Ratio (%)")
    fig_cov.update_layout(margin=dict(l=10, r=40, t=35, b=30), yaxis=dict(autorange="reversed"))

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_growth, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=7),
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_cov, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=5),
        ]),
        html.Div([
            html.H6("Comparative Takeaways: Luxembourg vs. Regional Peers", style={"fontWeight": "700", "color": TEXT_PRIMARY}),
            html.Ul([
                html.Li("Trade Growth Alignment: Luxembourg's merchandise trade expanded by +89% since 2000, tracking France (+84%), while transit hubs like the Netherlands (+236%) and Belgium (+168%) saw higher goods growth due to major container ports (Rotterdam and Antwerp)."),
                html.Li("Coverage Asymmetry Explained: Germany (116%) and the Netherlands (111%) run large merchandise surpluses, whereas Luxembourg operates at ~65% goods coverage because physical imports (cars, fuel, food) are financed by massive net export surpluses in financial, fund administration, and corporate services."),
            ], style={"fontSize": "13px", "color": TEXT_MUTED, "marginBottom": "0"})
        ], style={**CARD_STYLE, "backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}"})
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 6: SEASONALITY & TREND LAB (Q6)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_seasonality():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Seasonality & Trend Filtering Lab (Q6)", style={"fontWeight": "700"}),
                    html.P("Empirical decomposition of monthly trade flows into 12-month centered trend, seasonal factors, and adjusted series.", className="text-muted", style={"fontSize": "12px"}),

                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Sector / Product:", style={"fontSize": "12px", "fontWeight": "700"}),
                            dcc.Dropdown(
                                id="season-product-dropdown",
                                options=[
                                    {"label": "Total Merchandise Trade", "value": "TOTAL"},
                                    {"label": "HS 72: Iron and Steel", "value": "72"},
                                    {"label": "HS 73: Articles of Iron or Steel", "value": "73"},
                                    {"label": "HS 84: Machinery & Mechanical Appliances", "value": "84"},
                                    {"label": "HS 85: Electrical Machinery & Equipment", "value": "85"},
                                    {"label": "HS 87: Vehicles and Automotive", "value": "87"},
                                    {"label": "HS 39: Plastics & Articles", "value": "39"},
                                    {"label": "HS 40: Rubber & Articles", "value": "40"},
                                    {"label": "HS 30: Pharmaceutical Products", "value": "30"},
                                    {"label": "HS 27: Mineral Fuels & Oils", "value": "27"},
                                ],
                                value="TOTAL",
                                clearable=False,
                                style={"fontSize": "13px"}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Trade Flow Direction:", style={"fontSize": "12px", "fontWeight": "700"}),
                            dbc.RadioItems(
                                id="season-flow-radio",
                                options=[
                                    {"label": "Exports", "value": "EXPORT"},
                                    {"label": "Imports", "value": "IMPORT"},
                                ],
                                value="EXPORT",
                                inline=True,
                                style={"fontSize": "13px", "marginTop": "6px"}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Series Display:", style={"fontSize": "12px", "fontWeight": "700"}),
                            dbc.Checklist(
                                id="season-series-check",
                                options=[
                                    {"label": "Raw Observed", "value": "raw"},
                                    {"label": "12-M Trend", "value": "trend"},
                                    {"label": "Seasonally Adjusted", "value": "adjusted"},
                                ],
                                value=["raw", "trend", "adjusted"],
                                inline=True,
                                style={"fontSize": "13px", "marginTop": "6px"}
                            )
                        ], md=4),
                    ], className="mb-3"),

                    dcc.Graph(id="season-timeseries-graph", config={"displayModeBar": False}),
                ], style=CARD_STYLE)
            ], md=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(id="season-factor-title", style={"fontWeight": "700"}),
                    html.P("Monthly seasonal index (1.0 = neutral). Notice the pronounced August slump (-14.4% dip) due to European factory holidays and Luxembourg's collective construction leave ('congé collectif').", className="text-muted", style={"fontSize": "12px"}),
                    dcc.Graph(id="season-factor-graph", config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=12)
        ])
    ])


@callback(
    Output("season-timeseries-graph", "figure"),
    Output("season-factor-title", "children"),
    Output("season-factor-graph", "figure"),
    Input("season-product-dropdown", "value"),
    Input("season-flow-radio", "value"),
    Input("season-series-check", "value")
)
def update_seasonality_chart(product, flow, selected_series):
    sea_df = load_seasonal_decomposition()
    sub = sea_df[(sea_df["product_code"] == product) & (sea_df["flow"] == flow)].sort_values("date").copy()

    if sub.empty:
        return go.Figure(), "No data", go.Figure()

    # 1. Multi-series Time Series Chart
    fig_ts = go.Figure()
    if "raw" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["value_eur"] / 1e6,
            name="Raw Observed", mode="lines",
            line=dict(color="#94A3B8", width=1.5),
            hovertemplate="Raw: €%{y:.1f}M<extra></extra>"
        ))
    if "trend" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["trend_eur"] / 1e6,
            name="12-Month Centered Trend", mode="lines",
            line=dict(color=PRIMARY, width=3),
            hovertemplate="Trend: €%{y:.1f}M<extra></extra>"
        ))
    if "adjusted" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["seasonally_adjusted_eur"] / 1e6,
            name="Seasonally Adjusted", mode="lines",
            line=dict(color=SUCCESS, width=2, dash="dot"),
            hovertemplate="Adjusted: €%{y:.1f}M<extra></extra>"
        ))

    apply_plot_theme(fig_ts, title=f"Monthly Trade Evolution & Seasonal Filtering ({sub['product_name'].iloc[0]})", y_title="Million Euros (€M)", hovermode="x unified")

    # 2. Monthly Factor Bar Chart
    monthly_factors = sub.groupby("month")["seasonal_factor"].first().reset_index()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_factors["month_name"] = monthly_factors["month"].apply(lambda m: month_names[m - 1])

    colors = [DANGER if f < 0.95 else (SUCCESS if f > 1.05 else PRIMARY) for f in monthly_factors["seasonal_factor"]]
    fig_fac = go.Figure(go.Bar(
        x=monthly_factors["month_name"],
        y=monthly_factors["seasonal_factor"],
        marker_color=colors,
        text=monthly_factors["seasonal_factor"].apply(lambda v: f"{v:.3f}"),
        textposition="outside",
        hovertemplate="Month %{x}: Factor %{y:.3f}<extra></extra>"
    ))
    fig_fac.add_hline(y=1.0, line_dash="dash", line_color=NEUTRAL, annotation_text="Baseline (1.0)")
    apply_plot_theme(fig_fac, y_title="Seasonal Factor (Ratio to Trend)", x_title="Month of Year")
    fig_fac.update_yaxes(range=[0.75, 1.25])

    factor_title = f"Empirical Month-of-Year Seasonal Factors: {sub['product_name'].iloc[0]}"
    return fig_ts, factor_title, fig_fac


# ───────────────────────────────────────────────────────────────────────────
# TAB 1: RESILIENCE & CONCENTRATION RADAR (Leadership Priority Pillar)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_resilience(selected_year):
    pp_df = load_product_partners()
    if pp_df.empty:
        return html.Div("Resilience data not available.")

    # Strategic Baskets definition
    BASKETS = {
        "Energy & Fuels": {"chapters": ["27"], "desc": "Refined petroleum, natural gas, electrical energy"},
        "Food & Agriculture": {"chapters": ["01", "02", "03", "04", "10", "16", "19", "22"], "desc": "Dairy, meat, cereals, beverages, essential nutrition"},
        "Health & Medicines": {"chapters": ["30", "90"], "desc": "Pharmaceutical products, surgical & medical instruments"},
        "Raw Materials & Metals": {"chapters": ["72", "73", "25", "26"], "desc": "Iron, steel, construction minerals"},
        "Tech & Machinery": {"chapters": ["84", "85"], "desc": "Computers, electrical generators, telecom apparatus"},
        "Vehicles & Transport": {"chapters": ["87"], "desc": "Passenger cars, commercial transport equipment"},
    }

    hs4_df = load_hs4_product_rankings()
    cards = []
    comparison_data = []

    # Filter for import data in latest available year
    use_year = selected_year
    sub_yr = pp_df[(pp_df["flow"] == "IMPORT") & (pp_df["year"] == use_year)]
    if sub_yr.empty:
        use_year = pp_df["year"].max()
        sub_yr = pp_df[(pp_df["flow"] == "IMPORT") & (pp_df["year"] == use_year)]

    for basket_name, info in BASKETS.items():
        chs = info["chapters"]
        basket_data = sub_yr[sub_yr["hs2_code"].isin(chs)]
        if not basket_data.empty:
            total_b_val = basket_data["value_eur"].sum()
            # Top supplier in basket
            partner_agg = basket_data.groupby(["partner_code", "partner_name"])["value_eur"].sum().reset_index()
            partner_agg["share_pct"] = (partner_agg["value_eur"] / total_b_val) * 100
            partner_agg = partner_agg.sort_values("value_eur", ascending=False)
            top_p = partner_agg.iloc[0]
            top_p_share = top_p["share_pct"]
            top_p_name = top_p["partner_name"]

            # Calculate basket HHI
            basket_hhi = (partner_agg["share_pct"] ** 2).sum()

            # Hub transit share (BE + NL ports)
            hub_val = partner_agg[partner_agg["partner_code"].isin(["BE", "NL"])]["value_eur"].sum()
            hub_share = (hub_val / total_b_val) * 100

            comparison_data.append({
                "basket": basket_name,
                "val_m": total_b_val / 1e6,
                "hhi": basket_hhi,
                "hub_share": hub_share,
                "top_share": top_p_share,
                "top_name": top_p_name
            })

            # Top 4-digit good in basket
            top_hs4_div = html.Div()
            if not hs4_df.empty:
                b_hs4 = hs4_df[(hs4_df["hs2_parent"].isin(chs)) & (hs4_df["flow"] == "IMPORT") & (hs4_df["year"] == use_year)]
                if b_hs4.empty:
                    b_hs4 = hs4_df[(hs4_df["hs2_parent"].isin(chs)) & (hs4_df["flow"] == "IMPORT") & (hs4_df["year"] == hs4_df["year"].max())]
                if not b_hs4.empty:
                    lead_h4 = b_hs4.sort_values("value_eur", ascending=False).iloc[0]
                    top_hs4_div = html.Div([
                        html.Span("Key 4-Digit Good: ", style={"fontSize": "11px", "color": TEXT_MUTED}),
                        html.Strong(f"HS {lead_h4['hs4_code']}: {lead_h4['hs4_name'][:26]} ({fmt_eur(lead_h4['value_eur'])})", style={"fontSize": "11px", "color": TEXT_PRIMARY})
                    ], className="mb-1")

            cards.append(dbc.Col([
                html.Div([
                    html.Div([
                        html.Span(basket_name.upper(), style={"fontSize": "11px", "fontWeight": "800", "color": TEXT_PRIMARY, "letterSpacing": "0.5px"}),
                        get_concentration_badge(basket_hhi)
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    html.H4(fmt_eur(total_b_val), style={"fontWeight": "800", "color": PRIMARY, "marginBottom": "4px"}),
                    html.P(info["desc"], className="text-muted", style={"fontSize": "11px", "marginBottom": "8px"}),
                    top_hs4_div,
                    html.Div([
                        html.Span("Top Supplier: ", style={"fontSize": "12px", "color": TEXT_MUTED}),
                        html.Strong(f"{top_p_name} ({top_p_share:.1f}%)", style={"fontSize": "12px", "color": TEXT_PRIMARY})
                    ], className="mb-1"),
                    html.Div([
                        html.Span("Via BE/NL Transit Hubs: ", style={"fontSize": "12px", "color": TEXT_MUTED}),
                        html.Strong(f"{hub_share:.1f}%", style={"fontSize": "12px", "color": WARNING if hub_share > 50 else TEXT_PRIMARY})
                    ])
                ], style=KPI_CARD_STYLE)
            ], md=4, sm=6, className="mb-3"))

    # Vulnerability Comparison Chart
    fig_comp = go.Figure()
    if comparison_data:
        comp_df = pd.DataFrame(comparison_data).sort_values("hhi", ascending=True)
        fig_comp.add_trace(go.Bar(
            y=comp_df["basket"],
            x=comp_df["hhi"],
            name="Concentration Index (HHI)",
            orientation="h",
            marker_color=[DANGER if h >= 2500 else (WARNING if h >= 1500 else SUCCESS) for h in comp_df["hhi"]],
            text=comp_df["hhi"].apply(lambda v: f"HHI {v:.0f}"),
            textposition="outside",
            hovertemplate="%{y}<br>Supplier HHI: %{x:.0f}<extra></extra>"
        ))
        apply_plot_theme(fig_comp, title=f"Strategic Baskets Supplier Concentration Score (HHI) in {use_year}", x_title="HHI Score (Higher = Greater Concentration Risk)")
        fig_comp.add_vline(x=2500, line_dash="dash", line_color=DANGER, annotation_text="High Risk Threshold (2500)", annotation_position="top right")
        fig_comp.add_vline(x=1500, line_dash="dot", line_color=WARNING, annotation_text="Moderate (1500)", annotation_position="bottom right")
        fig_comp.update_layout(margin=dict(l=10, r=40, t=35, b=30), yaxis=dict(autorange="reversed"))

    # Executive Alert Banners
    alert_banners = dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("⚡", style={"fontSize": "18px", "marginRight": "8px"}),
                    html.Strong("ENERGY & FUELS VULNERABILITY", style={"fontSize": "12px", "color": "#991B1B"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Extreme dependency (HHI > 3,800). Over 50% of refined petroleum and natural gas arrives via pipeline and refinery infrastructure in Belgium and Netherlands.", style={"fontSize": "11px", "color": "#7F1D1D", "marginBottom": "0"})
            ], style={"backgroundColor": "#FEF2F2", "border": "1px solid #FCA5A5", "borderRadius": "8px", "padding": "12px 14px", "height": "100%"})
        ], md=3, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("🚢", style={"fontSize": "18px", "marginRight": "8px"}),
                    html.Strong("PORT TRANSIT DEPENDENCY", style={"fontSize": "12px", "color": "#92400E"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Rotterdam-Antwerp Gateway: ~33% of merchandise is consigned via Belgian and Dutch port corridors, creating physical choke-point exposure.", style={"fontSize": "11px", "color": "#78350F", "marginBottom": "0"})
            ], style={"backgroundColor": "#FFFBEB", "border": "1px solid #FCD34D", "borderRadius": "8px", "padding": "12px 14px", "height": "100%"})
        ], md=3, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("💶", style={"fontSize": "18px", "marginRight": "8px"}),
                    html.Strong("MACRO SERVICE BUFFER", style={"fontSize": "12px", "color": "#065F46"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Goods Deficit Hedged: The €9.2B merchandise deficit is sustainably financed by Luxembourg's massive surplus in financial and corporate services (+€25B+).", style={"fontSize": "11px", "color": "#064E3B", "marginBottom": "0"})
            ], style={"backgroundColor": "#ECFDF5", "border": "1px solid #6EE7B7", "borderRadius": "8px", "padding": "12px 14px", "height": "100%"})
        ], md=3, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("❄️", style={"fontSize": "18px", "marginRight": "8px"}),
                    html.Strong("AUGUST CYCLICAL SLUMP", style={"fontSize": "12px", "color": "#1E40AF"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Predictable Contraction: Merchandise flows dip by 14.4% every August due to European factory holidays and Luxembourg's 'congé collectif'.", style={"fontSize": "11px", "color": "#1E3A8A", "marginBottom": "0"})
            ], style={"backgroundColor": "#EFF6FF", "border": "1px solid #93C5FD", "borderRadius": "8px", "padding": "12px 14px", "height": "100%"})
        ], md=3, sm=6, className="mb-2"),
    ], className="mb-3")

    return html.Div([
        # Header banner
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("National Resilience Strategy: Strategic Import Dependency Radar", style={"fontWeight": "800", "color": TEXT_PRIMARY, "margin": "0"}),
                        html.Span("EXECUTIVE OVERVIEW FOR LEADERSHIP", className="badge bg-warning text-dark ms-3", style={"fontWeight": "700", "fontSize": "11px"})
                    ], className="d-flex align-items-center mb-1"),
                    html.P(
                        "Tracking Luxembourg's sovereign supply chain resilience and single-source supplier vulnerabilities across vital import baskets (Eurostat Comext data). Evaluates single-point supplier risks and transit vulnerability through Belgian and Dutch ports.",
                        className="text-muted", style={"fontSize": "13px", "marginBottom": "0"}
                    )
                ], className="mb-3")
            ], md=12)
        ]),

        alert_banners,

        # Chart Row
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_comp, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=12)
        ]),

        # Basket Cards Row
        dbc.Row(cards),

        # Takeaways & Recommendations
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Sovereign Policy Recommendations & Resilience Safeguards", style={"fontWeight": "700", "color": TEXT_PRIMARY}),
                    html.Ul([
                        html.Li("Energy Sovereignty: Refined petroleum products exhibit an HHI > 3,800, indicating intense single-source reliance on Belgian/Dutch refinery pipelines. Establish bilateral strategic petroleum reserves and explore grid electrification."),
                        html.Li("The 'Rotterdam-Antwerp Effect': Over 33% of Luxembourg's physical trade in goods transits through Belgian and Dutch ports. Formalize logistics contingency routes via French rail/ports to insulate against North Sea maritime disruptions."),
                        html.Li("High Resilience in Advanced Tech & Machinery: Tech and machinery baskets demonstrate healthy diversification across Germany, France, Japan, and the United States (HHI ~1,500)."),
                        html.Li("Healthcare Buffer: Pharmaceuticals are concentrated in Belgium and Germany; enforce minimum 90-day sovereign stockpile requirements for essential hospital medicines ahead of summer maintenance shutdowns."),
                    ], style={"fontSize": "13px", "color": TEXT_MUTED, "marginBottom": "0"})
                ], style={**CARD_STYLE, "backgroundColor": "#FFFBEB", "border": "1px solid #FDE68A"})
            ], md=12)
        ])
    ])


# ── Run Server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
