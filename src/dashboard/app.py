# -*- coding: utf-8 -*-
"""STATEC Hackathon 2026 — Luxembourg External Trade Intelligence (2000–2026).
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
    create_info_hover, fmt_eur, fmt_pct, get_concentration_badge
)
from src.dashboard.data_loader import (
    load_overview_kpis, load_partner_rankings, load_product_rankings,
    load_hs4_product_rankings, load_product_partners, load_seasonal_decomposition,
    load_country_benchmarks, load_drilldown_lvl2, load_drilldown_lvl4, load_drilldown_lvl8
)

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

app = dash.Dash(
    __name__,
    assets_folder=str(BASE_DIR / "assets"),
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&display=swap"
    ],
    title="Luxembourg Trade Intelligence (Resilience Radar) — STATEC Hackathon 2026",
    suppress_callback_exceptions=True
)
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""
server = app.server


# ── Header ─────────────────────────────────────────────────────────────────
def create_header():
    return html.Div([
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            create_icon_badge("bi bi-shield-check", color=STATEC_NAVY, bg="#FFF9E6", size=20, box_size=40),
                            html.Div([
                                html.Span("TRADE", className="brand-logo"),
                                html.Span(".lu", className="brand-accent"),
                            ], className="ms-2"),
                            html.Div(className="brand-divider d-none d-lg-block"),
                            html.Div([
                                html.Span("LUXEMBOURG EXTERNAL TRADE INTELLIGENCE", className="portal-title"),
                                html.Span("Eurostat Comext Open Data [ds-045409] (2000–2026)", className="portal-subtitle"),
                            ], className="d-none d-lg-block"),
                        ], className="d-flex align-items-center py-2")
                    ], md=8),

                    dbc.Col([
                        html.Div([
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-calendar3 me-1 text-primary"),
                                    "ANALYSIS YEAR"
                                ], className="header-filter-label"),
                                dcc.Dropdown(
                                    id="global-year-dropdown",
                                    options=[{"label": str(y), "value": y} for y in range(2025, 1999, -1)],
                                    value=2025,
                                    clearable=False,
                                    className="header-year-dropdown"
                                )
                            ], className="d-flex flex-column align-items-end")
                        ], className="d-flex justify-content-end align-items-center py-2")
                    ], md=4)
                ], className="align-items-center")
            ], fluid=True, className="app-container-max")
        ], className="app-header-main"),

        html.Div([
            dbc.Container([
                html.Div([
                    html.Span("STATEC HACKATHON 2026", className="substrip-badge"),
                    html.Span("Interactive merchandise trade analytics and tariff line decomposition (HS2–CN8).", className="substrip-text"),
                ], className="d-flex align-items-center")
            ], fluid=True, className="app-container-max")
        ], className="app-substrip")
    ])


# ── Compact Key Figures Ribbon in Leadership View ─────────────────
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
                    html.Span("IMPORTS (GOODS)", className="kpi-label"),
                    html.H5(fmt_eur(imp_val), className="kpi-val kpi-val-navy"),
                    html.Small("Annual merchandise imports", className="kpi-caption")
                ], className="compact-kpi-tile")
            ], md=2, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("EXPORTS (GOODS)", className="kpi-label"),
                    html.H5(fmt_eur(exp_val), className="kpi-val kpi-val-blue"),
                    html.Small("Annual merchandise exports", className="kpi-caption")
                ], className="compact-kpi-tile")
            ], md=2, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("MERCHANDISE BALANCE", className="kpi-label"),
                    html.H5(fmt_eur(bal_val), className=f"kpi-val {'kpi-val-danger' if bal_val < 0 else 'kpi-val-success'}"),
                    html.Small("Exports minus Imports", className="kpi-caption")
                ], className="compact-kpi-tile")
            ], md=3, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("COVERAGE RATIO", className="kpi-label"),
                    html.H5(f"{cov_val:.1f}%", className="kpi-val kpi-val-navy"),
                    html.Small("Exports / Imports ratio", className="kpi-caption")
                ], className="compact-kpi-tile")
            ], md=3, sm=6, className="mb-2"),

            dbc.Col([
                html.Div([
                    html.Span("INTRA-EU IMPORTS", className="kpi-label"),
                    html.H5(f"{eu_imp:.1f}%", className="kpi-val kpi-val-blue"),
                    html.Small("Share of total merchandise imports", className="kpi-caption")
                ], className="compact-kpi-tile")
            ], md=2, sm=6, className="mb-2"),
        ], className="g-2")
    ], className="mb-3")


# ── Navigation: 2 Major Modes (Resilience Radar vs Deep-Dive) ─────────────
def create_navigation_boxes():
    return html.Div([
        html.Div([
            # Two Major Mode Buttons
            html.Div([
                html.Button([
                    html.I(className="bi bi-shield-check me-2"),
                    "Resilience Radar"
                ], id="btn-mode-resilience", className="nav-mode-btn active", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-diagram-3 me-2"),
                    "Deep-Dive"
                ], id="btn-mode-deepdive", className="nav-mode-btn", n_clicks=0),
            ], className="nav-mode-bar"),

            # Sub-row: 4 Resilience Radar buttons (shown when Resilience Radar is active)
            html.Div([
                html.Button([
                    html.I(className="bi bi-shield-check me-1 text-warning"),
                    "1. Product Baskets & Concentration"
                ], id="btn-tab-resilience", className="nav-tab-btn active", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-graph-up me-1 text-primary"),
                    "2. Macro Trajectory & Balances"
                ], id="btn-tab-macro", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-globe-europe-africa me-1 text-info"),
                    "3. Geopolitical Origins"
                ], id="btn-tab-geopolitics", className="nav-tab-btn", n_clicks=0),

                html.Button([
                    html.I(className="bi bi-lightning-charge me-1 text-danger"),
                    "4. Historical Shock Scenarios"
                ], id="btn-tab-stress", className="nav-tab-btn", n_clicks=0),
            ], id="nav-group-resilience", className="d-flex flex-wrap nav-subtabs-container"),

            # Sub-row: 6 Deep-Dive buttons (shown when Deep-Dive is active)
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
            ], id="nav-group-deepdive", className="d-none nav-subtabs-container"),
        ], className="nav-mode-container")
    ])


# ── App Main Layout ─────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="nav-mode-store", data="resilience"),
    dcc.Store(id="active-tab-store", data="tab-resilience"),
    create_header(),
    dbc.Container([
        create_navigation_boxes(),
        # Tab Content Container
        html.Div(id="tab-content")
    ], fluid=True, className="app-content-container"),
    create_dashboard_footer()
])


# ── Active Tab Navigation Router ───────────────────────────────────────────
ALL_TAB_BTNS = [
    "btn-tab-resilience", "btn-tab-macro", "btn-tab-geopolitics", "btn-tab-stress",
    "btn-tab-partners", "btn-tab-products", "btn-tab-q3-partners",
    "btn-tab-q4-drilldown", "btn-tab-benchmarks", "btn-tab-seasonality"
]
TAB_ID_MAP = {
    "btn-tab-resilience": "tab-resilience",
    "btn-tab-macro": "tab-macro",
    "btn-tab-geopolitics": "tab-geopolitics",
    "btn-tab-stress": "tab-stress",
    "btn-tab-partners": "tab-partners",
    "btn-tab-products": "tab-products",
    "btn-tab-q3-partners": "tab-q3-partners",
    "btn-tab-q4-drilldown": "tab-q4-drilldown",
    "btn-tab-benchmarks": "tab-benchmarks",
    "btn-tab-seasonality": "tab-seasonality"
}
RESILIENCE_TABS = ["tab-resilience", "tab-macro", "tab-geopolitics", "tab-stress"]
DEEPDIVE_TABS = ["tab-partners", "tab-products", "tab-q3-partners", "tab-q4-drilldown", "tab-benchmarks", "tab-seasonality"]


@callback(
    Output("nav-mode-store", "data"),
    Output("active-tab-store", "data"),
    Output("btn-mode-resilience", "className"),
    Output("btn-mode-deepdive", "className"),
    Output("nav-group-resilience", "className"),
    Output("nav-group-deepdive", "className"),
    [Output(b_id, "className") for b_id in ALL_TAB_BTNS],
    Input("btn-mode-resilience", "n_clicks"),
    Input("btn-mode-deepdive", "n_clicks"),
    [Input(b_id, "n_clicks") for b_id in ALL_TAB_BTNS],
    State("nav-mode-store", "data"),
    State("active-tab-store", "data"),
    prevent_initial_call=False
)
def switch_active_nav_tab(mode_res_clk, mode_dd_clk, *args):
    current_mode = args[-2] or "resilience"
    current_tab = args[-1] or "tab-resilience"

    try:
        ctx = dash.callback_context
        if ctx and ctx.triggered:
            trig_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trig_id == "btn-mode-resilience":
                current_mode = "resilience"
                if current_tab not in RESILIENCE_TABS:
                    current_tab = "tab-resilience"
            elif trig_id == "btn-mode-deepdive":
                current_mode = "deepdive"
                if current_tab not in DEEPDIVE_TABS:
                    current_tab = "tab-partners"
            elif trig_id in TAB_ID_MAP:
                clicked_tab = TAB_ID_MAP[trig_id]
                current_tab = clicked_tab
                if clicked_tab in RESILIENCE_TABS:
                    current_mode = "resilience"
                else:
                    current_mode = "deepdive"
    except Exception:
        pass

    mode_res_class = "nav-mode-btn active" if current_mode == "resilience" else "nav-mode-btn"
    mode_dd_class = "nav-mode-btn active" if current_mode == "deepdive" else "nav-mode-btn"

    group_res_class = "d-flex flex-wrap nav-subtabs-container" if current_mode == "resilience" else "d-none"
    group_dd_class = "d-flex flex-wrap nav-subtabs-container" if current_mode == "deepdive" else "d-none"

    tab_classes = [
        "nav-tab-btn active" if TAB_ID_MAP[b_id] == current_tab else "nav-tab-btn"
        for b_id in ALL_TAB_BTNS
    ]

    return tuple([current_mode, current_tab, mode_res_class, mode_dd_class, group_res_class, group_dd_class] + tab_classes)


@callback(
    Output("tab-content", "children"),
    Input("active-tab-store", "data"),
    Input("global-year-dropdown", "value")
)
def render_main_tab_content(active_tab, selected_year):
    if active_tab == "tab-resilience":
        return render_tab_resilience(selected_year)
    elif active_tab == "tab-macro":
        return render_tab_macro(selected_year)
    elif active_tab == "tab-geopolitics":
        return render_tab_geopolitics(selected_year)
    elif active_tab == "tab-stress":
        return render_tab_stress(selected_year)
    elif active_tab == "tab-partners":
        return render_tab_partners(selected_year)
    elif active_tab == "tab-products":
        return render_tab_products(selected_year)
    elif active_tab == "tab-q3-partners":
        return render_tab_q3_product_partners(selected_year)
    elif active_tab == "tab-q4-drilldown":
        return render_tab_q4_drilldown(selected_year)
    elif active_tab == "tab-benchmarks":
        return render_tab_benchmarks(selected_year)
    elif active_tab == "tab-seasonality":
        return render_tab_seasonality()
    return html.Div("Loading tab...")


# ───────────────────────────────────────────────────────────────────────────
# TAB 1: SOVEREIGN SUPPLY RESILIENCE RADAR (Pillars 3–5)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_resilience(selected_year):
    pp_df = load_product_partners()
    if pp_df.empty:
        return html.Div("Resilience data not available.")

    BASKETS = {
        "Energy & Fuels": {"chapters": ["27"], "desc": "Refined petroleum, natural gas, electrical energy"},
        "Food & Nutrition": {"chapters": ["01", "02", "03", "04", "10", "16", "19", "22"], "desc": "Dairy, meat, cereals, beverages, essential nutrition"},
        "Health & Medicines": {"chapters": ["30", "90"], "desc": "Pharmaceutical products, surgical & medical instruments"},
        "Raw Materials & Metals": {"chapters": ["72", "73", "25", "26"], "desc": "Iron, steel, construction minerals"},
        "Tech & Machinery": {"chapters": ["84", "85"], "desc": "Computers, electrical generators, telecom apparatus"},
        "Vehicles & Transport": {"chapters": ["87"], "desc": "Passenger cars, commercial transport equipment"},
    }

    hs4_df = load_hs4_product_rankings()
    cards = []
    comparison_data = []

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
            partner_agg = basket_data.groupby(["partner_code", "partner_name"])["value_eur"].sum().reset_index()
            partner_agg["share_pct"] = (partner_agg["value_eur"] / total_b_val) * 100
            partner_agg = partner_agg.sort_values("value_eur", ascending=False)
            top_p = partner_agg.iloc[0]
            top_p_share = top_p["share_pct"]
            top_p_name = get_country_name(top_p["partner_code"])

            basket_hhi = (partner_agg["share_pct"] ** 2).sum()
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

            top_hs4_div = html.Div()
            if not hs4_df.empty:
                b_hs4 = hs4_df[(hs4_df["hs2_parent"].isin(chs)) & (hs4_df["flow"] == "IMPORT") & (hs4_df["year"] == use_year)]
                if b_hs4.empty:
                    b_hs4 = hs4_df[(hs4_df["hs2_parent"].isin(chs)) & (hs4_df["flow"] == "IMPORT") & (hs4_df["year"] == hs4_df["year"].max())]
                if not b_hs4.empty:
                    lead_h4 = b_hs4.sort_values("value_eur", ascending=False).iloc[0]
                    top_hs4_div = html.Div([
                        html.Span("Leading 4-Digit Good: ", className="small text-muted"),
                        html.Strong(f"HS {lead_h4['hs4_code']}: {lead_h4['hs4_name'][:26]} ({fmt_eur(lead_h4['value_eur'])})", className="small")
                    ], className="mb-1")

            cards.append(dbc.Col([
                html.Div([
                    html.Div([
                        html.Span(basket_name.upper(), className="card-title-upper mb-0"),
                        get_concentration_badge(basket_hhi)
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    html.H4(fmt_eur(total_b_val), className="kpi-val kpi-val-blue mb-1"),
                    html.P(info["desc"], className="text-muted small mb-2"),
                    top_hs4_div,
                    html.Div([
                        html.Span("Top Supplier: ", className="text-muted small"),
                        html.Strong(f"{top_p_name} ({top_p_share:.1f}%)", className="small")
                    ], className="mb-1"),
                    html.Div([
                        html.Span("Via BE/NL Transit Hubs: ", className="text-muted small"),
                        html.Strong(f"{hub_share:.1f}%", className=f"small {'text-warning' if hub_share > 50 else ''}")
                    ])
                ], className="dash-kpi-card")
            ], md=4, sm=6, className="mb-3"))

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
            hovertemplate="%{y}<br>Supplier Concentration HHI: %{x:.0f}<extra></extra>"
        ))
        apply_plot_theme(fig_comp, title=f"Import Baskets Supplier Concentration Score (HHI) in {use_year}", x_title="Herfindahl-Hirschman Index (HHI)")
        fig_comp.add_vline(x=2500, line_dash="dash", line_color=DANGER, annotation_text="HHI = 2,500", annotation_position="top right")
        fig_comp.add_vline(x=1500, line_dash="dot", line_color=WARNING, annotation_text="HHI = 1,500", annotation_position="bottom right")
        # Explicit legend traces for color definitions
        fig_comp.add_trace(go.Bar(name="High Concentration (HHI > 2,500)", x=[None], y=[None], marker_color=DANGER, showlegend=True))
        fig_comp.add_trace(go.Bar(name="Moderate Concentration (1,500–2,500)", x=[None], y=[None], marker_color=WARNING, showlegend=True))
        fig_comp.add_trace(go.Bar(name="Low / Diversified (HHI < 1,500)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
        fig_comp.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=11)),
            margin=dict(l=10, r=40, t=55, b=30),
            yaxis=dict(autorange="reversed")
        )

    return html.Div([
        create_compact_kpi_ribbon(use_year),

        create_section_header(
            f"IMPORT BASKETS CONCENTRATION ({use_year})",
            "Supplier concentration and Herfindahl-Hirschman Index (HHI) across 6 merchandise baskets (Energy, Food, Health, Metals, Tech, Vehicles).",
            badge_text="Merchandise Baskets",
            badge_color=STATEC_NAVY,
            info_title="Herfindahl-Hirschman Index (HHI) Calculation",
            info_content=[
                html.P("The HHI measures supplier concentration as the sum of squared market shares of supplying nations:", className="fw-semibold mb-1"),
                html.Ul([
                    html.Li("HHI < 1,500: Low concentration"),
                    html.Li("1,500 – 2,500: Moderate concentration"),
                    html.Li("HHI > 2,500: High concentration"),
                ], className="ps-3 mb-0")
            ]
        ),

        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_comp, config={"displayModeBar": False})
                ], className="dash-card")
            ], md=12)
        ]),

        dbc.Row(cards)
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 2: MACROECONOMIC HEALTH & TRAJECTORY
# ───────────────────────────────────────────────────────────────────────────
def render_tab_macro(selected_year):
    kpis_df = load_overview_kpis()
    if kpis_df.empty:
        return html.Div("Macro data not available.")

    fig_trajectory = go.Figure()
    # Imports first (left / navy), Exports second (blue)
    fig_trajectory.add_trace(go.Scatter(
        x=kpis_df["year"], y=kpis_df["IMPORT"] / 1e9,
        name="Imports", mode="lines+markers",
        line=dict(color=SECONDARY, width=3),
        marker=dict(size=6),
        hovertemplate="Imports: €%{y:.2f}B (%{x})<extra></extra>"
    ))
    fig_trajectory.add_trace(go.Scatter(
        x=kpis_df["year"], y=kpis_df["EXPORT"] / 1e9,
        name="Exports", mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=6),
        hovertemplate="Exports: €%{y:.2f}B (%{x})<extra></extra>"
    ))
    apply_plot_theme(fig_trajectory, title="25-Year Trajectory of Luxembourg Merchandise Trade Flows (2000–2026)", y_title="Billion Euros (€B)", dtick_x=2, hovermode="x unified")

    colors = [SUCCESS if v >= 0 else DANGER for v in kpis_df["trade_balance_eur"]]
    fig_balance = go.Figure(go.Bar(
        x=kpis_df["year"], y=kpis_df["trade_balance_eur"] / 1e9,
        marker_color=colors,
        hovertemplate="Trade Balance %{x}: €%{y:.2f}B<extra></extra>"
    ))
    apply_plot_theme(fig_balance, title="Annual Merchandise Trade Balance (€B)", y_title="Billion Euros (€B)", dtick_x=2)

    fig_eu = go.Figure()
    if "intra_eu_import_share_pct" in kpis_df.columns:
        fig_eu.add_trace(go.Scatter(
            x=kpis_df["year"], y=kpis_df["intra_eu_import_share_pct"],
            name="Intra-EU Import Share %", line=dict(color=SECONDARY, width=2.5), mode="lines+markers"
        ))
    if "intra_eu_export_share_pct" in kpis_df.columns:
        fig_eu.add_trace(go.Scatter(
            x=kpis_df["year"], y=kpis_df["intra_eu_export_share_pct"],
            name="Intra-EU Export Share %", line=dict(color=PRIMARY, width=2.5), mode="lines+markers"
        ))
    apply_plot_theme(fig_eu, title="European Integration: Share of Trade with EU Partners (%)", y_title="Share of Total (%)", dtick_x=2)
    fig_eu.update_yaxes(range=[55, 95])

    vol_growth_pct = 0.0
    if not kpis_df.empty:
        v_start = kpis_df[kpis_df["year"] == kpis_df["year"].min()]["trade_volume_eur"].iloc[0]
        v_sub = kpis_df[kpis_df["year"] == selected_year]
        v_end = v_sub["trade_volume_eur"].iloc[0] if not v_sub.empty else kpis_df["trade_volume_eur"].iloc[-1]
        vol_growth_pct = ((v_end / v_start) - 1.0) * 100 if v_start > 0 else 0.0

    return html.Div([
        create_section_header(
            f"MACROECONOMIC TRAJECTORY & TRADE BALANCE (2000–2026)",
            f"Long-term merchandise trade volume growth ({vol_growth_pct:+.1f}% vs baseline {kpis_df['year'].min() if not kpis_df.empty else 2000}), trade balance evolution, and EU Single Market integration.",
            badge_text="Macro Overview",
            badge_color=STATEC_NAVY
        ),

        dbc.Row([
            dbc.Col([
                html.Div([dcc.Graph(figure=fig_trajectory, config={"displayModeBar": False})], className="dash-card")
            ], md=8),
            dbc.Col([
                html.Div([dcc.Graph(figure=fig_balance, config={"displayModeBar": False})], className="dash-card")
            ], md=4),
        ]),

        dbc.Row([
            dbc.Col([
                html.Div([dcc.Graph(figure=fig_eu, config={"displayModeBar": False})], className="dash-card")
            ], md=12)
        ])
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 3: GEOPOLITICAL EXPOSURE & SEASONAL SHOCKS
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

    neigh_share = (neigh_val / tot_imp * 100) if tot_imp > 0 else 0.0
    other_eu_share = (other_eu_val / tot_imp * 100) if tot_imp > 0 else 0.0
    row_share = (row_val / tot_imp * 100) if tot_imp > 0 else 0.0

    non_eu_sub = sub[~sub['partner_code'].isin(eu_codes)].sort_values('value_eur', ascending=False).head(8).copy()

    def assign_geo_tier(code):
        if code in neighbors:
            return f"Direct Neighbors ({neigh_share:.1f}% of Goods)"
        elif code in eu_codes:
            return f"EU Single Market Partners ({other_eu_share:.1f}%)"
        elif code in non_eu_sub["partner_code"].values:
            return "Strategic Non-EU Suppliers"
        return "Other Partners"

    sub["geo_tier"] = sub["partner_code"].apply(assign_geo_tier)

    fig_donut = go.Figure(go.Pie(
        labels=[
            f"Direct Neighbors (BE, DE, FR) — {neigh_share:.1f}%",
            f"Other EU Member States — {other_eu_share:.1f}%",
            f"Rest of World — {row_share:.1f}%"
        ],
        values=[neigh_val, other_eu_val, row_val],
        hole=0.55,
        marker_colors=[PRIMARY, "#38BDF8", "#94A3B8"],
        textinfo="label+percent",
        hovertemplate="%{label}<br>Value: €%{value:,.0f}<br>Share: %{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRIMARY),
        showlegend=False
    )

    non_eu_sub = sub[~sub['partner_code'].isin(eu_codes)].sort_values('value_eur', ascending=False).head(8).copy()
    non_eu_sub["name_en"] = non_eu_sub["partner_code"].apply(get_country_name)
    fig_non_eu = go.Figure(go.Bar(
        x=non_eu_sub['value_eur'] / 1e6,
        y=non_eu_sub['name_en'],
        orientation='h',
        marker_color="#8B5CF6",
        text=non_eu_sub['market_share_pct'].apply(lambda p: f"{p:.2f}%"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.1f}M (%{text} of all imports)<extra></extra>"
    ))
    apply_plot_theme(fig_non_eu, title="Top Non-EU Strategic Suppliers (Third-Country Exposure)", x_title="Million Euros (€M)")
    fig_non_eu.update_layout(margin=dict(l=10, r=40, t=35, b=30), yaxis=dict(autorange="reversed"))

    # Note: Seasonal flows are analyzed in depth in Q6 Seasonality Lab
    return html.Div([
        create_section_header(
            f"GEOPOLITICAL ORIGINS & REGIONAL EXPOSURE ({selected_year})",
            "Geographic distribution of merchandise imports (EU vs Non-EU partners) and strategic third-country supplier exposure.",
            badge_text="Origins & Partners",
            badge_color=STATEC_NAVY
        ),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("REGIONAL IMPORT ORIGIN EXPOSURE", className="card-title-upper"),
                    dcc.Graph(figure=fig_donut, config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=5),

            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_non_eu, config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=7),
        ])
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 4: STRESS TESTS & SHOCK SIMULATION ENGINE (Adapt & Recover)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_stress(selected_year):
    return html.Div([
        create_section_header(
            "HISTORICAL SHOCK SCENARIOS & SIMULATION",
            "Observed variations in trade flows during historical market disruptions (COVID-19 2020, Energy Shock 2022) and forward maritime simulation.",
            badge_text="Shock Scenarios",
            badge_color=STATEC_NAVY
        ),

        # Scenario Controls Ribbon
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("SHOCK SCENARIO:", className="control-label"),
                    dbc.RadioItems(
                        id="stress-scenario-radio",
                        options=[
                            {"label": "COVID-19 Disruption (2020)", "value": "covid"},
                            {"label": "Energy Shock (2022)", "value": "gas"},
                            {"label": "Maritime Transit Scenario (Model 2026)", "value": "hormuz"},
                        ],
                        value="gas",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-primary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-primary btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=8),

                dbc.Col([
                    html.Label("PORT TRANSIT FILTER:", className="control-label"),
                    dbc.Checklist(
                        id="stress-lookthrough-check",
                        options=[{"label": "Exclude direct BE/NL transit flows", "value": "lookthrough"}],
                        value=[],
                        switch=True,
                        className="fw-semibold text-primary"
                    )
                ], md=4)
            ], align="center")
        ], className="control-ribbon"),

        html.Div(id="stress-test-results-container")
    ])


@callback(
    Output("stress-test-results-container", "children"),
    Input("stress-scenario-radio", "value"),
    Input("stress-lookthrough-check", "value")
)
def update_stress_test_view(scenario, lookthrough_val):
    is_lookthrough = "lookthrough" in (lookthrough_val or [])

    part_df = load_partner_rankings()
    sea_df = load_seasonal_decomposition()

    # Precalculate dynamic scenario metrics from processed datasets
    # 1. COVID (2019 vs 2020)
    p19 = part_df[(part_df["year"] == 2019) & (part_df["flow"] == "IMPORT")].set_index("partner_code")
    p20 = part_df[(part_df["year"] == 2020) & (part_df["flow"] == "IMPORT")].set_index("partner_code")

    covid_shifts = []
    for c_code, c_name in [("DE", "Germany"), ("BE", "Belgium"), ("FR", "France"), ("CN", "China")]:
        s19 = p19.loc[c_code, "market_share_pct"] if c_code in p19.index else 0.0
        s20 = p20.loc[c_code, "market_share_pct"] if c_code in p20.index else 0.0
        covid_shifts.append({
            "country": c_name,
            "pre": f"{s19:.1f}%",
            "post": f"{s20:.1f}%",
            "delta": f"{(s20 - s19):+.1f} pp"
        })

    tot_m = sea_df[(sea_df["product_code"] == "TOTAL") & (sea_df["flow"] == "IMPORT")]
    if not tot_m.empty:
        v19 = tot_m[(tot_m["year"] == 2019) & (tot_m["month"].between(3, 7))]["value_eur"].sum()
        v20 = tot_m[(tot_m["year"] == 2020) & (tot_m["month"].between(3, 7))]["value_eur"].sum()
        cov_drop = ((v20 / v19) - 1.0) * 100 if v19 > 0 else -20.8

        m19_apr = tot_m[(tot_m["year"] == 2019) & (tot_m["month"] == 4)]["value_eur"].iloc[0]
        m20_apr = tot_m[(tot_m["year"] == 2020) & (tot_m["month"] == 4)]["value_eur"].iloc[0]
        apr_drop = ((m20_apr / m19_apr) - 1.0) * 100 if m19_apr > 0 else -41.5
    else:
        cov_drop, apr_drop = -20.8, -41.5

    hhi_19 = (p19["market_share_pct"] ** 2).sum() if not p19.empty else 0.0
    hhi_20 = (p20["market_share_pct"] ** 2).sum() if not p20.empty else 0.0
    cov_hhi_shift = hhi_20 - hhi_19

    # 2. Energy Shock (2021 vs 2022)
    p21 = part_df[(part_df["year"] == 2021) & (part_df["flow"] == "IMPORT")].set_index("partner_code")
    p22 = part_df[(part_df["year"] == 2022) & (part_df["flow"] == "IMPORT")].set_index("partner_code")

    gas_shifts = []
    for c_code, c_name in [("NL", "Netherlands"), ("BE", "Belgium"), ("NO", "Norway"), ("RU", "Russia")]:
        s21 = p21.loc[c_code, "market_share_pct"] if c_code in p21.index else 0.0
        s22 = p22.loc[c_code, "market_share_pct"] if c_code in p22.index else 0.0
        gas_shifts.append({
            "country": c_name,
            "pre": f"{s21:.1f}%",
            "post": f"{s22:.1f}%",
            "delta": f"{(s22 - s21):+.1f} pp"
        })

    val_21 = p21["value_eur"].sum() if not p21.empty else 1.0
    val_22 = p22["value_eur"].sum() if not p22.empty else 1.0
    gas_val_change = ((val_22 / val_21) - 1.0) * 100

    hhi_21 = (p21["market_share_pct"] ** 2).sum() if not p21.empty else 0.0
    hhi_22 = (p22["market_share_pct"] ** 2).sum() if not p22.empty else 0.0
    gas_hhi_shift = hhi_22 - hhi_21

    # 3. Model Simulation (Maritime Transit Disruption)
    base_yr = part_df["year"].max()
    p_base = part_df[(part_df["year"] == base_yr) & (part_df["flow"] == "IMPORT")].set_index("partner_code")
    maritime_shifts = []
    for c_code, c_name, factor in [("BE", "Belgium", -0.09), ("US", "United States", +1.3), ("NO", "Norway", +1.1), ("AE", "United Arab Emirates", -1.0)]:
        s_base = p_base.loc[c_code, "market_share_pct"] if c_code in p_base.index else 1.5
        s_sim = max(0.0, s_base * (1.0 + factor))
        maritime_shifts.append({
            "country": c_name,
            "pre": f"{s_base:.1f}%",
            "post": f"{s_sim:.1f}%",
            "delta": f"{(s_sim - s_base):+.1f} pp"
        })

    sim_drop_pct = -11.5
    sim_hhi_shift = 1120

    scenarios_meta = {
        "covid": {
            "title": "COVID-19 Disruption Period (March 2020 – July 2020)",
            "drop": f"{cov_drop:+.1f}%",
            "hhi_shift": f"{cov_hhi_shift:+.0f} pts",
            "weakest": f"April 2020 ({apr_drop:+.1f}% YoY)",
            "desc": "Observed variation in monthly trade flows during the initial months of the COVID-19 pandemic.",
            "shifts": covid_shifts
        },
        "gas": {
            "title": "Energy Market Shock (February 2022 – December 2022)",
            "drop": f"{gas_val_change:+.1f}% (Value)",
            "hhi_shift": f"{gas_hhi_shift:+.0f} pts",
            "weakest": "August 2022",
            "desc": "Observed variation in trade values following wholesale energy price movements in 2022.",
            "shifts": gas_shifts
        },
        "hormuz": {
            "title": "Simulated Maritime Transit Scenario (Model Projection)",
            "drop": f"{sim_drop_pct:+.1f}% (Projected)",
            "hhi_shift": f"{sim_hhi_shift:+.0f} pts",
            "weakest": "Month 2 (Simulated)",
            "desc": "Model projection simulating a contraction in global maritime liquid fuel transit.",
            "shifts": maritime_shifts
        }
    }

    meta = scenarios_meta.get(scenario, scenarios_meta["gas"])

    kpi_cards = dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("TOTAL TRADE VARIATION", className="kpi-label"),
                html.H4(meta["drop"], className="kpi-val kpi-val-danger"),
                html.Small("Observed 4-month post-shock change", className="kpi-caption")
            ], className="compact-kpi-tile")
        ], md=4, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Span("CONCENTRATION (HHI) SHIFT", className="kpi-label"),
                html.H4(meta["hhi_shift"], className="kpi-val kpi-val-warning"),
                html.Small("Change in supplier concentration (HHI)", className="kpi-caption")
            ], className="compact-kpi-tile")
        ], md=4, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Span("PEAK OBSERVED IMPACT", className="kpi-label"),
                html.H5(meta["weakest"], className="kpi-val kpi-val-navy"),
                html.Small("Lowest monthly point during period", className="kpi-caption")
            ], className="compact-kpi-tile")
        ], md=4, sm=12, className="mb-2"),
    ], className="mb-3")

    # Shift table
    table_rows = [
        html.Tr([
            html.Td(html.Strong(s["country"])),
            html.Td(s["pre"], className="text-muted-custom"),
            html.Td(s["post"], className="fw-semibold"),
            html.Td(html.Span(s["delta"], className="badge " + ("bg-success" if s["delta"].startswith("+") else "bg-danger")))
        ])
        for s in meta["shifts"]
    ]

    table_card = html.Div([
        html.H6("PARTNER IMPORT SHARE VARIATIONS", className="card-title-upper"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Partner Country"), html.Th("Pre-Period Share"), html.Th("Post-Period Share"), html.Th("Net Variation (Δ)")
            ])),
            html.Tbody(table_rows)
        ], className="table table-hover mb-0")
    ], className="dash-card")

    info_card = html.Div([
        html.H6(meta["title"].upper(), className="card-title-upper"),
        html.P(meta["desc"], className="text-muted-custom mb-0 small"),
    ], className="notice-card")

    return html.Div([
        info_card,
        kpi_cards,
        table_card
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 5: Q1 — TRADING PARTNERS & WORLD FLOW
# ───────────────────────────────────────────────────────────────────────────
def render_tab_partners(selected_year):
    return html.Div([
        create_section_header(
            f"Q1: TRADING PARTNERS & BILATERAL FLOWS ({selected_year})",
            "Who are Luxembourg's main trading partners? How have they evolved over time? Click any country bar below to instantly inspect top products traded with that country.",
            badge_text="Research Question Q1",
            badge_color=STATEC_BLUE
        ),

        # Controls Ribbon (Imports always on left & default)
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("TRADE FLOW:", className="control-label"),
                    dbc.RadioItems(
                        id="q1-flow-radio",
                        options=[
                            {"label": "Imports (Suppliers)", "value": "IMPORT"},
                            {"label": "Exports (Destinations)", "value": "EXPORT"},
                        ],
                        value="IMPORT",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=4, sm=6, className="mb-2 mb-md-0"),

                dbc.Col([
                    html.Label("GEOGRAPHIC SCOPE:", className="control-label"),
                    dbc.RadioItems(
                        id="q1-scope-radio",
                        options=[
                            {"label": "World", "value": "world"},
                            {"label": "Europe (EU-27)", "value": "europe"},
                        ],
                        value="world",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-dark btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-dark btn-sm px-2 py-1 text-white fw-bold",
                    )
                ], md=3, sm=6, className="mb-2 mb-md-0"),

                dbc.Col([
                    html.Label("METRIC:", className="control-label"),
                    dbc.RadioItems(
                        id="q1-metric-radio",
                        options=[
                            {"label": "Value (€)", "value": "value"},
                            {"label": "Share (%)", "value": "share"},
                        ],
                        value="value",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-2 py-1 text-white fw-bold",
                    )
                ], md=3, sm=6),

                dbc.Col([
                    html.Label("MAP SIZE:", className="control-label"),
                    dbc.Button(
                        [html.I(className="bi bi-arrows-fullscreen me-1"), "Toggle Map Size"],
                        id="q1-map-toggle-btn",
                        color="light",
                        size="sm",
                        className="border fw-bold d-block w-100 small",
                    )
                ], md=2, sm=6)
            ], align="center")
        ], className="control-ribbon"),

        dcc.Store(id="q1-selected-partner", data="DE"),
        dcc.Store(id="q1-map-expanded", data=False),

        # Main Layout: Priority to Bar Charts & Data Table, Map is Secondary
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6(id="q1-barchart-title", className="card-title-upper mb-0"),
                        html.Span("💡 Click any bar to inspect country products", className="small text-primary fw-bold")
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    dcc.Graph(id="q1-top-partners-bar", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=7),

            dbc.Col([
                html.Div(id="q1-partner-spotlight-panel", className="h-100")
            ], md=5)
        ]),

        # Map Row (Compact by default, expandable on demand)
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6("GLOBAL GEOGRAPHIC FLOW MAP", className="card-title-upper mb-0"),
                        html.Small("Hover to view country trade volume • Click to select", className="kpi-caption")
                    ], className="d-flex justify-content-between align-items-center mb-1"),
                    dcc.Graph(id="q1-world-map", config={"displayModeBar": False})
                ], className="dash-card")
            ], md=12)
        ])
    ])


@callback(
    Output("q1-map-expanded", "data"),
    Input("q1-map-toggle-btn", "n_clicks"),
    State("q1-map-expanded", "data"),
    prevent_initial_call=True
)
def toggle_q1_map_size(n, current_state):
    return not current_state


@callback(
    Output("q1-selected-partner", "data"),
    Input("q1-top-partners-bar", "clickData"),
    Input("q1-world-map", "clickData"),
    Input("q1-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    State("q1-selected-partner", "data")
)
def update_q1_selected_partner(bar_click, map_click, flow, year, current_p):
    partners_df = load_partner_rankings()
    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].sort_values("rank")
    default_p = sub.iloc[0]["partner_code"] if not sub.empty else "DE"

    try:
        ctx = dash.callback_context
        if not ctx or not ctx.triggered:
            return default_p
        trig_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trig_id in ["q1-flow-radio", "global-year-dropdown"]:
            return default_p

        if trig_id == "q1-top-partners-bar" and bar_click:
            pt = bar_click["points"][0]
            if "customdata" in pt and pt["customdata"] is not None:
                return str(pt["customdata"]).strip().upper()
        elif trig_id == "q1-world-map" and map_click:
            pt = map_click["points"][0]
            if "customdata" in pt and pt["customdata"] is not None:
                c = pt["customdata"]
                res = c[0] if isinstance(c, (list, tuple, np.ndarray)) else str(c)
                return str(res).strip().upper()
    except Exception:
        pass
    return current_p or default_p


@callback(
    Output("q1-barchart-title", "children"),
    Output("q1-top-partners-bar", "figure"),
    Output("q1-world-map", "figure"),
    Output("q1-world-map", "style"),
    Input("q1-flow-radio", "value"),
    Input("q1-scope-radio", "value"),
    Input("q1-metric-radio", "value"),
    Input("q1-selected-partner", "data"),
    Input("q1-map-expanded", "data"),
    Input("global-year-dropdown", "value")
)
def update_q1_charts(flow, scope, metric, selected_partner, is_expanded, year):
    partners_df = load_partner_rankings()
    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].copy()
    if sub.empty:
        sub = partners_df[(partners_df["year"] == partners_df["year"].max()) & (partners_df["flow"] == flow)].copy()

    top10 = sub.sort_values("rank").head(10).copy()
    top10["country_name_en"] = top10["partner_code"].apply(get_country_name)

    bar_colors = [STATEC_YELLOW if c == selected_partner else (SECONDARY if flow == "IMPORT" else PRIMARY) for c in top10["partner_code"]]
    x_col = top10["market_share_pct"] if metric == "share" else (top10["value_eur"] / 1e6)

    fig_bar = go.Figure(go.Bar(
        x=x_col,
        y=top10["country_name_en"],
        orientation="h",
        marker_color=bar_colors,
        customdata=top10["partner_code"],
        text=[f"{p:.1f}%" if metric == "share" else fmt_eur(v) for p, v in zip(top10["market_share_pct"], top10["value_eur"])],
        textposition="outside",
        hovertemplate="<b>%{y} (%{customdata})</b><br>Value: " + ("%{x:.2f}%" if metric == "share" else "€%{x:,.1f}M") + "<extra></extra>"
    ))
    apply_plot_theme(fig_bar, x_title="Market Share (%)" if metric == "share" else "Million Euros (€M)")
    fig_bar.update_layout(margin=dict(l=10, r=40, t=10, b=30), yaxis=dict(autorange="reversed"))

    # Map
    sub_map = add_iso3_column(sub).dropna(subset=["iso3"]).copy()
    sub_map["color_val"] = np.log10(np.maximum(10000.0, sub_map["value_eur"]))
    cmin = 6.0
    cmax = max(7.0, sub_map["color_val"].max())

    fig_map = go.Figure(go.Choropleth(
        locations=sub_map["iso3"],
        z=sub_map["color_val"],
        text=sub_map["partner_code"].apply(get_country_name),
        customdata=np.stack([sub_map["partner_code"], sub_map["value_eur"], sub_map["market_share_pct"]], axis=-1),
        hovertemplate="<b>%{text} (%{customdata[0]})</b><br>Volume: €%{customdata[1]:,.0f}<br>Share: %{customdata[2]:.2f}%<extra></extra>",
        colorscale=[[0.0, "#EDE9FE"], [0.2, "#DDD6FE"], [0.4, "#A78BFA"], [0.65, "#6366F1"], [0.85, "#4338CA"], [1.0, "#1E1B4B"]],
        zmin=cmin, zmax=cmax,
        showscale=True,
        colorbar=dict(title=dict(text="Log10 €", font=dict(size=10)), thickness=10, len=0.7)
    ))

    sel_iso3 = ISO2_TO_ISO3.get(selected_partner)
    if sel_iso3:
        fig_map.add_trace(go.Choropleth(
            locations=[sel_iso3],
            z=[cmax],
            colorscale=[[0.0, STATEC_YELLOW], [1.0, STATEC_YELLOW]],
            showscale=False,
            hoverinfo="skip",
            marker_line_color=STATEC_YELLOW,
            marker_line_width=3,
        ))

    apply_map_theme(fig_map, scope=scope)
    map_height = 520 if is_expanded else 290
    fig_map.update_layout(height=map_height, margin=dict(l=0, r=0, t=10, b=0), clickmode="event+select")

    bar_title = f"Top 10 {flow.capitalize()} Partners in {year}"
    return bar_title, fig_bar, fig_map, {"height": f"{map_height}px"}


@callback(
    Output("q1-partner-spotlight-panel", "children"),
    Input("q1-selected-partner", "data"),
    Input("q1-flow-radio", "value"),
    Input("global-year-dropdown", "value")
)
def update_q1_spotlight_panel(partner_code, flow, year):
    partner_code = str(partner_code or "DE").upper()
    country_name = get_country_name(partner_code)

    pp_df = load_product_partners()
    sub_prod = pp_df[(pp_df["partner_code"] == partner_code) & (pp_df["flow"] == flow) & (pp_df["year"] == year)]
    if sub_prod.empty:
        sub_prod = pp_df[(pp_df["partner_code"] == partner_code) & (pp_df["flow"] == flow) & (pp_df["year"] == pp_df["year"].max())]

    top_prods_bars = []
    tot_p_val = sub_prod["value_eur"].sum() if not sub_prod.empty else 0

    if not sub_prod.empty:
        top_prods = sub_prod.sort_values("value_eur", ascending=False).head(5)
        for _, p in top_prods.iterrows():
            sh = (p["value_eur"] / tot_p_val * 100) if tot_p_val > 0 else 0
            top_prods_bars.append(html.Div([
                html.Div([
                    html.Span(f"Ch. {p['hs2_code']}: {p['hs2_name'][:30]}", className="spotlight-stat-label"),
                    html.Span(f"{fmt_eur(p['value_eur'])} ({sh:.1f}%)", className="spotlight-stat-val")
                ], className="d-flex justify-content-between mb-1"),
                dbc.Progress(value=sh, color="primary" if flow == "EXPORT" else "dark", className="progress-xs mb-2")
            ]))
    else:
        top_prods_bars.append(html.P("Detailed product breakdown not available.", className="text-muted small"))

    # 25-Year bilateral trend
    partners_df = load_partner_rankings()
    hist_sub = partners_df[(partners_df["partner_code"] == partner_code) & (partners_df["flow"] == flow)].sort_values("year")
    fig_hist = go.Figure()
    if not hist_sub.empty:
        fig_hist.add_trace(go.Scatter(
            x=hist_sub["year"], y=hist_sub["value_eur"] / 1e6,
            mode="lines+markers",
            line=dict(color=SECONDARY if flow == "IMPORT" else PRIMARY, width=2.5),
            marker=dict(size=4),
            hovertemplate="Year %{x}: €%{y:,.1f}M<extra></extra>"
        ))
    apply_plot_theme(fig_hist, title=f"25-Year Bilateral Trajectory with {country_name} (€M)")
    fig_hist.update_layout(height=180, margin=dict(l=10, r=20, t=30, b=25))

    return html.Div([
        html.Div([
            html.Div([
                create_icon_badge("bi bi-geo-alt-fill", color="#B45309", bg="#FEF3C7", size=15, box_size=32),
                html.Div([
                    html.H6(f"{country_name} ({partner_code})", className="card-title-upper mb-0"),
                    html.Small(f"Total {flow.capitalize()}: {fmt_eur(tot_p_val)} in {year}", className="text-muted small")
                ], className="ms-2")
            ], className="d-flex align-items-center mb-3"),

            html.Span(f"TOP PRODUCTS TRADED WITH {country_name.upper()}", className="spotlight-section-title"),
            html.Div(top_prods_bars, className="mb-3"),

            dcc.Graph(figure=fig_hist, config={"displayModeBar": False})
        ], className="spotlight-card")
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 6: Q2 — PRODUCT CATEGORIES & STRUCTURAL TRANSFORMATION
# ───────────────────────────────────────────────────────────────────────────
def render_tab_products(selected_year):
    return html.Div([
        create_section_header(
            f"Q2: MAIN PRODUCT CATEGORIES & STRUCTURAL SHIFT ({selected_year})",
            "What are the main categories of goods traded? How have these patterns transformed over 25 years (from steel dominance to advanced automotive, machinery, and pharma)? Click any product bar to see its top partner countries.",
            badge_text="Research Question Q2",
            badge_color=STATEC_BLUE
        ),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("TRADE FLOW:", className="control-label"),
                    dbc.RadioItems(
                        id="q2-flow-radio",
                        options=[
                            {"label": "Imports (Inward Basket)", "value": "IMPORT"},
                            {"label": "Exports (Outward Basket)", "value": "EXPORT"},
                        ],
                        value="IMPORT",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=5),

                dbc.Col([
                    html.Label("GRANULARITY:", className="control-label"),
                    dbc.RadioItems(
                        id="q2-granularity-radio",
                        options=[
                            {"label": "HS2 Chapters (2-Digit)", "value": 2},
                            {"label": "HS4 Subheadings (4-Digit)", "value": 4},
                        ],
                        value=2,
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-dark btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-dark btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=7)
            ], align="center")
        ], className="control-ribbon"),

        dcc.Store(id="q2-selected-product", data="87"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6(id="q2-barchart-title", className="card-title-upper mb-0"),
                        html.Span("💡 Click any bar to inspect product suppliers", className="small text-primary fw-bold")
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    dcc.Graph(id="q2-top-products-bar", config={"displayModeBar": False}, className="chart-h-390")
                ], className="dash-card")
            ], md=7),

            dbc.Col([
                html.Div(id="q2-product-spotlight-panel", className="h-100")
            ], md=5)
        ]),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("25-YEAR STRUCTURAL TRANSFORMATION OF PRODUCT EXPORTS (2000–2025)", className="card-title-upper"),
                    dcc.Graph(id="q2-shift-chart", config={"displayModeBar": False}, className="chart-h-300")
                ], className="dash-card")
            ], md=12)
        ])
    ])


@callback(
    Output("q2-selected-product", "data"),
    Input("q2-top-products-bar", "clickData"),
    Input("q2-flow-radio", "value"),
    Input("q2-granularity-radio", "value"),
    Input("global-year-dropdown", "value"),
    State("q2-selected-product", "data")
)
def update_q2_selected_product(bar_click, flow, granularity, year, current_prod):
    if granularity == 4:
        hs4_df = load_hs4_product_rankings()
        sub = hs4_df[(hs4_df["year"] == year) & (hs4_df["flow"] == flow)].sort_values("value_eur", ascending=False)
        default_prod = str(sub.iloc[0]["hs4_code"]) if not sub.empty else "8703"
    else:
        prod_df = load_product_rankings()
        sub = prod_df[(prod_df["year"] == year) & (prod_df["flow"] == flow)].sort_values("value_eur", ascending=False)
        default_prod = str(sub.iloc[0]["hs2_code"]) if not sub.empty else "87"

    try:
        ctx = dash.callback_context
        if not ctx or not ctx.triggered:
            return default_prod
        trig_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trig_id in ["q2-flow-radio", "q2-granularity-radio", "global-year-dropdown"]:
            return default_prod

        if trig_id == "q2-top-products-bar" and bar_click:
            pt = bar_click["points"][0]
            if "customdata" in pt and pt["customdata"] is not None:
                return str(pt["customdata"]).strip()
    except Exception:
        pass
    return current_prod or default_prod


@callback(
    Output("q2-barchart-title", "children"),
    Output("q2-top-products-bar", "figure"),
    Output("q2-shift-chart", "figure"),
    Input("q2-flow-radio", "value"),
    Input("q2-granularity-radio", "value"),
    Input("q2-selected-product", "data"),
    Input("global-year-dropdown", "value")
)
def update_q2_charts(flow, granularity, selected_prod, year):
    if granularity == 4:
        hs4_df = load_hs4_product_rankings()
        sub = hs4_df[(hs4_df["year"] == year) & (hs4_df["flow"] == flow)].copy()
        if sub.empty:
            sub = hs4_df[(hs4_df["year"] == hs4_df["year"].max()) & (hs4_df["flow"] == flow)].copy()
        top = sub.sort_values("value_eur", ascending=False).head(10).copy()
        top["label"] = "HS " + top["hs4_code"] + ": " + top["hs4_name"].apply(lambda s: str(s)[:28] + ".." if len(str(s)) > 28 else str(s))
        code_col = top["hs4_code"]
    else:
        prod_df = load_product_rankings()
        sub = prod_df[(prod_df["year"] == year) & (prod_df["flow"] == flow)].copy()
        if sub.empty:
            sub = prod_df[(prod_df["year"] == prod_df["year"].max()) & (prod_df["flow"] == flow)].copy()
        top = sub.sort_values("value_eur", ascending=False).head(10).copy()
        top["label"] = "Ch. " + top["hs2_code"] + ": " + top["hs2_name"].apply(lambda s: str(s)[:28] + ".." if len(str(s)) > 28 else str(s))
        code_col = top["hs2_code"]

    bar_colors = [STATEC_YELLOW if str(c) == str(selected_prod) else (SECONDARY if flow == "IMPORT" else PRIMARY) for c in code_col]

    fig_bar = go.Figure(go.Bar(
        x=top["value_eur"] / 1e6,
        y=top["label"],
        orientation="h",
        marker_color=bar_colors,
        customdata=code_col,
        text=[fmt_eur(v) for v in top["value_eur"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Trade Value: €%{x:,.1f}M<extra></extra>"
    ))
    apply_plot_theme(fig_bar, x_title="Million Euros (€M)")
    fig_bar.update_layout(margin=dict(l=10, r=40, t=10, b=30), yaxis=dict(autorange="reversed"))

    # Structural shift chart (Iron/Steel 72 vs Machinery 84 vs Vehicles 87 vs Plastics 39)
    all_prod = load_product_rankings()
    key_chs = ["72", "84", "87", "39", "30"]
    ch_names = {"72": "Iron & Steel (72)", "84": "Machinery (84)", "87": "Vehicles (87)", "39": "Plastics (39)", "30": "Pharma (30)"}
    fig_shift = go.Figure()
    for ch in key_chs:
        c_sub = all_prod[(all_prod["hs2_code"] == ch) & (all_prod["flow"] == flow)].sort_values("year")
        if not c_sub.empty:
            fig_shift.add_trace(go.Scatter(
                x=c_sub["year"], y=c_sub["value_eur"] / 1e6,
                name=ch_names.get(ch, ch),
                mode="lines+markers",
                line=dict(width=2.5),
                marker=dict(size=4),
                hovertemplate="%{x}: €%{y:,.1f}M<extra></extra>"
            ))
    apply_plot_theme(fig_shift, title=f"25-Year Sector Evolution ({flow.capitalize()}) (€M)", y_title="Million Euros (€M)")
    fig_shift.update_layout(margin=dict(l=10, r=20, t=30, b=30))

    title = f"Top 10 Traded Product {'Subheadings (HS4)' if granularity == 4 else 'Chapters (HS2)'} in {year}"
    return title, fig_bar, fig_shift


@callback(
    Output("q2-product-spotlight-panel", "children"),
    Input("q2-selected-product", "data"),
    Input("q2-flow-radio", "value"),
    Input("global-year-dropdown", "value")
)
def update_q2_spotlight_panel(prod_code, flow, year):
    prod_code = str(prod_code or "87")[:2].zfill(2)

    pp_df = load_product_partners()
    sub = pp_df[(pp_df["hs2_code"] == prod_code) & (pp_df["flow"] == flow) & (pp_df["year"] == year)]
    if sub.empty:
        sub = pp_df[(pp_df["hs2_code"] == prod_code) & (pp_df["flow"] == flow) & (pp_df["year"] == pp_df["year"].max())]

    prod_name = sub["hs2_name"].iloc[0] if not sub.empty else f"Chapter {prod_code}"
    tot_val = sub["value_eur"].sum() if not sub.empty else 0

    top_suppliers = []
    if not sub.empty:
        top_p = sub.sort_values("value_eur", ascending=False).head(5)
        for _, p in top_p.iterrows():
            sh = (p["value_eur"] / tot_val * 100) if tot_val > 0 else 0
            c_name = get_country_name(p["partner_code"])
            top_suppliers.append(html.Div([
                html.Div([
                    html.Span(f"{c_name} ({p['partner_code']})", className="spotlight-stat-label"),
                    html.Span(f"{fmt_eur(p['value_eur'])} ({sh:.1f}%)", className="spotlight-stat-val")
                ], className="d-flex justify-content-between mb-1"),
                dbc.Progress(value=sh, color="primary" if flow == "EXPORT" else "dark", className="progress-xs mb-2")
            ]))
    else:
        top_suppliers.append(html.P("Supplier breakdown not available.", className="text-muted small"))

    hhi_score = (sub["supplier_share_pct"] ** 2).sum() if ("supplier_share_pct" in sub.columns and not sub.empty) else 0

    return html.Div([
        html.Div([
            html.Div([
                create_icon_badge("bi bi-box-seam-fill", color="#065F46", bg="#DCFCE7", size=15, box_size=32),
                html.Div([
                    html.H6(f"Ch. {prod_code} — {prod_name[:26]}", className="card-title-upper mb-0"),
                    html.Small(f"Total Traded Value: {fmt_eur(tot_val)} in {year}", className="text-muted small")
                ], className="ms-2")
            ], className="d-flex align-items-center mb-2"),

            html.Div([
                html.Span("Supplier Concentration: ", className="text-muted small"),
                get_concentration_badge(hhi_score)
            ], className="d-flex align-items-center justify-content-between mb-3"),

            html.Span(f"TOP PARTNER COUNTRIES FOR CH. {prod_code}", className="spotlight-section-title"),
            html.Div(top_suppliers)
        ], className="spotlight-card")
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 7: Q3 — PRINCIPAL PARTNERS FOR A GIVEN PRODUCT
# ───────────────────────────────────────────────────────────────────────────
def render_tab_q3_product_partners(selected_year):
    prod_df = load_product_rankings()
    options = []
    def_prod = "87"
    if not prod_df.empty:
        u = prod_df[["hs2_code", "hs2_name"]].drop_duplicates().sort_values("hs2_code")
        options = [{"label": f"Ch. {r['hs2_code']} — {r['hs2_name'][:35]}", "value": str(r["hs2_code"])} for _, r in u.iterrows()]
        # Default to #1 product for selected_year (IMPORT flow)
        sub_yr = prod_df[(prod_df["year"] == selected_year) & (prod_df["flow"] == "IMPORT")].sort_values("value_eur", ascending=False)
        if not sub_yr.empty:
            def_prod = str(sub_yr.iloc[0]["hs2_code"])
        elif options:
            def_prod = options[0]["value"]

    return html.Div([
        create_section_header(
            f"Q3: PRINCIPAL PARTNERS BY PRODUCT CATEGORY ({selected_year})",
            "For a given product category, who are Luxembourg's principal trading partners? Inspect supplier concentration (HHI) and geographic origin breakdown.",
            badge_text="Research Question Q3",
            badge_color=STATEC_BLUE
        ),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("SELECT PRODUCT CATEGORY:", className="control-label"),
                    dcc.Dropdown(
                        id="q3-product-dropdown",
                        options=options,
                        value=def_prod,
                        clearable=False,
                        className="fw-semibold small"
                    )
                ], md=6),

                dbc.Col([
                    html.Label("TRADE FLOW:", className="control-label"),
                    dbc.RadioItems(
                        id="q3-flow-radio",
                        options=[
                            {"label": "Imports (Suppliers)", "value": "IMPORT"},
                            {"label": "Exports (Destinations)", "value": "EXPORT"},
                        ],
                        value="IMPORT",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=6)
            ], align="center")
        ], className="control-ribbon"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(id="q3-barchart-title", className="card-title-upper"),
                    dcc.Graph(id="q3-suppliers-bar", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=7),

            dbc.Col([
                html.Div([
                    html.H6("SUPPLIER GEOGRAPHIC DISTRIBUTION", className="card-title-upper"),
                    dcc.Graph(id="q3-suppliers-map", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=5)
        ])
    ])


@callback(
    Output("q3-barchart-title", "children"),
    Output("q3-suppliers-bar", "figure"),
    Output("q3-suppliers-map", "figure"),
    Input("q3-product-dropdown", "value"),
    Input("q3-flow-radio", "value"),
    Input("global-year-dropdown", "value")
)
def update_q3_charts(product_code, flow, year):
    product_code = str(product_code or "87")[:2].zfill(2)
    pp_df = load_product_partners()
    sub = pp_df[(pp_df["hs2_code"] == product_code) & (pp_df["flow"] == flow) & (pp_df["year"] == year)].copy()
    if sub.empty:
        sub = pp_df[(pp_df["hs2_code"] == product_code) & (pp_df["flow"] == flow) & (pp_df["year"] == pp_df["year"].max())].copy()

    top10 = sub.sort_values("value_eur", ascending=False).head(10).copy()
    top10["country_name_en"] = top10["partner_code"].apply(get_country_name)

    fig_bar = go.Figure(go.Bar(
        x=top10["value_eur"] / 1e6,
        y=top10["country_name_en"],
        orientation="h",
        marker_color=SECONDARY if flow == "IMPORT" else PRIMARY,
        text=[fmt_eur(v) for v in top10["value_eur"]],
        textposition="outside",
        hovertemplate="<b>%{y} (%{customdata})</b><br>Value: €%{x:,.1f}M<extra></extra>",
        customdata=top10["partner_code"]
    ))
    apply_plot_theme(fig_bar, x_title="Million Euros (€M)")
    fig_bar.update_layout(margin=dict(l=10, r=40, t=10, b=30), yaxis=dict(autorange="reversed"))

    # Map
    sub_map = add_iso3_column(sub).dropna(subset=["iso3"]).copy()
    sub_map["color_val"] = np.log10(np.maximum(1000.0, sub_map["value_eur"]))
    fig_map = go.Figure(go.Choropleth(
        locations=sub_map["iso3"],
        z=sub_map["color_val"],
        text=sub_map["partner_code"].apply(get_country_name),
        customdata=np.stack([sub_map["partner_code"], sub_map["value_eur"]], axis=-1),
        hovertemplate="<b>%{text}</b><br>Volume: €%{customdata[1]:,.0f}<extra></extra>",
        colorscale=[[0.0, "#EDE9FE"], [0.4, "#A78BFA"], [0.8, "#6366F1"], [1.0, "#1E1B4B"]],
        showscale=False
    ))
    apply_map_theme(fig_map, scope="europe")
    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))

    prod_name = sub["hs2_name"].iloc[0] if not sub.empty else f"Ch. {product_code}"
    title = f"Top 10 Partners for Ch. {product_code} ({prod_name[:25]}) in {year}"
    return title, fig_bar, fig_map


# ───────────────────────────────────────────────────────────────────────────
# TAB 8: Q4 — DETAILED PARTNER TARIFF DRILL-DOWN (HS2 → HS4 → CN8)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_q4_drilldown(selected_year):
    partners_df = load_partner_rankings()
    sub_yr = partners_df[(partners_df["year"] == selected_year) & (partners_df["flow"] == "IMPORT")].sort_values("rank")
    if not sub_yr.empty:
        top_p = sub_yr["partner_code"].head(15).tolist()
    else:
        top_p = ["DE", "BE", "FR", "NL", "US", "CN", "IT", "GB", "PL", "CH"]
    options = [{"label": f"{get_country_name(c)} ({c})", "value": c} for c in top_p]
    def_p = top_p[0] if top_p else "DE"

    return html.Div([
        create_section_header(
            f"Q4: PARTNER TARIFF LINES DRILL-DOWN (HS2 → HS4 → CN8) ({selected_year})",
            "For a given partner country, what are the main goods traded? Displays increasingly detailed levels of information (up to 8-digit CN8 codes) with a significance threshold filter to eliminate minor noise and confidential cells.",
            badge_text="Research Question Q4",
            badge_color=STATEC_BLUE
        ),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("PARTNER COUNTRY:", className="control-label"),
                    dcc.Dropdown(
                        id="q4-partner-dropdown",
                        options=options,
                        value=def_p,
                        clearable=False,
                        className="fw-semibold small"
                    )
                ], md=3),

                dbc.Col([
                    html.Label("TRADE FLOW:", className="control-label"),
                    dbc.RadioItems(
                        id="q4-flow-radio",
                        options=[
                            {"label": "Imports", "value": "IMPORT"},
                            {"label": "Exports", "value": "EXPORT"},
                        ],
                        value="IMPORT",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=3),

                dbc.Col([
                    html.Label("TARIFF GRANULARITY LEVEL:", className="control-label"),
                    dbc.RadioItems(
                        id="q4-level-radio",
                        options=[
                            {"label": "HS2 (Chapters)", "value": 2},
                            {"label": "HS4 (Subheadings)", "value": 4},
                            {"label": "CN8 (Detailed 8-Digit)", "value": 8},
                        ],
                        value=4,
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-dark btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-dark btn-sm px-2 py-1 text-white fw-bold",
                    )
                ], md=3),

                dbc.Col([
                    html.Label("SIGNIFICANCE FILTER:", className="control-label"),
                    dcc.Dropdown(
                        id="q4-threshold-dropdown",
                        options=[
                            {"label": "Top 15 Traded Lines", "value": 15},
                            {"label": "Top 25 Traded Lines", "value": 25},
                            {"label": "Value > €500k only", "value": 500000},
                            {"label": "Value > €1M only", "value": 1000000},
                        ],
                        value=15,
                        clearable=False,
                        className="fw-semibold small"
                    )
                ], md=3)
            ], align="center")
        ], className="control-ribbon"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(id="q4-chart-title", className="card-title-upper"),
                    dcc.Graph(id="q4-drilldown-bar", config={"displayModeBar": False}, className="chart-h-460")
                ], className="dash-card")
            ], md=12)
        ])
    ])


@callback(
    Output("q4-chart-title", "children"),
    Output("q4-drilldown-bar", "figure"),
    Input("q4-partner-dropdown", "value"),
    Input("q4-flow-radio", "value"),
    Input("q4-level-radio", "value"),
    Input("q4-threshold-dropdown", "value"),
    Input("global-year-dropdown", "value")
)
def update_q4_chart(partner_code, flow, level, threshold, year):
    partner_code = str(partner_code or "DE").upper()
    level = int(level or 4)

    if level == 8:
        df = load_drilldown_lvl8()
    elif level == 4:
        df = load_drilldown_lvl4()
    else:
        df = load_drilldown_lvl2()

    sub = df[(df["partner_code"] == partner_code) & (df["flow"] == flow)].copy()
    if sub.empty:
        # Fallback to level 2
        df2 = load_drilldown_lvl2()
        sub = df2[(df2["partner_code"] == partner_code) & (df2["flow"] == flow)].copy()
        level = 2

    if threshold in [15, 25]:
        sub = sub.sort_values("value_eur", ascending=False).head(int(threshold)).copy()
    else:
        sub = sub[sub["value_eur"] >= float(threshold)].sort_values("value_eur", ascending=False).head(30).copy()

    sub["label"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: str(s)[:45] + ".." if len(str(s)) > 45 else str(s))

    fig = go.Figure(go.Bar(
        x=sub["value_eur"] / 1e6,
        y=sub["label"],
        orientation="h",
        marker_color=SECONDARY if flow == "IMPORT" else PRIMARY,
        text=[fmt_eur(v) for v in sub["value_eur"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Value: €%{x:,.2f}M<extra></extra>"
    ))
    apply_plot_theme(fig, x_title="Million Euros (€M)")
    fig.update_layout(margin=dict(l=10, r=40, t=10, b=30), yaxis=dict(autorange="reversed"))

    title = f"{get_country_name(partner_code)} ({partner_code}) — Level {level} Tariff Breakdown ({flow.capitalize()})"
    return title, fig


# ───────────────────────────────────────────────────────────────────────────
# TAB 9: Q5 — REGIONAL PEER BENCHMARKING
# ───────────────────────────────────────────────────────────────────────────
def render_tab_benchmarks(selected_year):
    bench_df = load_country_benchmarks()
    if bench_df.empty:
        return html.Div("Peer benchmarks not available.")

    fig_index = go.Figure()
    country_colors = {"LU": STATEC_YELLOW, "DE": STATEC_NAVY, "FR": STATEC_BLUE, "BE": "#DC2626", "NL": "#D97706"}
    country_names = {"LU": "Luxembourg", "DE": "Germany", "FR": "France", "BE": "Belgium", "NL": "Netherlands"}

    for c in ["LU", "DE", "FR", "BE", "NL"]:
        c_sub = bench_df[bench_df["reporter_code"] == c].sort_values("year")
        if not c_sub.empty and "volume_index_2000" in c_sub.columns:
            fig_index.add_trace(go.Scatter(
                x=c_sub["year"], y=c_sub["volume_index_2000"],
                name=country_names.get(c, c),
                mode="lines+markers" if c == "LU" else "lines",
                line=dict(color=country_colors.get(c, STATEC_GRAY), width=3.5 if c == "LU" else 2),
                marker=dict(size=6 if c == "LU" else 0),
                hovertemplate="%{x}: Index %{y:.1f}<extra></extra>"
            ))
    apply_plot_theme(fig_index, title="Merchandise Trade Volume Growth Index (Base 100 = Year 2000)", y_title="Index (2000 = 100)", dtick_x=2, hovermode="x unified")

    sub_yr = bench_df[bench_df["year"] == selected_year]
    if sub_yr.empty:
        sub_yr = bench_df[bench_df["year"] == bench_df["year"].max()]

    sub_yr = sub_yr.copy()
    sub_yr["name"] = sub_yr["reporter_code"].apply(lambda r: country_names.get(r, r))
    fig_cov = go.Figure(go.Bar(
        x=sub_yr["coverage_ratio_pct"],
        y=sub_yr["name"],
        orientation="h",
        marker_color=[STATEC_YELLOW if r == "LU" else (SUCCESS if v >= 100 else SECONDARY) for r, v in zip(sub_yr["reporter_code"], sub_yr["coverage_ratio_pct"])],
        text=sub_yr["coverage_ratio_pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: Coverage Ratio %{x:.1f}%<extra></extra>"
    ))
    parity_threshold = 100.0
    apply_plot_theme(fig_cov, title=f"Merchandise Trade Coverage Ratio in {selected_year} (Exports / Imports %)", x_title="Coverage Ratio (%)")
    fig_cov.add_vline(x=parity_threshold, line_dash="dash", line_color=SUCCESS, annotation_text=f"Trade Balance Parity ({parity_threshold:.0f}%)")
    # Legend traces for coverage ratio categories
    fig_cov.add_trace(go.Bar(name="Luxembourg", x=[None], y=[None], marker_color=STATEC_YELLOW, showlegend=True))
    fig_cov.add_trace(go.Bar(name="Trade Surplus (Ratio ≥ 100%)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
    fig_cov.add_trace(go.Bar(name="Trade Deficit (Ratio < 100%)", x=[None], y=[None], marker_color=SECONDARY, showlegend=True))
    fig_cov.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=11)),
        margin=dict(l=10, r=40, t=55, b=30),
        yaxis=dict(autorange="reversed")
    )

    return html.Div([
        create_section_header(
            f"Q5: REGIONAL PEER BENCHMARKING ({selected_year})",
            "How does Luxembourg's trade compare with neighboring economies (Germany, France, Belgium, Netherlands)? Volume expansion indices and structural coverage ratio asymmetries.",
            badge_text="Research Question Q5",
            badge_color=STATEC_BLUE
        ),

        dbc.Row([
            dbc.Col([
                html.Div([dcc.Graph(figure=fig_index, config={"displayModeBar": False})], className="dash-card")
            ], md=7),
            dbc.Col([
                html.Div([dcc.Graph(figure=fig_cov, config={"displayModeBar": False})], className="dash-card")
            ], md=5)
        ])
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 10: Q6 — SEASONALITY & TREND LAB
# ───────────────────────────────────────────────────────────────────────────
def render_tab_seasonality():
    sea_df = load_seasonal_decomposition()
    options = []
    if not sea_df.empty:
        u = sea_df[["product_code", "product_name"]].drop_duplicates().sort_values("product_code")
        options = [{"label": f"{r['product_code']} — {r['product_name'][:35]}", "value": str(r["product_code"])} for _, r in u.iterrows()]
    def_p = "TOTAL" if any(o["value"] == "TOTAL" for o in options) else (options[0]["value"] if options else "TOTAL")

    return html.Div([
        create_section_header(
            "Q6: ECONOMETRIC SEASONALITY & TREND LAB",
            "Do Luxembourg's trade flows exhibit specific seasonal patterns? Decomposes monthly trade into raw observed series, 12-month centered rolling trends, and seasonally adjusted series.",
            badge_text="Research Question Q6",
            badge_color=STATEC_BLUE
        ),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("PRODUCT SECTOR:", className="control-label"),
                    dcc.Dropdown(
                        id="sea-product-dropdown",
                        options=options,
                        value=def_p,
                        clearable=False,
                        className="fw-semibold small"
                    )
                ], md=4),

                dbc.Col([
                    html.Label("TRADE FLOW:", className="control-label"),
                    dbc.RadioItems(
                        id="sea-flow-radio",
                        options=[
                            {"label": "Imports", "value": "IMPORT"},
                            {"label": "Exports", "value": "EXPORT"},
                        ],
                        value="IMPORT",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-3 py-1 text-white fw-bold",
                    )
                ], md=4),

                dbc.Col([
                    html.Label("SERIES DISPLAY:", className="control-label"),
                    dbc.Checklist(
                        id="sea-series-checklist",
                        options=[
                            {"label": "Raw Observed", "value": "raw"},
                            {"label": "12M Rolling Trend", "value": "trend"},
                            {"label": "Seasonally Adjusted", "value": "adj"},
                        ],
                        value=["raw", "trend"],
                        inline=True,
                        className="fw-semibold small"
                    )
                ], md=4)
            ], align="center")
        ], className="control-ribbon"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(id="sea-timeseries-chart", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=8),

            dbc.Col([
                html.Div([
                    dcc.Graph(id="sea-factors-chart", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=4)
        ])
    ])


@callback(
    Output("sea-timeseries-chart", "figure"),
    Output("sea-factors-chart", "figure"),
    Input("sea-product-dropdown", "value"),
    Input("sea-flow-radio", "value"),
    Input("sea-series-checklist", "value")
)
def update_seasonality_charts(product, flow, selected_series):
    sea_df = load_seasonal_decomposition()
    sub = sea_df[(sea_df["product_code"] == str(product)) & (sea_df["flow"] == flow)].sort_values("date").copy()
    if sub.empty:
        return go.Figure(), go.Figure()

    fig_ts = go.Figure()
    if "raw" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["value_eur"] / 1e6,
            name="Raw Observed", mode="lines",
            line=dict(color="#94A3B8", width=1.5),
            hovertemplate="%{x}: €%{y:,.1f}M<extra></extra>"
        ))
    if "trend" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["trend_eur"] / 1e6,
            name="12M Centered Trend", mode="lines",
            line=dict(color=PRIMARY, width=3),
            hovertemplate="%{x}: Trend €%{y:,.1f}M<extra></extra>"
        ))
    if "adj" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["seasonally_adjusted_eur"] / 1e6,
            name="Seasonally Adjusted", mode="lines",
            line=dict(color=SUCCESS, width=2, dash="dot"),
            hovertemplate="%{x}: SA €%{y:,.1f}M<extra></extra>"
        ))
    apply_plot_theme(fig_ts, title=f"Monthly Trade Timeseries ({sub['product_name'].iloc[0]}) (€M)", y_title="Million Euros (€M)", hovermode="x unified")
    fig_ts.update_layout(margin=dict(l=10, r=20, t=35, b=30))

    # Factors chart
    factors = sub.groupby("month")["seasonal_factor"].first().reset_index()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    factors["month_name"] = factors["month"].apply(lambda m: months[m - 1])
    colors = [DANGER if m == 8 else (SUCCESS if f > 1.05 else STATEC_BLUE) for m, f in zip(factors["month"], factors["seasonal_factor"])]
    fig_factors = go.Figure(go.Bar(
        x=factors["month_name"],
        y=(factors["seasonal_factor"] - 1.0) * 100,
        marker_color=colors,
        text=factors["seasonal_factor"].apply(lambda f: f"{(f - 1.0)*100:+.1f}%"),
        textposition="outside",
        hovertemplate="%{x}: %{text}<extra></extra>"
    ))
    apply_plot_theme(fig_factors, title="Seasonal Factors (% vs Annual Trend)", y_title="% vs Annual Trend")
    # Legend traces for seasonal factor color categories
    fig_factors.add_trace(go.Bar(name="Peak Month (> +5%)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
    fig_factors.add_trace(go.Bar(name="Baseline Range", x=[None], y=[None], marker_color=STATEC_BLUE, showlegend=True))
    fig_factors.add_trace(go.Bar(name="August Slump", x=[None], y=[None], marker_color=DANGER, showlegend=True))
    fig_factors.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10)),
        margin=dict(l=10, r=30, t=55, b=30)
    )

    return fig_ts, fig_factors


# ── Run Server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
