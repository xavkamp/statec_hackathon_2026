"""Interactive Dash Application for STATEC Hackathon 2026.
Luxembourg External Trade Representation (2000-2026).
Eurostat Dataset: ds-045409
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

# Ensure project root is in path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.dashboard.design_system import (
    PRIMARY, SECONDARY, SUCCESS, DANGER, WARNING, NEUTRAL,
    SURFACE, BACKGROUND, BORDER, TEXT_PRIMARY, TEXT_MUTED,
    CATEGORICAL, PLOT_LAYOUT, CARD_STYLE, KPI_CARD_STYLE
)
from src.dashboard.data_loader import (
    load_overview_kpis, load_partner_rankings, load_product_rankings,
    load_seasonal_decomposition, load_country_benchmarks,
    load_drilldown_lvl2, load_drilldown_lvl4, load_drilldown_lvl8
)

# Initialize Dash App with modern theme
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    title="Luxembourg Trade Intelligence (2000-2026)",
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

# ── Header & KPI Ribbon Layout ──────────────────────────────────────────────
def create_header():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("STATEC", style={"backgroundColor": "#0284C7", "color": "white", "padding": "4px 8px", "borderRadius": "6px", "fontWeight": "700", "fontSize": "13px", "marginRight": "10px", "letterSpacing": "1px"}),
                        html.Span("LUXEMBOURG EXTERNAL TRADE INTELLIGENCE", style={"fontSize": "18px", "fontWeight": "700", "color": TEXT_PRIMARY, "letterSpacing": "0.5px"}),
                    ], className="d-flex align-items-center mb-1"),
                    html.P("Eurostat Comext [ds-045409] • Multi-dimensional Trade in Goods (2000–2026)", className="text-muted mb-0", style={"fontSize": "13px"})
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.Label("Analysis Year:", style={"fontSize": "12px", "fontWeight": "600", "color": TEXT_MUTED, "marginBottom": "4px"}),
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

# ── App Main Layout with Navigation Tabs ───────────────────────────────────
app.layout = html.Div([
    create_header(),
    dbc.Container([
        create_kpi_ribbon(),
        
        # Tabs Navigation
        dbc.Tabs(id="main-tabs", active_tab="tab-overview", children=[
            dbc.Tab(label="1. Macro Overview", tab_id="tab-overview", label_style={"fontWeight": "600"}),
            dbc.Tab(label="2. Trading Partners (Q1)", tab_id="tab-partners", label_style={"fontWeight": "600"}),
            dbc.Tab(label="3. Product Categories (Q2)", tab_id="tab-products", label_style={"fontWeight": "600"}),
            dbc.Tab(label="4. Flow Deep-Dive (Q3 & Q4)", tab_id="tab-drilldown", label_style={"fontWeight": "600"}),
            dbc.Tab(label="5. Peer Benchmarks (Q5)", tab_id="tab-benchmarks", label_style={"fontWeight": "600"}),
            dbc.Tab(label="6. Seasonality & Trend Lab (Q6)", tab_id="tab-seasonality", label_style={"fontWeight": "600"}),
        ], className="mb-4 custom-tabs"),

        # Tab Content Container
        html.Div(id="tab-content", style={"minHeight": "600px"})
    ], fluid=True, style={"maxWidth": "1500px", "paddingBottom": "60px"})
], style={"backgroundColor": BACKGROUND, "minHeight": "100vh", "fontFamily": "Inter, sans-serif"})


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
        return html.Span(f"{icon} {abs(val):.1f}{suffix} YoY", style={"color": color, "fontSize": "11px", "fontWeight": "600", "marginLeft": "6px"})

    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("TOTAL EXPORTS", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.Div([
                    html.H3(fmt_eur(exp_val), style={"fontWeight": "700", "color": PRIMARY, "margin": "4px 0 0 0"}),
                    render_badge(exp_yoy)
                ], className="d-flex align-items-baseline"),
                html.Small(f"Intra-EU Share: {intra_eu_exp:.1f}%" if not pd.isna(intra_eu_exp) else "Merchandise exports", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),

        dbc.Col([
            html.Div([
                html.Span("TOTAL IMPORTS", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.Div([
                    html.H3(fmt_eur(imp_val), style={"fontWeight": "700", "color": SECONDARY, "margin": "4px 0 0 0"}),
                    render_badge(imp_yoy)
                ], className="d-flex align-items-baseline"),
                html.Small(f"Intra-EU Share: {intra_eu_imp:.1f}%" if not pd.isna(intra_eu_imp) else "Merchandise imports", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),

        dbc.Col([
            html.Div([
                html.Span("TRADE BALANCE", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.H3(fmt_eur(bal_val), style={"fontWeight": "700", "color": DANGER if bal_val < 0 else SUCCESS, "margin": "4px 0 0 0"}),
                html.Small("Merchandise goods deficit" if bal_val < 0 else "Trade surplus", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),

        dbc.Col([
            html.Div([
                html.Span("COVERAGE RATIO", style={"fontSize": "11px", "fontWeight": "700", "color": TEXT_MUTED, "letterSpacing": "0.5px"}),
                html.H3(f"{cov_val:.1f}%", style={"fontWeight": "700", "color": TEXT_PRIMARY, "margin": "4px 0 0 0"}),
                html.Small(f"Exports cover {cov_val:.0f}c per €1 imported", className="text-muted")
            ], style=KPI_CARD_STYLE)
        ], md=3, sm=6, className="mb-3"),
    ])


# ── Tab Content Router Callback ────────────────────────────────────────────
@callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab"),
    Input("global-year-dropdown", "value")
)
def render_tab_content(active_tab, selected_year):
    if active_tab == "tab-overview":
        return render_tab_overview()
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
    return html.Div("Tab not found.")


# ───────────────────────────────────────────────────────────────────────────
# TAB 1: MACRO OVERVIEW
# ───────────────────────────────────────────────────────────────────────────
def render_tab_overview():
    kpis_df = load_overview_kpis()
    if kpis_df.empty:
        return html.Div("Data not loaded.")

    # Chart 1: Long-term trade trajectory (2000-2026)
    fig_trajectory = go.Figure()
    fig_trajectory.add_trace(go.Scatter(
        x=kpis_df["year"], y=kpis_df["EXPORT"] / 1e9,
        name="Exports", mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=6),
        hovertemplate="Exports: €%{y:.2f}B<extra></extra>"
    ))
    fig_trajectory.add_trace(go.Scatter(
        x=kpis_df["year"], y=kpis_df["IMPORT"] / 1e9,
        name="Imports", mode="lines+markers",
        line=dict(color=SECONDARY, width=3),
        marker=dict(size=6),
        hovertemplate="Imports: €%{y:.2f}B<extra></extra>"
    ))
    fig_trajectory.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="<b>Evolution of Luxembourg Trade Flows (2000–2026)</b>", font=dict(size=15)),
        yaxis=dict(title="Billion Euros (€B)"),
        xaxis=dict(title="Year", tickmode="linear", dtick=2),
        hovermode="x unified"
    )

    # Chart 2: Trade Balance Trajectory
    colors = [SUCCESS if v >= 0 else DANGER for v in kpis_df["trade_balance_eur"]]
    fig_balance = go.Figure(go.Bar(
        x=kpis_df["year"], y=kpis_df["trade_balance_eur"] / 1e9,
        marker_color=colors,
        hovertemplate="Year %{x}: €%{y:.2f}B<extra></extra>"
    ))
    fig_balance.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="<b>Annual Merchandise Trade Balance (Deficit / Surplus)</b>", font=dict(size=15)),
        yaxis=dict(title="Billion Euros (€B)"),
        xaxis=dict(title="Year", tickmode="linear", dtick=2)
    )

    # Chart 3: Intra-EU Share Evolution
    fig_eu = go.Figure()
    if "intra_eu_export_share_pct" in kpis_df.columns:
        fig_eu.add_trace(go.Scatter(
            x=kpis_df["year"], y=kpis_df["intra_eu_export_share_pct"],
            name="Intra-EU Export Share %", line=dict(color=PRIMARY, width=2.5)
        ))
        fig_eu.add_trace(go.Scatter(
            x=kpis_df["year"], y=kpis_df["intra_eu_import_share_pct"],
            name="Intra-EU Import Share %", line=dict(color=SECONDARY, width=2.5)
        ))
    fig_eu.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="<b>European Integration: Share of Trade with EU Partners (%)</b>", font=dict(size=15)),
        yaxis=dict(title="Share of Total Trade (%)", range=[50, 100]),
        xaxis=dict(title="Year", tickmode="linear", dtick=2)
    )

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
            html.H6("Key Macro Takeaways", style={"fontWeight": "700", "color": TEXT_PRIMARY}),
            html.Ul([
                html.Li("Luxembourg's external trade in goods expanded from €9.3B exports / €12.5B imports in 2000 to over €16.5B exports / €25.7B imports by recent peaks."),
                html.Li("Merchandise trade maintains a structural goods deficit (between €7B and €9.5B annually), typical for advanced service-oriented financial hubs."),
                html.Li("Heavy European integration: Over 80% of exports and imports occur within the European Union (predominantly Germany, Belgium, France)."),
            ], style={"fontSize": "13px", "color": TEXT_MUTED})
        ], style={**CARD_STYLE, "backgroundColor": "#F1F5F9", "border": "none"})
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 2: TRADING PARTNERS (Q1)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_partners(selected_year):
    partners_df = load_partner_rankings()
    if partners_df.empty:
        return html.Div("No partner data available.")

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Label("Trade Flow Direction:", style={"fontWeight": "600", "fontSize": "13px", "marginRight": "12px"}),
                        dbc.RadioItems(
                            id="partner-flow-radio",
                            options=[
                                {"label": "Exports", "value": "EXPORT"},
                                {"label": "Imports", "value": "IMPORT"},
                            ],
                            value="EXPORT",
                            inline=True,
                            style={"fontSize": "13px"}
                        )
                    ], className="d-flex align-items-center mb-3"),
                    dcc.Graph(id="partner-map-graph", config={"displayModeBar": False})
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
                    html.H6("Historical Partner Share Evolution (2000–2026)", style={"fontWeight": "700", "marginBottom": "8px"}),
                    html.P("Tracking how market shares have shifted between Luxembourg's primary trading partners over time.", className="text-muted", style={"fontSize": "12px"}),
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
    Input("global-year-dropdown", "value")
)
def update_partner_tab(flow, year):
    partners_df = load_partner_rankings()
    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].copy()

    # 1. World Choropleth Map
    fig_map = px.choropleth(
        sub,
        locations="partner_code",
        color="value_eur",
        hover_name="partner_name",
        hover_data={"value_eur": ":,.0f", "market_share_pct": ":.2f%", "partner_code": False},
        color_continuous_scale="Blues" if flow == "EXPORT" else "Purples",
        projection="natural earth"
    )
    fig_map.update_geos(
        showcoastlines=True, coastlinecolor="#CBD5E1",
        showland=True, landcolor="#F8FAFC",
        showocean=True, oceancolor="#F1F5F9",
        scope="world"
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(title="€ (Value)", len=0.6, thickness=12, y=0.5)
    )

    # 2. Top 10 Partners Bar Chart
    top10 = sub.sort_values("rank").head(10).copy()
    top10 = top10.sort_values("value_eur", ascending=True)

    fig_top10 = go.Figure(go.Bar(
        x=top10["value_eur"] / 1e9,
        y=top10["partner_name"],
        orientation="h",
        marker_color=PRIMARY if flow == "EXPORT" else SECONDARY,
        text=top10["market_share_pct"].apply(lambda p: f"{p:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.2f}B (%{text})<extra></extra>"
    ))
    fig_top10.update_layout(
        **PLOT_LAYOUT,
        margin=dict(l=10, r=40, t=10, b=30),
        xaxis=dict(title="Billion Euros (€B)"),
        yaxis=dict(autorange="reversed")
    )

    # 3. Partner Share Evolution (2000-2026) for Top 6 historical partners
    top_codes = ["DE", "FR", "BE", "NL", "US", "IT", "GB", "CN"]
    hist_sub = partners_df[(partners_df["partner_code"].isin(top_codes)) & (partners_df["flow"] == flow)].copy()

    fig_hist = go.Figure()
    for i, code in enumerate(top_codes):
        p_data = hist_sub[hist_sub["partner_code"] == code].sort_values("year")
        if not p_data.empty:
            p_name = p_data["partner_name"].iloc[0]
            fig_hist.add_trace(go.Scatter(
                x=p_data["year"], y=p_data["market_share_pct"],
                name=f"{p_name} ({code})", mode="lines+markers",
                line=dict(color=CATEGORICAL[i % len(CATEGORICAL)], width=2.5),
                marker=dict(size=5),
                hovertemplate=f"{p_name}: %{{y:.1f}}% in %{{x}}<extra></extra>"
            ))
    fig_hist.update_layout(
        **PLOT_LAYOUT,
        xaxis=dict(title="Year", tickmode="linear", dtick=2),
        yaxis=dict(title="Market Share of Total (%)"),
        hovermode="x unified"
    )

    top10_title = f"Top 10 {flow.capitalize()} Partners in {year}"
    return fig_map, top10_title, fig_top10, fig_hist


# ───────────────────────────────────────────────────────────────────────────
# TAB 3: PRODUCT CATEGORIES (Q2)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_products(selected_year):
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Label("Trade Flow Direction:", style={"fontWeight": "600", "fontSize": "13px", "marginRight": "12px"}),
                        dbc.RadioItems(
                            id="prod-flow-radio",
                            options=[
                                {"label": "Exports", "value": "EXPORT"},
                                {"label": "Imports", "value": "IMPORT"},
                            ],
                            value="EXPORT",
                            inline=True,
                            style={"fontSize": "13px"}
                        )
                    ], className="d-flex align-items-center mb-3"),
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
                    html.H6("Structural Shifts in Product Composition (2000 vs Recent)", style={"fontWeight": "700", "marginBottom": "8px"}),
                    html.P("Evolution of key HS2 chapters: Historical shift from basic metals/steel to machinery, plastics, and high-value transport equipment.", className="text-muted", style={"fontSize": "12px"}),
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
    Output("prod-shift-graph", "figure"),
    Input("prod-flow-radio", "value"),
    Input("global-year-dropdown", "value")
)
def update_product_tab(flow, year):
    prods_df = load_product_rankings()
    sub = prods_df[(prods_df["year"] == year) & (prods_df["flow"] == flow)].copy()

    # 1. Treemap: HS Section -> HS2 Chapter
    sub["short_name"] = sub["hs2_name"].apply(lambda s: (s[:30] + "..") if len(s) > 30 else s)
    fig_tree = px.treemap(
        sub,
        path=["hs_section", "short_name"],
        values="value_eur",
        color="value_eur",
        color_continuous_scale="Blues" if flow == "EXPORT" else "Teal",
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
    fig_top10.update_layout(
        **PLOT_LAYOUT,
        margin=dict(l=10, r=40, t=10, b=30),
        xaxis=dict(title="Million Euros (€M)"),
        yaxis=dict(autorange="reversed")
    )

    # 3. Structural Shift (2000-2026) for key chapters
    key_chapters = ["72", "73", "84", "85", "87", "39", "40", "30", "27"]
    hist_sub = prods_df[(prods_df["hs2_code"].isin(key_chapters)) & (prods_df["flow"] == flow)].copy()

    fig_shift = go.Figure()
    for i, code in enumerate(key_chapters):
        c_data = hist_sub[hist_sub["hs2_code"] == code].sort_values("year")
        if not c_data.empty:
            c_name = c_data["hs2_name"].iloc[0].split(";")[0].title()[:25]
            fig_shift.add_trace(go.Scatter(
                x=c_data["year"], y=c_data["product_share_pct"],
                name=f"HS {code}: {c_name}", mode="lines+markers",
                line=dict(color=CATEGORICAL[i % len(CATEGORICAL)], width=2.5),
                marker=dict(size=5),
                hovertemplate=f"HS {code} ({c_name}): %{{y:.1f}}% in %{{x}}<extra></extra>"
            ))
    fig_shift.update_layout(
        **PLOT_LAYOUT,
        xaxis=dict(title="Year", tickmode="linear", dtick=2),
        yaxis=dict(title="Share of Total Trade (%)"),
        hovermode="x unified"
    )

    tree_title = f"Product Tree by HS Section & Chapter ({flow.capitalize()} {year})"
    bar_title = f"Top 10 Traded Product Chapters ({year})"
    return tree_title, fig_tree, bar_title, fig_top10, fig_shift


# ───────────────────────────────────────────────────────────────────────────
# TAB 4: PRODUCT & PARTNER DEEP-DIVE (Q3 & Q4)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_drilldown(selected_year):
    lvl2_df = load_drilldown_lvl2()
    partners = [{"label": f"{p} - {n}", "value": p} for p, n in lvl2_df[["partner_code", "partner_name"]].drop_duplicates().values] if not lvl2_df.empty else []

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Hierarchical Partner Drill-Down (Q4)", style={"fontWeight": "700"}),
                    html.P("Explore products traded with a specific partner: drill down from 2-digit (HS2) to 4-digit (HS4) and 8-digit (CN8) codes, highlighting significant flows.", className="text-muted", style={"fontSize": "12px"}),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Partner Country:", style={"fontSize": "12px", "fontWeight": "600"}),
                            dcc.Dropdown(
                                id="drill-partner-dropdown",
                                options=partners,
                                value="DE" if partners else None,
                                clearable=False,
                                style={"fontSize": "13px"}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Flow Direction:", style={"fontSize": "12px", "fontWeight": "600"}),
                            dbc.RadioItems(
                                id="drill-flow-radio",
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
                            html.Label("Granularity Level:", style={"fontSize": "12px", "fontWeight": "600"}),
                            dbc.RadioItems(
                                id="drill-level-radio",
                                options=[
                                    {"label": "2-Digit (HS2 Chapter)", "value": 2},
                                    {"label": "4-Digit (HS4 Subheading)", "value": 4},
                                    {"label": "8-Digit (CN8 Detailed)", "value": 8},
                                ],
                                value=2,
                                inline=True,
                                style={"fontSize": "13px", "marginTop": "6px"}
                            )
                        ], md=4),
                    ], className="mb-3"),

                    dcc.Graph(id="drilldown-bar-graph", config={"displayModeBar": False}),
                ], style=CARD_STYLE)
            ], md=12)
        ])
    ])


@callback(
    Output("drilldown-bar-graph", "figure"),
    Input("drill-partner-dropdown", "value"),
    Input("drill-flow-radio", "value"),
    Input("drill-level-radio", "value")
)
def update_drilldown_chart(partner, flow, level):
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
        sub["short_name"] = sub["product_code"] + ": " + sub["product_name"].apply(lambda s: s[:45] + ".." if len(s) > 45 else s)
        y_col = "short_name"
    else:
        df = load_drilldown_lvl8()
        sub = df[(df["partner_code"] == partner) & (df["flow"] == flow)].copy()
        sub = sub.sort_values("value_eur", ascending=True).tail(15)
        sub["short_name"] = sub["product_code"] + ": " + sub["product_name"].apply(lambda s: s[:45] + ".." if len(s) > 45 else s)
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
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text=f"<b>Top Significant Trade Flows for Partner {partner} ({level}-digit level)</b>", font=dict(size=14)),
        xaxis=dict(title="Million Euros (€M)"),
        yaxis=dict(autorange="reversed")
    )
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
        fig_growth.add_trace(go.Scatter(
            x=c_df["year"], y=c_df["volume_index_2000"],
            name=c_name, mode="lines+markers",
            line=dict(color=PRIMARY if c == "LU" else CATEGORICAL[i % len(CATEGORICAL)], width=4 if c == "LU" else 2),
            marker=dict(size=6 if c == "LU" else 4),
            hovertemplate=f"{c_name}: %{{y:.1f}} in %{{x}}<extra></extra>"
        ))
    fig_growth.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="<b>Trade Volume Expansion Index (2000 = 100)</b>", font=dict(size=15)),
        yaxis=dict(title="Index (2000 = 100)"),
        xaxis=dict(title="Year", tickmode="linear", dtick=2),
        hovermode="x unified"
    )

    # 2. Coverage Ratio Comparison (Exports / Imports)
    latest_yr = selected_year
    sub_yr = bench_df[bench_df["year"] == latest_yr].sort_values("coverage_ratio_pct", ascending=True)

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
    fig_cov.update_layout(
        **PLOT_LAYOUT,
        title=dict(text=f"<b>Export-to-Import Coverage Ratio in {latest_yr} (%)</b>", font=dict(size=15)),
        xaxis=dict(title="Coverage Ratio (Exports / Imports %)"),
        yaxis=dict(autorange="reversed")
    )

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
            html.H6("Comparative Takeaways", style={"fontWeight": "700", "color": TEXT_PRIMARY}),
            html.Ul([
                html.Li("Trade Growth: Luxembourg's trade in goods has expanded by ~89% since 2000, comparable to France (+84%), while the Netherlands (+236%) and Belgium (+168%) exhibited stronger transit and logistics goods expansion."),
                html.Li("Coverage Asymmetry: Germany and the Netherlands run large merchandise surpluses (>110% coverage), whereas Luxembourg sits at ~65% coverage because physical goods imports are balanced by massive net exports in cross-border financial and professional services."),
            ], style={"fontSize": "13px", "color": TEXT_MUTED})
        ], style={**CARD_STYLE, "backgroundColor": "#F1F5F9", "border": "none"})
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
                    html.P("Decomposing monthly trade flows into long-term trend-cycle and seasonal components to filter out noise.", className="text-muted", style={"fontSize": "12px"}),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Sector / Product:", style={"fontSize": "12px", "fontWeight": "600"}),
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
                            html.Label("Trade Flow Direction:", style={"fontSize": "12px", "fontWeight": "600"}),
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
                            html.Label("Series Display:", style={"fontSize": "12px", "fontWeight": "600"}),
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
                    html.P("Monthly seasonal index (1.0 = neutral). Notice the pronounced August summer factory/collective leave shutdown dip and spring peaks.", className="text-muted", style={"fontSize": "12px"}),
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
            name="Observed Raw", mode="lines",
            line=dict(color="#94A3B8", width=1.5),
            hovertemplate="Raw: €%{y:.1f}M<extra></extra>"
        ))
    if "trend" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["trend_eur"] / 1e6,
            name="12-Month Trend", mode="lines",
            line=dict(color=PRIMARY, width=3),
            hovertemplate="Trend: €%{y:.1f}M<extra></extra>"
        ))
    if "adjusted" in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=sub["date"], y=sub["seasonally_adjusted_eur"] / 1e6,
            name="Seasonally Adjusted", mode="lines",
            line=dict(color=SUCCESS, width=2, dash="dot"),
            hovertemplate="Seasonally Adjusted: €%{y:.1f}M<extra></extra>"
        ))

    fig_ts.update_layout(
        **PLOT_LAYOUT,
        title=dict(text=f"<b>Monthly Trade Evolution & Seasonal Filtering ({sub['product_name'].iloc[0]})</b>", font=dict(size=14)),
        yaxis=dict(title="Million Euros (€M)"),
        xaxis=dict(title="Date"),
        hovermode="x unified"
    )

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
        hovertemplate="Month %{x}: Seasonal Factor %{y:.3f}<extra></extra>"
    ))
    fig_fac.add_hline(y=1.0, line_dash="dash", line_color=NEUTRAL, annotation_text="Baseline (1.0)")
    fig_fac.update_layout(
        **PLOT_LAYOUT,
        yaxis=dict(title="Seasonal Factor (Ratio to Trend)", range=[0.7, 1.25]),
        xaxis=dict(title="Month of Year")
    )

    factor_title = f"Empirical Month-of-Year Seasonal Factors: {sub['product_name'].iloc[0]}"
    return fig_ts, factor_title, fig_fac


# ── Run Server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
