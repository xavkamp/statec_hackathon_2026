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
        ], className="app-header-main")
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


# ── Navigation Tabs ────────────────────────────────────────────────────────
def create_navigation_boxes():
    return html.Div([
        html.Div([
            html.Button([
                html.I(className="bi bi-shield-check me-1 text-warning"),
                "Resilience Radar"
            ], id="btn-tab-resilience", className="nav-tab-btn active", n_clicks=0),

            html.Button([
                html.I(className="bi bi-geo-alt me-1"),
                "Trading Partners (Q1 & Q4)"
            ], id="btn-tab-partners", className="nav-tab-btn", n_clicks=0),

            html.Button([
                html.I(className="bi bi-boxes me-1"),
                "Product Categories (Q2 & Q3)"
            ], id="btn-tab-products", className="nav-tab-btn", n_clicks=0),

            html.Button([
                html.I(className="bi bi-bar-chart-steps me-1"),
                "Peer Benchmarks (Q5)"
            ], id="btn-tab-benchmarks", className="nav-tab-btn", n_clicks=0),

            html.Button([
                html.I(className="bi bi-calendar-range me-1"),
                "Seasonality (Q6)"
            ], id="btn-tab-seasonality", className="nav-tab-btn", n_clicks=0),
        ], className="d-flex flex-wrap align-items-center nav-mode-container")
    ], className="mb-3")


# ── App Main Layout ─────────────────────────────────────────────────────────
app.layout = html.Div([
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
    "btn-tab-resilience",
    "btn-tab-partners", "btn-tab-products",
    "btn-tab-benchmarks", "btn-tab-seasonality"
]
TAB_ID_MAP = {
    "btn-tab-resilience": "tab-resilience",
    "btn-tab-partners": "tab-partners",
    "btn-tab-products": "tab-products",
    "btn-tab-benchmarks": "tab-benchmarks",
    "btn-tab-seasonality": "tab-seasonality"
}


@callback(
    Output("active-tab-store", "data"),
    [Output(b_id, "className") for b_id in ALL_TAB_BTNS],
    [Input(b_id, "n_clicks") for b_id in ALL_TAB_BTNS],
    State("active-tab-store", "data"),
    prevent_initial_call=False
)
def switch_active_nav_tab(*args):
    current_tab = args[-1] or "tab-resilience"

    try:
        ctx = dash.callback_context
        if ctx and ctx.triggered:
            trig_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trig_id in TAB_ID_MAP:
                current_tab = TAB_ID_MAP[trig_id]
    except Exception:
        pass

    tab_classes = [
        "nav-tab-btn active" if TAB_ID_MAP[b_id] == current_tab else "nav-tab-btn"
        for b_id in ALL_TAB_BTNS
    ]

    return tuple([current_tab] + tab_classes)


@callback(
    Output("tab-content", "children"),
    Input("active-tab-store", "data"),
    Input("global-year-dropdown", "value")
)
def render_main_tab_content(active_tab, selected_year):
    if active_tab == "tab-resilience":
        return render_tab_resilience(selected_year)
    elif active_tab in ["tab-partners", "tab-q4-drilldown"]:
        return render_tab_partners(selected_year)
    elif active_tab in ["tab-products", "tab-q3-partners"]:
        return render_tab_products(selected_year)
    elif active_tab == "tab-benchmarks":
        return render_tab_benchmarks(selected_year)
    elif active_tab == "tab-seasonality":
        return render_tab_seasonality()
    return render_tab_resilience(selected_year)


# ───────────────────────────────────────────────────────────────────────────
# TAB 1: SOVEREIGN SUPPLY RESILIENCE RADAR (Pillars 3–5)
# ───────────────────────────────────────────────────────────────────────────


def render_tab_resilience(selected_year):
    pp_df = load_product_partners()
    kpis_df = load_overview_kpis()
    partners_df = load_partner_rankings()
    hs4_df = load_hs4_product_rankings()
    if pp_df.empty and kpis_df.empty:
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
                    h4_title = f"HS {lead_h4['hs4_code']}: {lead_h4['hs4_name']}"
                    top_hs4_div = html.Div([
                        html.Span("Leading 4-Digit Good: ", className="small text-muted"),
                        html.Strong(f"{h4_title} ({fmt_eur(lead_h4['value_eur'])})", className="small", title=h4_title)
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
            showlegend=False,
            orientation="h",
            marker_color=[DANGER if h >= 2500 else (WARNING if h >= 1500 else SUCCESS) for h in comp_df["hhi"]],
            text=comp_df["hhi"].apply(lambda v: f"HHI {v:.0f}"),
            textposition="outside",
            hovertemplate="%{y}<br>Supplier Concentration HHI: %{x:.0f}<extra></extra>"
        ))
        apply_plot_theme(fig_comp, x_title="Herfindahl-Hirschman Index (HHI)")
        # Highly visible threshold reference lines at top of graph
        fig_comp.add_vline(
            x=1500, line_dash="dash", line_color=WARNING, line_width=2,
            annotation_text="<b>Threshold: HHI = 1,500 (Moderate)</b>",
            annotation_position="top left",
            annotation_font=dict(size=11, color=WARNING, family="Inter, sans-serif"),
            annotation_bgcolor="#FFFFFF"
        )
        fig_comp.add_vline(
            x=2500, line_dash="dash", line_color=DANGER, line_width=2,
            annotation_text="<b>Threshold: HHI = 2,500 (High)</b>",
            annotation_position="top right",
            annotation_font=dict(size=11, color=DANGER, family="Inter, sans-serif"),
            annotation_bgcolor="#FFFFFF"
        )
        # Explicit legend traces for color definitions
        fig_comp.add_trace(go.Bar(name="High Concentration (HHI > 2,500)", x=[None], y=[None], marker_color=DANGER, showlegend=True))
        fig_comp.add_trace(go.Bar(name="Moderate Concentration (1,500–2,500)", x=[None], y=[None], marker_color=WARNING, showlegend=True))
        fig_comp.add_trace(go.Bar(name="Low / Diversified (HHI < 1,500)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
        fig_comp.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10)),
            margin=dict(l=150, r=50, t=35, b=30),
            yaxis=dict(autorange="reversed")
        )

    # Macroeconomic Trajectory & Geopolitical Origin Figures
    fig_trajectory = go.Figure()
    fig_balance = go.Figure()
    fig_eu = go.Figure()
    vol_growth_pct = 0.0

    if not kpis_df.empty:
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
        apply_plot_theme(fig_trajectory, y_title="Billion Euros (€B)", dtick_x=2, hovermode="x unified")
        fig_trajectory.update_yaxes(range=[7, 28])
        fig_trajectory.update_layout(margin=dict(l=40, r=20, t=25, b=30), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        colors = [SUCCESS if v >= 0 else DANGER for v in kpis_df["trade_balance_eur"]]
        fig_balance = go.Figure(go.Bar(
            x=kpis_df["year"], y=kpis_df["trade_balance_eur"] / 1e9,
            marker_color=colors,
            hovertemplate="Trade Balance %{x}: €%{y:.2f}B<extra></extra>"
        ))
        apply_plot_theme(fig_balance, y_title="Billion Euros (€B)", dtick_x=2)
        fig_balance.update_layout(margin=dict(l=40, r=20, t=25, b=30))

        if "intra_eu_import_share_pct" in kpis_df.columns:
            fig_eu.add_trace(go.Scatter(
                x=kpis_df["year"], y=kpis_df["intra_eu_import_share_pct"],
                name="EU Import Share", line=dict(color=SECONDARY, width=2.5), mode="lines+markers"
            ))
        if "intra_eu_export_share_pct" in kpis_df.columns:
            fig_eu.add_trace(go.Scatter(
                x=kpis_df["year"], y=kpis_df["intra_eu_export_share_pct"],
                name="EU Export Share", line=dict(color=PRIMARY, width=2.5), mode="lines+markers"
            ))
        apply_plot_theme(fig_eu, y_title="Share of Total (%)", dtick_x=5)
        fig_eu.update_yaxes(range=[55, 98])
        fig_eu.update_layout(margin=dict(l=45, r=20, t=25, b=30), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        v_start = kpis_df[kpis_df["year"] == kpis_df["year"].min()]["trade_volume_eur"].iloc[0]
        v_sub = kpis_df[kpis_df["year"] == use_year]
        v_end = v_sub["trade_volume_eur"].iloc[0] if not v_sub.empty else kpis_df["trade_volume_eur"].iloc[-1]
        vol_growth_pct = ((v_end / v_start) - 1.0) * 100 if v_start > 0 else 0.0

    # Regional Origin Donut & Non-EU Suppliers
    sub_geo = partners_df[(partners_df["year"] == use_year) & (partners_df["flow"] == "IMPORT")].copy()
    if sub_geo.empty and not partners_df.empty:
        sub_geo = partners_df[(partners_df["year"] == partners_df["year"].max()) & (partners_df["flow"] == "IMPORT")].copy()

    eu_codes = {'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'}
    neighbors = {'BE', 'DE', 'FR'}
    tot_imp = sub_geo['value_eur'].sum() if not sub_geo.empty else 0.0
    neigh_val = sub_geo[sub_geo['partner_code'].isin(neighbors)]['value_eur'].sum() if not sub_geo.empty else 0.0
    other_eu_val = sub_geo[sub_geo['partner_code'].isin(eu_codes - neighbors)]['value_eur'].sum() if not sub_geo.empty else 0.0
    row_val = max(0, tot_imp - (neigh_val + other_eu_val))

    neigh_share = (neigh_val / tot_imp * 100) if tot_imp > 0 else 0.0
    other_eu_share = (other_eu_val / tot_imp * 100) if tot_imp > 0 else 0.0
    row_share = (row_val / tot_imp * 100) if tot_imp > 0 else 0.0

    fig_donut = go.Figure(go.Pie(
        labels=[
            "Direct Neighbors (BE, DE, FR)",
            "Other EU Member States",
            "Rest of World"
        ],
        values=[neigh_val, other_eu_val, row_val],
        hole=0.55,
        textposition="outside",
        textinfo="label+percent",
        marker_colors=[PRIMARY, "#38BDF8", "#94A3B8"],
        hovertemplate="<b>%{label}</b><br>Value: €%{value:,.0f}<br>Share: %{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=35, t=30, b=30),
        font=dict(family="Inter, sans-serif", size=10, color=TEXT_PRIMARY),
        showlegend=False
    )

    non_eu_sub = sub_geo[~sub_geo['partner_code'].isin(eu_codes)].sort_values('value_eur', ascending=False).head(8).copy() if not sub_geo.empty else pd.DataFrame()
    fig_non_eu = go.Figure()
    if not non_eu_sub.empty:
        non_eu_sub["name_en"] = non_eu_sub["partner_code"].apply(get_country_name)
        max_val_m = (non_eu_sub['value_eur'] / 1e6).max()
        fig_non_eu.add_trace(go.Bar(
            x=non_eu_sub['value_eur'] / 1e6,
            y=non_eu_sub['name_en'],
            orientation='h',
            marker_color="#8B5CF6",
            text=non_eu_sub['market_share_pct'].apply(lambda p: f"{p:.2f}%"),
            textposition="outside",
            hovertemplate="%{y}: €%{x:.1f}M (%{text} of all imports)<extra></extra>"
        ))
        apply_plot_theme(fig_non_eu, x_title="Million Euros (€M)")
        fig_non_eu.update_xaxes(range=[0, max_val_m * 1.25])
        fig_non_eu.update_layout(margin=dict(l=110, r=55, t=10, b=30), yaxis=dict(autorange="reversed"))

    return html.Div([
        create_compact_kpi_ribbon(use_year),

        # Section 1: Macro Trajectory & Geopolitical Origins
        create_section_header(
            "MACRO TRAJECTORY & GEOPOLITICAL ORIGINS",
            f"25-Year merchandise trade trajectory ({vol_growth_pct:+.1f}% volume growth vs 2000), trade balance evolution, EU Single Market integration, and third-country supplier exposure."
        ),

        # Row 1: Macro Trajectory & Trade Balance
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("25-YEAR TRAJECTORY OF MERCHANDISE TRADE FLOWS (2000–2026)", className="card-title-upper"),
                    dcc.Graph(figure=fig_trajectory, config={"displayModeBar": False})
                ], className="dash-card")
            ], md=8),
            dbc.Col([
                html.Div([
                    html.H6("ANNUAL MERCHANDISE TRADE BALANCE (€B)", className="card-title-upper"),
                    dcc.Graph(figure=fig_balance, config={"displayModeBar": False})
                ], className="dash-card")
            ], md=4),
        ]),

        # Row 2: Origin Donut, Non-EU Suppliers, and EU Integration Line Chart
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("REGIONAL IMPORT ORIGIN EXPOSURE", className="card-title-upper"),
                    dcc.Graph(figure=fig_donut, config={"displayModeBar": False}, className="chart-h-340")
                ], className="dash-card")
            ], md=4),

            dbc.Col([
                html.Div([
                    html.H6("TOP NON-EU STRATEGIC SUPPLIERS", className="card-title-upper"),
                    dcc.Graph(figure=fig_non_eu, config={"displayModeBar": False}, className="chart-h-340")
                ], className="dash-card")
            ], md=4),

            dbc.Col([
                html.Div([
                    html.H6("EUROPEAN SINGLE MARKET INTEGRATION", className="card-title-upper"),
                    dcc.Graph(figure=fig_eu, config={"displayModeBar": False}, className="chart-h-340")
                ], className="dash-card")
            ], md=4),
        ], className="mb-4"),

        # Section 2: Critical Supply Baskets & Concentration
        create_section_header(
            f"CRITICAL IMPORT BASKETS & SUPPLIER CONCENTRATION ({use_year})",
            "Supplier concentration estimated by Herfindahl-Hirschman Index (HHI) across 6 merchandise baskets (Energy, Food, Health, Metals, Tech, Vehicles).",
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
                    html.H6(f"IMPORT BASKETS SUPPLIER CONCENTRATION SCORE (HHI) IN {use_year}", className="card-title-upper"),
                    dcc.Graph(figure=fig_comp, config={"displayModeBar": False})
                ], className="dash-card")
            ], md=12)
        ]),

        dbc.Row(cards)
    ])


# ───────────────────────────────────────────────────────────────────────────
# COMPATIBILITY ALIASES FOR MERGED RESILIENCE VIEW
# ───────────────────────────────────────────────────────────────────────────
def render_tab_macro(selected_year):
    return render_tab_resilience(selected_year)


def render_tab_geopolitics(selected_year):
    return render_tab_resilience(selected_year)



def render_tab_stress(selected_year=None):
    return render_tab_resilience(selected_year)



# ───────────────────────────────────────────────────────────────────────────
# TAB 5: Q1 — TRADING PARTNERS & WORLD FLOW
# ───────────────────────────────────────────────────────────────────────────
def render_tab_partners(selected_year):
    partners_df = load_partner_rankings()
    sub_yr = partners_df[(partners_df["year"] == selected_year) & (partners_df["flow"] == "IMPORT")].sort_values("rank")
    if not sub_yr.empty:
        top_p = sub_yr["partner_code"].head(30).tolist()
    else:
        top_p = ["DE", "BE", "FR", "NL", "US", "CN", "IT", "GB", "PL", "CH", "ES", "JP", "CZ", "TR", "AT"]
    q4_options = [{"label": f"{get_country_name(c)} ({c})", "value": c} for c in top_p]
    def_q4_p = top_p[0] if top_p else "DE"

    return html.Div([
        # ── Q1 Section: Main Trading Partners & Bilateral Flows ──
        create_section_header(
            "Q1: TRADING PARTNERS & BILATERAL FLOWS",
            "Who are Luxembourg's main trading partners? How have they evolved over time? Click any country bar below to inspect top products and detailed tariff lines."
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
                ], md=6, sm=6),

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
                ], md=6, sm=6),
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
                        html.Span("💡 Click any bar to inspect country products & tariff lines", className="small text-primary fw-bold")
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    dcc.Graph(id="q1-top-partners-bar", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=7),

            dbc.Col([
                html.Div(id="q1-partner-spotlight-panel", className="h-100")
            ], md=5)
        ]),

        # Map Row (With Geographic Scope and Map Size controls right beside the map header)
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H6("GLOBAL GEOGRAPHIC FLOW MAP", className="card-title-upper mb-0"),
                            html.Small("Hover to view country trade volume • Click to select", className="kpi-caption")
                        ]),
                        html.Div([
                            html.Label("SCOPE:", className="control-label me-2 mb-0 d-none d-sm-inline"),
                            dbc.RadioItems(
                                id="q1-scope-radio",
                                options=[
                                    {"label": "World", "value": "world"},
                                    {"label": "Europe (EU-27)", "value": "europe"},
                                ],
                                value="world",
                                inline=True,
                                className="btn-group me-2",
                                input_class_name="btn-check",
                                label_class_name="btn btn-outline-dark btn-sm px-2 py-1",
                                label_checked_class_name="btn btn-dark btn-sm px-2 py-1 text-white fw-bold",
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-arrows-fullscreen me-1"), "Toggle Map Size"],
                                id="q1-map-toggle-btn",
                                color="light",
                                size="sm",
                                className="border fw-bold small",
                            )
                        ], className="d-flex align-items-center")
                    ], className="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2"),
                    dcc.Graph(id="q1-world-map", config={"displayModeBar": False})
                ], className="dash-card")
            ], md=12)
        ], className="mb-4"),

        # ── Q4 Section: Product Breakdown per Country (Tariff Drill-Down) ──
        create_section_header(
            f"Q4: PRODUCT BREAKDOWN PER COUNTRY ({selected_year})",
            "Granular product breakdown for the selected partner country across HS2 Chapters, HS4 Subheadings, and 8-digit CN8 tariff lines. Select or click any country above to update."
        ),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("PARTNER COUNTRY:", className="control-label"),
                    dcc.Dropdown(
                        id="q4-partner-dropdown",
                        options=q4_options,
                        value=def_q4_p,
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
                ], md=2),

                dbc.Col([
                    html.Label("TARIFF GRANULARITY LEVEL:", className="control-label"),
                    dbc.RadioItems(
                        id="q4-level-radio",
                        options=[
                            {"label": "HS2 (Chapters)", "value": 2},
                            {"label": "HS4 (Subheadings)", "value": 4},
                            {"label": "CN8 (Detailed)", "value": 8},
                        ],
                        value=4,
                        inline=True,
                        className="btn-group d-flex",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-dark btn-sm px-2 py-1 flex-fill",
                        label_checked_class_name="btn btn-dark btn-sm px-2 py-1 text-white fw-bold flex-fill",
                    )
                ], md=4),

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
    max_x_val = float(x_col.max()) if not x_col.empty else 100
    fig_bar.update_xaxes(range=[0, max_x_val * 1.25])
    fig_bar.update_layout(margin=dict(l=120, r=50, t=10, b=30), yaxis=dict(autorange="reversed"))

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
    prod_df = load_product_rankings()
    q3_options = []
    def_q3_prod = "87"
    if not prod_df.empty:
        u = prod_df[["hs2_code", "hs2_name"]].drop_duplicates().sort_values("hs2_code")
        q3_options = [{"label": f"Ch. {r['hs2_code']} — {r['hs2_name'][:35]}", "value": str(r["hs2_code"])} for _, r in u.iterrows()]
        sub_yr = prod_df[(prod_df["year"] == selected_year) & (prod_df["flow"] == "IMPORT")].sort_values("value_eur", ascending=False)
        if not sub_yr.empty:
            def_q3_prod = str(sub_yr.iloc[0]["hs2_code"])
        elif q3_options:
            def_q3_prod = q3_options[0]["value"]

    return html.Div([
        # ── Q2 Section: Main Product Categories & Structural Shift ──
        create_section_header(
            f"Q2: MAIN PRODUCT CATEGORIES & STRUCTURAL SHIFT ({selected_year})",
            "What are the main categories of goods traded? How have these patterns transformed over 25 years (from steel dominance to advanced automotive, machinery, and pharma)? Click any product bar to see its top partner countries."
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
                        html.Span("💡 Click any bar to inspect product suppliers & partner origins", className="small text-primary fw-bold")
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
                    html.H6(id="q2-shift-chart-title", className="card-title-upper"),
                    dcc.Graph(id="q2-shift-chart", config={"displayModeBar": False}, className="chart-h-300")
                ], className="dash-card")
            ], md=12)
        ], className="mb-4"),

        # ── Q3 Section: Principal Partners by Product Category ──
        create_section_header(
            f"Q3: PRINCIPAL PARTNERS BY PRODUCT CATEGORY ({selected_year})",
            "For a given product category, who are Luxembourg's principal trading partners? Inspect supplier concentration (HHI) and geographic origin breakdown. Select or click any product above to update."
        ),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("SELECT PRODUCT CATEGORY:", className="control-label"),
                    dcc.Dropdown(
                        id="q3-product-dropdown",
                        options=q3_options,
                        value=def_q3_prod,
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
    Output("q2-shift-chart-title", "children"),
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
        top["label"] = "HS " + top["hs4_code"] + ": " + top["hs4_name"].apply(lambda s: str(s)[:34] + ".." if len(str(s)) > 34 else str(s))
        code_col = top["hs4_code"]
    else:
        prod_df = load_product_rankings()
        sub = prod_df[(prod_df["year"] == year) & (prod_df["flow"] == flow)].copy()
        if sub.empty:
            sub = prod_df[(prod_df["year"] == prod_df["year"].max()) & (prod_df["flow"] == flow)].copy()
        top = sub.sort_values("value_eur", ascending=False).head(10).copy()
        top["label"] = "Ch. " + top["hs2_code"] + ": " + top["hs2_name"].apply(lambda s: str(s)[:34] + ".." if len(str(s)) > 34 else str(s))
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
    max_val_m = (top["value_eur"] / 1e6).max() if not top.empty else 100
    fig_bar.update_xaxes(range=[0, max_val_m * 1.25])
    fig_bar.update_layout(margin=dict(l=190, r=50, t=10, b=30), yaxis=dict(autorange="reversed"))

    # Structural shift chart: dynamically track top 5 product categories for this flow in the selected year
    all_prod = load_product_rankings()
    sub_yr = all_prod[(all_prod["year"] == year) & (all_prod["flow"] == flow)].sort_values("value_eur", ascending=False)
    if not sub_yr.empty:
        top5_chs = sub_yr.head(5)
        key_chs = top5_chs["hs2_code"].tolist()
        ch_names = {r["hs2_code"]: f"{r['hs2_name'][:20]} ({r['hs2_code']})" for _, r in top5_chs.iterrows()}
    else:
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
    apply_plot_theme(fig_shift, y_title="Million Euros (€M)")
    fig_shift.update_layout(
        margin=dict(l=10, r=20, t=25, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10))
    )

    barchart_title = f"Top 10 Traded Product {'Subheadings (HS4)' if granularity == 4 else 'Chapters (HS2)'} in {year}"
    shift_title = f"25-YEAR STRUCTURAL TRANSFORMATION OF PRODUCT {flow.upper()}S (2000–2025)"
    return barchart_title, fig_bar, fig_shift, shift_title


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

    if not sub.empty:
        if "hhi" in sub.columns and pd.notna(sub["hhi"].iloc[0]):
            hhi_score = float(sub["hhi"].iloc[0])
        elif tot_val > 0:
            shares = (sub["value_eur"] / tot_val) * 100
            hhi_score = float((shares ** 2).sum())
        else:
            hhi_score = 0.0
    else:
        hhi_score = 0.0

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
    return render_tab_products(selected_year)


@callback(
    Output("q3-product-dropdown", "value"),
    Input("q2-selected-product", "data"),
    prevent_initial_call=True
)
def sync_q3_product_from_q2(selected_prod):
    if selected_prod:
        return str(selected_prod)[:2].zfill(2)
    return dash.no_update


@callback(
    Output("q3-flow-radio", "value"),
    Input("q2-flow-radio", "value"),
    prevent_initial_call=True
)
def sync_q3_flow_from_q2(flow):
    if flow:
        return flow
    return dash.no_update


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
    return render_tab_partners(selected_year)


@callback(
    Output("q4-partner-dropdown", "value"),
    Input("q1-selected-partner", "data"),
    prevent_initial_call=True
)
def sync_q4_partner_from_q1(selected_p):
    if selected_p:
        return str(selected_p).upper()
    return dash.no_update


@callback(
    Output("q4-flow-radio", "value"),
    Input("q1-flow-radio", "value"),
    prevent_initial_call=True
)
def sync_q4_flow_from_q1(flow):
    if flow:
        return flow
    return dash.no_update


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
        # Fallback to level 2 drilldown
        df2 = load_drilldown_lvl2()
        sub = df2[(df2["partner_code"] == partner_code) & (df2["flow"] == flow)].copy()
        level = 2

    if sub.empty:
        # Fallback to product_partners (which covers all 237 partner countries)
        pp_df = load_product_partners()
        sub_pp = pp_df[(pp_df["partner_code"] == partner_code) & (pp_df["flow"] == flow) & (pp_df["year"] == year)].copy()
        if sub_pp.empty:
            sub_pp = pp_df[(pp_df["partner_code"] == partner_code) & (pp_df["flow"] == flow)].copy()
            if not sub_pp.empty:
                sub_pp = sub_pp[sub_pp["year"] == sub_pp["year"].max()]
        if not sub_pp.empty:
            sub = pd.DataFrame({
                "partner_code": sub_pp["partner_code"],
                "flow": sub_pp["flow"],
                "product_code": sub_pp["hs2_code"],
                "product_name": sub_pp["hs2_name"],
                "value_eur": sub_pp["value_eur"],
                "level": 2
            })
            level = 2

    if threshold in [15, 25]:
        sub = sub.sort_values("value_eur", ascending=False).head(int(threshold)).copy()
    else:
        sub = sub[sub["value_eur"] >= float(threshold)].sort_values("value_eur", ascending=False).head(30).copy()

    sub["label"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: str(s)[:38] + ".." if len(str(s)) > 38 else str(s))

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
    max_val_m = (sub["value_eur"] / 1e6).max() if not sub.empty else 100
    fig.update_xaxes(range=[0, max_val_m * 1.25])
    fig.update_layout(margin=dict(l=190, r=50, t=10, b=30), yaxis=dict(autorange="reversed"))

    title = f"{get_country_name(partner_code)} ({partner_code}) — Level {level} Tariff Breakdown ({flow.capitalize()})"
    return title, fig


# ───────────────────────────────────────────────────────────────────────────
# TAB 9: Q5 — REGIONAL PEER BENCHMARKING
# ───────────────────────────────────────────────────────────────────────────
BENCHMARK_PRODUCT_OPTIONS = [
    {"label": "All Merchandise Trade (Total)", "value": "TOTAL"},
    {"label": "Ch. 87 — Vehicles & Automotive Equipment", "value": "87"},
    {"label": "Ch. 84 — Machinery & Mechanical Appliances", "value": "84"},
    {"label": "Ch. 85 — Electrical Machinery & Electronics", "value": "85"},
    {"label": "Ch. 30 — Pharmaceutical Products", "value": "30"},
    {"label": "Ch. 72 — Iron and Steel", "value": "72"},
    {"label": "Ch. 73 — Articles of Iron or Steel", "value": "73"},
    {"label": "Ch. 27 — Mineral Fuels & Energy", "value": "27"},
    {"label": "Ch. 39 — Plastics and Articles Thereof", "value": "39"},
    {"label": "Ch. 90 — Optical, Medical & Precision Instruments", "value": "90"},
    {"label": "Ch. 04 — Dairy Produce, Honey & Edible Products", "value": "04"},
    {"label": "Ch. 22 — Beverages, Spirits and Vinegar", "value": "22"},
    {"label": "Ch. 10 — Cereals and Grains", "value": "10"},
    {"label": "Ch. 76 — Aluminium and Articles Thereof", "value": "76"},
    {"label": "Ch. 40 — Rubber and Articles Thereof", "value": "40"},
    {"label": "Ch. 94 — Furniture & Lighting", "value": "94"},
    {"label": "Ch. 25 — Salt, Stone, Plaster & Cement", "value": "25"},
    {"label": "Ch. 48 — Paper and Paperboard", "value": "48"},
    {"label": "Ch. 62 — Apparel & Clothing Accessories", "value": "62"},
    {"label": "Ch. 88 — Aircraft, Spacecraft & Parts", "value": "88"},
]
BENCHMARK_PRODUCT_MAP = {opt["value"]: opt["label"] for opt in BENCHMARK_PRODUCT_OPTIONS}


def generate_q5_figures(product_code="TOTAL", flow_metric="volume", selected_year=2025):
    bench_df = load_country_benchmarks()
    if bench_df.empty:
        return "Growth Trajectory", go.Figure(), "Peer Comparison", go.Figure()

    product_code = str(product_code or "TOTAL")
    sub_prod = bench_df[bench_df["product_code"] == product_code]
    if sub_prod.empty:
        product_code = "TOTAL"
        sub_prod = bench_df[bench_df["product_code"] == "TOTAL"]

    product_label = BENCHMARK_PRODUCT_MAP.get(product_code, f"Product {product_code}")
    flow_metric = str(flow_metric or "volume").lower()

    country_colors = {"LU": STATEC_YELLOW, "DE": STATEC_NAVY, "FR": STATEC_BLUE, "BE": "#DC2626", "NL": "#D97706"}
    country_names = {"LU": "Luxembourg", "DE": "Germany", "FR": "France", "BE": "Belgium", "NL": "Netherlands"}

    if flow_metric == "import":
        index_col = "import_index_2000"
        flow_name = "Import Growth"
        left_title = f"{product_label.upper()} — IMPORT GROWTH TRAJECTORY (BASE 100 = 2000)"
        right_title = f"{product_label.upper()} — IMPORT VALUE IN {selected_year} (€M)"
    elif flow_metric == "export":
        index_col = "export_index_2000"
        flow_name = "Export Growth"
        left_title = f"{product_label.upper()} — EXPORT GROWTH TRAJECTORY (BASE 100 = 2000)"
        right_title = f"{product_label.upper()} — EXPORT VALUE IN {selected_year} (€M)"
    else:
        index_col = "volume_index_2000"
        flow_name = "Trade Volume Growth"
        left_title = f"{product_label.upper()} — TRADE VOLUME GROWTH TRAJECTORY (BASE 100 = 2000)"
        right_title = f"{product_label.upper()} — TRADE COVERAGE RATIO IN {selected_year} (EXPORTS / IMPORTS %)"

    # Left chart: Multi-country trajectory line chart
    fig_index = go.Figure()
    for c in ["LU", "DE", "FR", "BE", "NL"]:
        c_sub = sub_prod[sub_prod["reporter_code"] == c].sort_values("year")
        if not c_sub.empty and index_col in c_sub.columns:
            fig_index.add_trace(go.Scatter(
                x=c_sub["year"], y=c_sub[index_col],
                name=country_names.get(c, c),
                mode="lines+markers" if c == "LU" else "lines",
                line=dict(color=country_colors.get(c, STATEC_GRAY), width=3.5 if c == "LU" else 2),
                marker=dict(size=6 if c == "LU" else 0),
                hovertemplate="%{x}: Index %{y:.1f}<extra></extra>"
            ))

    apply_plot_theme(fig_index, y_title=f"{flow_name} Index (2000 = 100)", dtick_x=2, hovermode="x unified")
    fig_index.add_hline(
        y=100, line_dash="dash", line_color="#94A3B8", line_width=1,
        annotation_text="Base 2000 = 100", annotation_position="bottom right",
        annotation_font=dict(size=9, color="#94A3B8", family="Inter, sans-serif")
    )
    fig_index.update_layout(
        margin=dict(l=55, r=20, t=25, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10))
    )

    # Right chart: Peer Comparison for selected_year
    sub_yr = sub_prod[sub_prod["year"] == selected_year]
    if sub_yr.empty:
        sub_yr = sub_prod[sub_prod["year"] == sub_prod["year"].max()]

    sub_yr = sub_yr.copy()
    sub_yr["name"] = sub_yr["reporter_code"].apply(lambda r: country_names.get(r, r))

    if flow_metric in ["import", "export"]:
        val_col = "IMPORT" if flow_metric == "import" else "EXPORT"
        sub_yr["val_m"] = sub_yr[val_col] / 1e6
        max_val_m = float(sub_yr["val_m"].max()) if not sub_yr["val_m"].empty else 1.0

        fig_right = go.Figure(go.Bar(
            x=sub_yr["val_m"],
            y=sub_yr["name"],
            showlegend=False,
            orientation="h",
            marker_color=[STATEC_YELLOW if r == "LU" else STATEC_BLUE for r in sub_yr["reporter_code"]],
            text=sub_yr["val_m"].apply(lambda v: f"€{v:,.1f}M" if v < 1000 else f"€{v/1000:,.2f}B"),
            textposition="outside",
            hovertemplate="%{y}: €%{x:,.1f}M<extra></extra>"
        ))
        apply_plot_theme(fig_right, x_title="Million Euros (€M)")
        fig_right.add_trace(go.Bar(name="Luxembourg", x=[None], y=[None], marker_color=STATEC_YELLOW, showlegend=True))
        fig_right.add_trace(go.Bar(name="Peer Economies", x=[None], y=[None], marker_color=STATEC_BLUE, showlegend=True))
        fig_right.update_xaxes(range=[0, max(max_val_m * 1.35, 10.0)])
        fig_right.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10)),
            margin=dict(l=100, r=55, t=25, b=30),
            yaxis=dict(autorange="reversed")
        )
    else:
        # Trade Volume -> Structural Coverage Ratio with 100% Parity threshold
        max_cov = float(sub_yr["coverage_ratio_pct"].max()) if not sub_yr["coverage_ratio_pct"].empty else 100.0
        fig_right = go.Figure(go.Bar(
            x=sub_yr["coverage_ratio_pct"],
            y=sub_yr["name"],
            showlegend=False,
            orientation="h",
            marker_color=[STATEC_YELLOW if r == "LU" else (SUCCESS if v >= 100 else SECONDARY) for r, v in zip(sub_yr["reporter_code"], sub_yr["coverage_ratio_pct"])],
            text=sub_yr["coverage_ratio_pct"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside",
            hovertemplate="%{y}: Coverage Ratio %{x:.1f}%<extra></extra>"
        ))
        parity_threshold = 100.0
        apply_plot_theme(fig_right, x_title="Coverage Ratio (%)")
        fig_right.add_vline(
            x=parity_threshold, line_dash="dash", line_color=SUCCESS, line_width=1.5,
            annotation_text="<b>Parity: 100%</b>",
            annotation_position="top left",
            annotation_font=dict(size=10, color=SUCCESS, family="Inter, sans-serif"),
            annotation_bgcolor="#FFFFFF"
        )
        fig_right.add_trace(go.Bar(name="Luxembourg", x=[None], y=[None], marker_color=STATEC_YELLOW, showlegend=True))
        fig_right.add_trace(go.Bar(name="Trade Surplus (Ratio ≥ 100%)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
        fig_right.add_trace(go.Bar(name="Trade Deficit (Ratio < 100%)", x=[None], y=[None], marker_color=SECONDARY, showlegend=True))
        fig_right.update_xaxes(range=[0, max(max_cov * 1.3, 135.0)])
        fig_right.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10)),
            margin=dict(l=100, r=45, t=25, b=30),
            yaxis=dict(autorange="reversed")
        )

    return left_title, fig_index, right_title, fig_right


def render_tab_benchmarks(selected_year):
    left_title, fig_index, right_title, fig_cov = generate_q5_figures("TOTAL", "volume", selected_year)

    return html.Div([
        create_section_header(
            f"Q5: REGIONAL PEER BENCHMARKING ({selected_year})",
            "How does Luxembourg's trade compare with neighboring economies (Germany, France, Belgium, Netherlands)? Compare long-term growth trajectories and structural trade balances across key product categories."
        ),

        # Controls Ribbon for Product and Flow Dimension
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("PRODUCT CATEGORY:", className="control-label"),
                    dcc.Dropdown(
                        id="q5-product-dropdown",
                        options=BENCHMARK_PRODUCT_OPTIONS,
                        value="TOTAL",
                        clearable=False,
                        searchable=True,
                        className="fw-semibold small"
                    )
                ], md=7, sm=12),
                dbc.Col([
                    html.Label("GROWTH FLOW:", className="control-label"),
                    dbc.RadioItems(
                        id="q5-flow-radio",
                        options=[
                            {"label": " Trade Volume (Exp + Imp)", "value": "volume"},
                            {"label": " Imports", "value": "import"},
                            {"label": " Exports", "value": "export"},
                        ],
                        value="volume",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-2 py-1 text-white fw-bold",
                    )
                ], md=5, sm=12),
            ], align="center")
        ], className="control-ribbon"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6(left_title, id="q5-index-title", className="card-title-upper"),
                    dcc.Graph(id="q5-index-graph", figure=fig_index, config={"displayModeBar": False})
                ], className="dash-card")
            ], md=7),
            dbc.Col([
                html.Div([
                    html.H6(right_title, id="q5-cov-title", className="card-title-upper"),
                    dcc.Graph(id="q5-cov-graph", figure=fig_cov, config={"displayModeBar": False})
                ], className="dash-card")
            ], md=5)
        ])
    ])


@callback(
    Output("q5-index-title", "children"),
    Output("q5-index-graph", "figure"),
    Output("q5-cov-title", "children"),
    Output("q5-cov-graph", "figure"),
    Input("q5-product-dropdown", "value"),
    Input("q5-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    prevent_initial_call=True
)
def update_q5_charts(product_code, flow_metric, selected_year):
    return generate_q5_figures(product_code, flow_metric, selected_year)


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
            "Q6: ECONOMETRIC SEASONALITY & TREND",
            "Do Luxembourg's trade flows exhibit specific seasonal patterns? Decomposes monthly trade into raw observed series, 12-month centered rolling trends, and seasonally adjusted series."
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
                            {"label": "Trade Balance", "value": "BALANCE"},
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
                    html.H6("MONTHLY TRADE FLOW TIMESERIES & 12M TREND (€M)", className="card-title-upper"),
                    dcc.Graph(id="sea-timeseries-chart", config={"displayModeBar": False}, className="chart-h-380")
                ], className="dash-card")
            ], md=8),

            dbc.Col([
                html.Div([
                    html.H6("MONTHLY SEASONAL FACTORS & DEVIATION", className="card-title-upper"),
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
    if flow == "BALANCE":
        imp = sea_df[(sea_df["product_code"] == str(product)) & (sea_df["flow"] == "IMPORT")].sort_values("date").copy()
        exp = sea_df[(sea_df["product_code"] == str(product)) & (sea_df["flow"] == "EXPORT")].sort_values("date").copy()
        if imp.empty or exp.empty:
            return go.Figure(), go.Figure()
        sub = pd.merge(exp[["date", "month", "product_code", "product_name", "value_eur", "trend_eur", "seasonally_adjusted_eur"]],
                       imp[["date", "value_eur", "trend_eur", "seasonally_adjusted_eur"]],
                       on="date", suffixes=("_exp", "_imp"))
        sub["value_eur"] = sub["value_eur_exp"] - sub["value_eur_imp"]
        sub["trend_eur"] = sub["trend_eur_exp"] - sub["trend_eur_imp"]
        sub["seasonally_adjusted_eur"] = sub["seasonally_adjusted_eur_exp"] - sub["seasonally_adjusted_eur_imp"]
        sub["seasonal_dev_eur"] = sub["value_eur"] - sub["trend_eur"]
    else:
        sub = sea_df[(sea_df["product_code"] == str(product)) & (sea_df["flow"] == flow)].sort_values("date").copy()
        if sub.empty:
            return go.Figure(), go.Figure()

    fig_ts = go.Figure()
    flow_lbl = "Trade Balance" if flow == "BALANCE" else flow.capitalize()
    if "raw" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["value_eur"] / 1e6,
            name=f"Raw Observed {flow_lbl}", mode="lines",
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
    apply_plot_theme(fig_ts, y_title="Million Euros (€M)", hovermode="x unified")
    fig_ts.update_layout(
        margin=dict(l=10, r=20, t=25, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10))
    )

    # Factors chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if flow == "BALANCE":
        factors = sub.groupby("month")["seasonal_dev_eur"].mean().reset_index()
        factors["month_name"] = factors["month"].apply(lambda m: months[m - 1])
        dev_m = factors["seasonal_dev_eur"] / 1e6
        colors = [SUCCESS if v > 15 else (DANGER if v < -15 else STATEC_BLUE) for v in dev_m]
        fig_factors = go.Figure(go.Bar(
            x=factors["month_name"],
            y=dev_m,
            showlegend=False,
            marker_color=colors,
            text=[f"{v:+.1f}M" for v in dev_m],
            textposition="outside",
            hovertemplate="%{x}: Deviation %{text}<extra></extra>"
        ))
        apply_plot_theme(fig_factors, y_title="Deviation vs Trend (€M)")
        fig_factors.add_trace(go.Bar(name="Deficit Narrowing (> +€15M)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
        fig_factors.add_trace(go.Bar(name="Baseline Range", x=[None], y=[None], marker_color=STATEC_BLUE, showlegend=True))
        fig_factors.add_trace(go.Bar(name="Deficit Widening (< -€15M)", x=[None], y=[None], marker_color=DANGER, showlegend=True))
        y_vals = dev_m
    else:
        factors = sub.groupby("month")["seasonal_factor"].first().reset_index()
        factors["month_name"] = factors["month"].apply(lambda m: months[m - 1])
        colors = [DANGER if m == 8 else (SUCCESS if f > 1.05 else STATEC_BLUE) for m, f in zip(factors["month"], factors["seasonal_factor"])]
        fig_factors = go.Figure(go.Bar(
            x=factors["month_name"],
            y=(factors["seasonal_factor"] - 1.0) * 100,
            showlegend=False,
            marker_color=colors,
            text=factors["seasonal_factor"].apply(lambda f: f"{(f - 1.0)*100:+.1f}%"),
            textposition="outside",
            hovertemplate="%{x}: %{text}<extra></extra>"
        ))
        apply_plot_theme(fig_factors, y_title="% vs Annual Trend")
        fig_factors.add_trace(go.Bar(name="Peak Month (> +5%)", x=[None], y=[None], marker_color=SUCCESS, showlegend=True))
        fig_factors.add_trace(go.Bar(name="Baseline Range", x=[None], y=[None], marker_color=STATEC_BLUE, showlegend=True))
        fig_factors.add_trace(go.Bar(name="August Slump", x=[None], y=[None], marker_color=DANGER, showlegend=True))
        y_vals = (factors["seasonal_factor"] - 1.0) * 100

    y_min, y_max = float(y_vals.min()), float(y_vals.max())
    y_pad = max(abs(y_min), abs(y_max), 5.0) * 0.25
    fig_factors.update_yaxes(range=[y_min - y_pad, y_max + y_pad])
    fig_factors.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter, sans-serif", size=10)),
        margin=dict(l=10, r=30, t=25, b=30)
    )

    return fig_ts, fig_factors


# ── Run Server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
