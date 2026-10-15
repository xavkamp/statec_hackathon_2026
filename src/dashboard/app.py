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
    apply_map_theme, create_icon_badge,
    add_iso3_column, ISO2_TO_ISO3, STATEC_NAVY, STATEC_YELLOW, STATEC_BLUE,
    STATEC_RED, STATEC_GRAY, STATEC_BG, STATEC_HEADING_STYLE,
    create_section_header, create_statec_footer, create_infobox,
    create_info_hover, INFO_HOVER_CSS
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
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&display=swap"
    ],
    title="Luxembourg Trade Intelligence (Prototype d'Analyse) — Données Ouvertes",
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
    return html.Div([
        # Top White Brand Bar (Luxembourg Trade Intelligence Prototype)
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            # TRADE.lu Logo with professional globe icon badge
                            html.Div([
                                create_icon_badge("bi bi-globe-americas", color=STATEC_NAVY, bg="#F0F4F8", size=20, box_size=42),
                                html.Div([
                                    html.Div([
                                        html.Span("TRADE", style={
                                            "fontSize": "25px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif",
                                            "color": STATEC_NAVY, "letterSpacing": "-0.5px"
                                        }),
                                        html.Span(".lu", style={
                                            "fontSize": "25px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif",
                                            "color": STATEC_YELLOW
                                        }),
                                    ]),
                                    html.Span("LUXEMBOURG TRADE INTELLIGENCE", style={
                                        "fontSize": "8.5px", "fontWeight": "800", "letterSpacing": "1.3px",
                                        "color": STATEC_GRAY, "display": "block", "marginTop": "-4px"
                                    }),
                                ], className="ms-2")
                            ], className="d-flex align-items-center", style={"minWidth": "250px"}),

                            # Vertical Divider
                            html.Div(style={"width": "1px", "height": "34px", "backgroundColor": "#CBD5E1", "margin": "0 22px"}, className="d-none d-lg-block"),

                            # Section Title
                            html.Div([
                                html.Span("COMMERCE EXTÉRIEUR DU LUXEMBOURG", style={
                                    "fontSize": "16px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif",
                                    "color": STATEC_NAVY, "letterSpacing": "0.3px", "display": "block"
                                }),
                                html.Span("OBSERVATOIRE MACROÉCONOMIQUE & RÉSILIENCE SOUVERAINE (2000–2026)", style={
                                    "fontSize": "11px", "fontWeight": "600", "color": STATEC_GRAY, "display": "block"
                                }),
                            ], className="d-none d-lg-block"),
                        ], className="d-flex align-items-center py-2")
                    ], md=8),

                    dbc.Col([
                        html.Div([
                            # Research Project Badge
                            html.Div([
                                html.Span("PROJET HACKATHON 2026", style={
                                    "fontSize": "10px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif",
                                    "color": STATEC_NAVY, "display": "block"
                                }),
                                html.Span("PROTOTYPE NON OFFICIEL", style={
                                    "fontSize": "9px", "fontWeight": "700", "color": STATEC_GRAY, "display": "block"
                                }),
                            ], className="text-end me-4 d-none d-md-block"),

                            # Year Selector
                            html.Div([
                                html.Label([
                                    html.I(className="bi bi-calendar3 me-1", style={"color": STATEC_BLUE}),
                                    "ANNÉE D'ANALYSE"
                                ], style={
                                    "fontSize": "10px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif",
                                    "color": STATEC_NAVY, "letterSpacing": "0.5px", "marginBottom": "2px"
                                }),
                                dcc.Dropdown(
                                    id="global-year-dropdown",
                                    options=[{"label": str(y), "value": y} for y in range(2025, 1999, -1)],
                                    value=2024,
                                    clearable=False,
                                    style={"fontSize": "13px", "fontWeight": "700", "borderRadius": "6px", "minWidth": "105px"}
                                )
                            ], className="d-flex flex-column align-items-end")
                        ], className="d-flex justify-content-end align-items-center py-2")
                    ], md=4)
                ], className="align-items-center")
            ], fluid=True, style={"maxWidth": "1540px"})
        ], style={"backgroundColor": "#FFFFFF", "borderBottom": "1px solid #E2E8F0"}),

        # Second Midnight Navy Banner Bar
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("PROTOTYPE ANALYTIQUE", style={
                                "backgroundColor": STATEC_YELLOW, "color": STATEC_NAVY,
                                "fontWeight": "800", "fontSize": "10px", "padding": "2px 8px",
                                "borderRadius": "4px", "marginRight": "12px", "letterSpacing": "0.5px",
                                "fontFamily": "'Montserrat', sans-serif"
                            }),
                            html.Span("Basé sur les données ouvertes Eurostat Comext [ds-045409] & STATEC (2000–2026)", style={
                                "color": "#F8FAFC", "fontSize": "12px", "fontWeight": "500"
                            }),
                        ], className="d-flex align-items-center")
                    ], md=8),
                    dbc.Col([
                        html.Div([
                            html.Span("PROTOTYPE HACKATHON 2026 — NON AFFILIÉ OFFICIELLEMENT AU STATEC", style={
                                "color": "#94A3B8", "fontSize": "10.5px", "fontWeight": "600", "letterSpacing": "0.3px",
                                "fontFamily": "'Montserrat', sans-serif"
                            }),
                        ], className="d-flex justify-content-end align-items-center")
                    ], md=4, className="d-none d-md-flex")
                ], className="align-items-center")
            ], fluid=True, style={"maxWidth": "1540px"})
        ], style={
            "backgroundColor": STATEC_NAVY, "padding": "7px 0",
            "marginBottom": "24px", "borderBottom": f"3px solid {STATEC_YELLOW}",
            "boxShadow": "0 2px 8px rgba(0, 26, 56, 0.15)"
        })
    ])


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
                                create_icon_badge("bi bi-bank2", color=STATEC_NAVY, bg="#FFF9E6", size=22, box_size=46),
                                html.Div([
                                    html.Div([
                                        html.Strong("NATIONAL LEADERSHIP BRIEFING", style={"fontSize": "14px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.5px"}),
                                        html.Span("EXECUTIVE • PRIORITY OVERVIEW", style={"backgroundColor": STATEC_NAVY, "color": STATEC_YELLOW, "fontSize": "10px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "padding": "2px 8px", "borderRadius": "4px", "marginLeft": "10px"})
                                    ], className="d-flex align-items-center"),
                                    html.P(
                                        "Answers Pressing Questions First: Sovereign economic resilience, critical supply chain bottlenecks, and macro health.",
                                        className="text-muted mb-0", style={"fontSize": "12px", "marginTop": "2px"}
                                    )
                                ], className="ms-3")
                            ], className="d-flex align-items-center"),
                        ], id="btn-mode-leaders", n_clicks=0, style={
                            "cursor": "pointer", "padding": "16px 20px", "borderRadius": "8px",
                            "border": f"2px solid {STATEC_YELLOW}", "backgroundColor": "#FFFFFF",
                            "transition": "all 0.2s ease-in-out", "boxShadow": "0 4px 14px rgba(255, 200, 0, 0.28)"
                        })
                    ], md=6, className="mb-2 mb-md-0"),

                    dbc.Col([
                        html.Div([
                            html.Div([
                                create_icon_badge("bi bi-graph-up-arrow", color=STATEC_BLUE, bg="#EFF6FF", size=22, box_size=46),
                                html.Div([
                                    html.Div([
                                        html.Strong("DATA ANALYST DEEP-DIVE SUITE", style={"fontSize": "14px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.5px"}),
                                        html.Span("ADVANCED DRILL-DOWN", style={"backgroundColor": "#F1F5F9", "color": STATEC_GRAY, "fontSize": "10px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "padding": "2px 8px", "borderRadius": "4px", "marginLeft": "10px"})
                                    ], className="d-flex align-items-center"),
                                    html.P(
                                        "Explore Details Afterwards: Granular tariff lines (HS2→CN8), full world maps, seasonal modeling & peer benchmarks.",
                                        className="text-muted mb-0", style={"fontSize": "12px", "marginTop": "2px"}
                                    )
                                ], className="ms-3")
                            ], className="d-flex align-items-center"),
                        ], id="btn-mode-analysts", n_clicks=0, style={
                            "cursor": "pointer", "padding": "16px 20px", "borderRadius": "8px",
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
    ], fluid=True, style={"maxWidth": "1540px", "paddingBottom": "30px"}),
    create_statec_footer()
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
            style={"color": color, "fontSize": "12px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "marginLeft": "8px"}
        )

    return html.Div([
        # "CHIFFRES CLÉS" Section Title with interactive hover infobox
        html.Div([
            html.Div([
                html.H5(f"CHIFFRES CLÉS DU COMMERCE EXTÉRIEUR ({selected_year})", style=STATEC_HEADING_STYLE, className="mb-0 d-inline-block"),
                create_info_hover(
                    "Comprendre les Chiffres Clés : Déficit des Biens & Rôle des Services",
                    [
                        html.Span("Le solde physique déficitaire des marchandises ("),
                        html.Strong(fmt_eur(bal_val)),
                        html.Span(f", taux de couverture de {cov_val:.1f}%) est une caractéristique structurelle du Luxembourg : les biens importés (énergie, véhicules, denrées alimentaires) sont intégralement financés par l'excédent massif des services financiers et de fonds d'investissement (+25 Mrd €), assurant un compte courant souverain très excédentaire."),
                    ],
                    icon="ⓘ",
                    variant="navy"
                )
            ], className="d-flex align-items-center mb-1"),
            html.Div(style={"width": "42px", "height": "4px", "backgroundColor": STATEC_YELLOW, "borderRadius": "2px", "marginBottom": "16px"}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-box-arrow-up-right", color=PRIMARY, bg="#EBF5FF", size=15, box_size=32),
                        html.Span("EXPORTATIONS TOTALES", style={"fontSize": "11px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_GRAY, "letterSpacing": "0.8px", "marginLeft": "8px"}),
                    ], className="d-flex align-items-center mb-1"),
                    html.Div([
                        html.H2(fmt_eur(exp_val), style={"fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": PRIMARY, "margin": "2px 0 0 0"}),
                        render_badge(exp_yoy)
                    ], className="d-flex align-items-baseline"),
                    html.Small(f"Part intra-UE : {intra_eu_exp:.1f}% des biens exportés" if not pd.isna(intra_eu_exp) else "Exportations physiques", className="text-muted", style={"fontSize": "11px"})
                ], style={**KPI_CARD_STYLE, "borderTop": f"4px solid {PRIMARY}"})
            ], md=3, sm=6, className="mb-3"),

            dbc.Col([
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-box-arrow-in-down-left", color=SECONDARY, bg="#F1F5F9", size=15, box_size=32),
                        html.Span("IMPORTATIONS TOTALES", style={"fontSize": "11px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_GRAY, "letterSpacing": "0.8px", "marginLeft": "8px"}),
                    ], className="d-flex align-items-center mb-1"),
                    html.Div([
                        html.H2(fmt_eur(imp_val), style={"fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": SECONDARY, "margin": "2px 0 0 0"}),
                        render_badge(imp_yoy)
                    ], className="d-flex align-items-baseline"),
                    html.Small(f"Part intra-UE : {intra_eu_imp:.1f}% des biens importés" if not pd.isna(intra_eu_imp) else "Importations physiques", className="text-muted", style={"fontSize": "11px"})
                ], style={**KPI_CARD_STYLE, "borderTop": f"4px solid {SECONDARY}"})
            ], md=3, sm=6, className="mb-3"),

            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div([
                            create_icon_badge("bi bi-scale", color=DANGER if bal_val < 0 else SUCCESS, bg="#FEF2F2" if bal_val < 0 else "#ECFDF5", size=15, box_size=32),
                            html.Span("SOLDE COMMERCIAL", style={"fontSize": "11px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_GRAY, "letterSpacing": "0.8px", "marginLeft": "8px"}),
                        ], className="d-flex align-items-center"),
                        create_info_hover(
                            "Solde Commercial & Couverture",
                            f"Le déficit de {fmt_eur(bal_val)} en biens physiques est structurel. Les exportations financent {cov_val:.1f}% des importations de marchandises, le solde étant largement couvert par les services.",
                            icon="ⓘ",
                            variant="danger" if bal_val < 0 else "success",
                            align="right"
                        )
                    ], className="d-flex align-items-center justify-content-between mb-1"),
                    html.H2(fmt_eur(bal_val), style={"fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": DANGER if bal_val < 0 else SUCCESS, "margin": "2px 0 0 0"}),
                    html.Small("Déficit structurel des biens physiques" if bal_val < 0 else "Excédent commercial des biens", className="text-muted", style={"fontSize": "11px"})
                ], style={**KPI_CARD_STYLE, "borderTop": f"4px solid {DANGER if bal_val < 0 else SUCCESS}"})
            ], md=3, sm=6, className="mb-3"),

            dbc.Col([
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-pie-chart-fill", color="#B45309", bg="#FEF9E7", size=15, box_size=32),
                        html.Span("TAUX DE COUVERTURE", style={"fontSize": "11px", "fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_GRAY, "letterSpacing": "0.8px", "marginLeft": "8px"}),
                    ], className="d-flex align-items-center mb-1"),
                    html.H2(f"{cov_val:.1f}%", style={"fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "margin": "2px 0 0 0"}),
                    html.Small(f"Les exports financent {cov_val:.0f}c par €1 importé", className="text-muted", style={"fontSize": "11px"})
                ], style={**KPI_CARD_STYLE, "borderTop": f"4px solid {STATEC_YELLOW}"})
            ], md=3, sm=6, className="mb-3"),
        ])
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
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "8px",
        "border": f"2px solid {STATEC_YELLOW}", "backgroundColor": "#FFFFFF",
        "transition": "all 0.2s ease-in-out", "boxShadow": "0 4px 14px rgba(255, 200, 0, 0.28)"
    }
    inactive_lead_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "8px",
        "border": f"1px solid {BORDER}", "backgroundColor": SURFACE,
        "transition": "all 0.2s ease-in-out"
    }

    active_ana_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "8px",
        "border": f"2px solid {STATEC_YELLOW}", "backgroundColor": "#FFFFFF",
        "transition": "all 0.2s ease-in-out", "boxShadow": "0 4px 14px rgba(255, 200, 0, 0.28)"
    }
    inactive_ana_style = {
        "cursor": "pointer", "padding": "16px 20px", "borderRadius": "8px",
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
    tab_label_style = {
        "fontWeight": "700", "fontSize": "12.5px",
        "fontFamily": "'Montserrat', sans-serif", "color": STATEC_GRAY,
        "padding": "10px 18px", "border": "none", "letterSpacing": "0.3px"
    }
    tab_active_style = {
        "fontWeight": "800", "fontSize": "12.5px",
        "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY,
        "border": "none", "borderBottom": f"3px solid {STATEC_YELLOW}",
        "backgroundColor": "transparent", "letterSpacing": "0.3px"
    }
    if mode == "leaders":
        default_tab = active_tab_store if active_tab_store in ["tab-resilience", "tab-macro", "tab-geopolitics"] else "tab-resilience"
        return dbc.Tabs(id="sub-tabs", active_tab=default_tab, children=[
            dbc.Tab(label="1. RÉSILIENCE & APPROVISIONNEMENT SOUVERAIN", tab_id="tab-resilience", label_style=tab_label_style, active_label_style=tab_active_style),
            dbc.Tab(label="2. SANTÉ MACROÉCONOMIQUE & TRAJECTOIRE", tab_id="tab-macro", label_style=tab_label_style, active_label_style=tab_active_style),
            dbc.Tab(label="3. EXPOSITION GÉOPOLITIQUE & CHOCS SAISONNIERS", tab_id="tab-geopolitics", label_style=tab_label_style, active_label_style=tab_active_style),
        ], style={"borderBottom": "2px solid #E2E8F0"})
    else:
        default_tab = active_tab_store if active_tab_store in ["tab-studio", "tab-partners", "tab-products", "tab-drilldown", "tab-seasonality", "tab-benchmarks"] else "tab-studio"
        return dbc.Tabs(id="sub-tabs", active_tab=default_tab, children=[
            dbc.Tab(label="1. STUDIO GÉO-TARIFAIRE & DRILL-DOWN (Q1–Q4)", tab_id="tab-studio", label_style=tab_label_style, active_label_style=tab_active_style),
            dbc.Tab(label="2. LABORATOIRE DE SAISONNALITÉ (Q6)", tab_id="tab-seasonality", label_style=tab_label_style, active_label_style=tab_active_style),
            dbc.Tab(label="3. BENCHMARKS COMPARATIFS (Q5)", tab_id="tab-benchmarks", label_style=tab_label_style, active_label_style=tab_active_style),
        ], style={"borderBottom": "2px solid #E2E8F0"})


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
    elif active_tab in ["tab-studio", "tab-partners", "tab-products", "tab-drilldown"]:
        return render_studio_tab(selected_year)
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
        create_section_header(
            "TRAJECTOIRE & SANTÉ MACROÉCONOMIQUE (2000–2026)",
            "Analyse sur 25 ans des volumes d'échanges, du solde structurel des biens et de l'intégration dans le marché unique européen.",
            badge_text="25 Ans • Macroéconomie",
            badge_color=STATEC_NAVY,
            info_title="Intégration Européenne (80–90% du Commerce)",
            info_content="Entre 80% et 90% des flux physiques de biens sont réalisés au sein du marché unique de l'UE. Cette intégration offre une sécurité juridique totale et l'absence de droits de douane, mais expose l'économie aux aléas de la demande de ses voisins directs (Allemagne, Belgique, France).",
            info_icon="bi bi-flag-fill",
            info_variant="primary"
        ),
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
            html.H6("FAITS SAILLANTS MACROÉCONOMIQUES (2000–2026)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.5px"}),
            html.Ul([
                html.Li("Croissance des flux : Le commerce de marchandises du Luxembourg est passé de 9,1 Mrd € d'exports / 12,2 Mrd € d'imports en 2000 à plus de 16,5 Mrd € d'exports / 25,7 Mrd € d'imports à ses récents sommets (+89% en volume total)."),
                html.Li("Déficit structurel des biens : Le déficit commercial annuel en marchandises (-7 à -9,2 Mrd €) est une caractéristique structurelle des économies de services et de hubs financiers mondiaux, largement compensé par les excédents colossaux des services financiers et de gestion de fonds (+25 Mrd €)."),
                html.Li("Intégration européenne intense : Entre 80% et 90% des flux physiques de biens sont réalisés au sein de l'Union européenne, avec la Belgique, l'Allemagne et la France constituant le socle indéboulonnable des approvisionnements."),
            ], style={"fontSize": "13px", "color": TEXT_MUTED, "marginBottom": "0"})
        ], style={**CARD_STYLE, "backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}", "borderLeft": f"4px solid {STATEC_YELLOW}"})
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

    # 3. Executive Geopolitical Exposure Map
    sub_map = add_iso3_column(sub).dropna(subset=["iso3"]).copy()
    tier_colors = {
        "Direct Neighbors (73.6% of Goods)": "#1D4ED8",
        "EU Single Market Partners (17.9%)": "#0EA5E9",
        "Strategic Non-EU Suppliers": "#8B5CF6",
        "Other Partners": "#CBD5E1"
    }

    def assign_geo_tier(code):
        if code in neighbors:
            return "Direct Neighbors (73.6% of Goods)"
        elif code in eu_codes:
            return "EU Single Market Partners (17.9%)"
        elif code in non_eu_sub["partner_code"].values:
            return "Strategic Non-EU Suppliers"
        return "Other Partners"

    sub_map["tier"] = sub_map["partner_code"].apply(assign_geo_tier)

    fig_geo = go.Figure()
    for tier_name, tier_color in tier_colors.items():
        t_sub = sub_map[sub_map["tier"] == tier_name]
        if not t_sub.empty:
            fig_geo.add_trace(go.Choropleth(
                locations=t_sub["iso3"],
                z=[1] * len(t_sub),
                name=tier_name,
                locationmode="ISO-3",
                colorscale=[[0, tier_color], [1, tier_color]],
                showscale=False,
                marker_line_color="#94A3B8",
                marker_line_width=0.8,
                customdata=np.stack([
                    t_sub["partner_code"],
                    t_sub["partner_name"],
                    t_sub["value_eur"],
                    t_sub["market_share_pct"],
                    t_sub["rank"],
                    t_sub["tier"]
                ], axis=-1),
                hovertemplate="<b>%{customdata[1]}</b> (%{customdata[0]})<br>" +
                              "Strategic Tier: <b>%{customdata[5]}</b><br>" +
                              "Imports: €%{customdata[2]:,.0f}<br>" +
                              "Share of All Imports: %{customdata[3]:.2f}%<br>" +
                              "National Rank: #%{customdata[4]}<extra></extra>"
            ))

    # Add Luxembourg Pinpoint
    fig_geo.add_trace(go.Scattergeo(
        locations=["LUX"],
        locationmode="ISO-3",
        mode="markers+text",
        marker=dict(size=14, color=STATEC_YELLOW, symbol="star", line=dict(color=STATEC_NAVY, width=2)),
        text=["★ Luxembourg (Hub)"],
        textposition="top right",
        textfont=dict(family="'Montserrat', sans-serif", size=12, color=STATEC_NAVY, weight="bold"),
        hoverinfo="skip",
        showlegend=False
    ))

    apply_map_theme(fig_geo, scope="europe")
    fig_geo.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(family="'Inter', sans-serif", size=11, color=STATEC_NAVY),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#CBD5E1",
            borderwidth=1
        )
    )

    # 4. Seasonal timeline chart for leadership (August slump highlight)
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
        create_section_header(
            f"EXPOSITION GÉOPOLITIQUE & CHOCS SAISONNIERS ({selected_year})",
            "Analyse des dépendances géographiques : concentration sur les voisins directs (BE, DE, FR), exposition aux fournisseurs tiers hors-UE et résilience aux arrêts saisonniers estivaux.",
            badge_text="Alerte Souveraineté",
            badge_color=STATEC_RED,
            info_title="Effet 'Rotterdam-Anvers' & Congé Collectif",
            info_content=[
                html.Span("1. "),
                html.Strong("Effet Rotterdam-Anvers : "),
                html.Span("Plus de 33% des marchandises physiques arrivent via les plateformes portuaires belges et néerlandaises (effet de transit maritime). Tout goulot d'étranglement sur la mer du Nord se répercute sous 48 heures au Grand-Duché. "),
                html.Br(),
                html.Span("2. "),
                html.Strong("Choc d'Août (-14,4%) : "),
                html.Span("Ralentissement cyclique récurrent causé par le congé collectif du secteur du bâtiment et les fermetures annuelles des usines européennes."),
            ],
            info_icon="bi bi-shield-exclamation",
            info_variant="danger"
        ),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("CONCENTRATION RÉGIONALE DES IMPORTATIONS", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                    html.P(f"En {selected_year}, plus de 73% des biens physiques importés proviennent de Belgique, d'Allemagne et de France.", className="text-muted", style={"fontSize": "12px"}),
                    dcc.Graph(figure=fig_donut, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=5),
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_non_eu, config={"displayModeBar": False})
                ], style=CARD_STYLE)
            ], md=7),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("CARTOGRAPHIE DE SOUVERAINETÉ : DÉPENDANCES PAR PALIER STRATÉGIQUE", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                    html.P("Visualisation des corridors d'approvisionnement : Voisins immédiats (73,6%), Marché unique européen (17,9%) et Fournisseurs stratégiques hors-UE.", className="text-muted", style={"fontSize": "12px"}),
                    dcc.Graph(figure=fig_geo, config={"displayModeBar": False}, style={"height": "440px"})
                ], style=CARD_STYLE)
            ], md=12)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(figure=fig_aug, config={"displayModeBar": False}),
                    html.Div([
                        html.Strong("Recommandation Opérationnelle pour Décideurs : ", style={"color": DANGER, "fontSize": "12px", "fontFamily": "'Montserrat', sans-serif"}),
                        html.Span(
                            "La contraction de -14,4% observée chaque mois d'août est d'origine saisonnière (congés industriels et congé collectif du bâtiment). Les stocks stratégiques prioritaires (médicaments d'urgence hospitaliers, matériaux de construction, carburants de chauffe) doivent impérativement être consolidés en juin et juillet.",
                            style={"fontSize": "12px", "color": TEXT_MUTED}
                        )
                    ], className="mt-2 p-3 rounded", style={"backgroundColor": "#FEF2F2", "border": "1px solid #FCA5A5", "borderLeft": f"4px solid {DANGER}"})
                ], style=CARD_STYLE)
            ], md=12)
        ])
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 1 (ANALYST): STUDIO GÉO-TARIFAIRE & DRILL-DOWN BILATÉRAL (Q1–Q4)
# ───────────────────────────────────────────────────────────────────────────

ISO2_NAMES = {
    "DE": "Allemagne", "FR": "France", "BE": "Belgique", "NL": "Pays-Bas",
    "US": "États-Unis", "IT": "Italie", "GB": "Royaume-Uni", "ES": "Espagne",
    "CN": "Chine", "CH": "Suisse", "PL": "Pologne", "AT": "Autriche",
    "SE": "Suède", "JP": "Japon", "CZ": "Tchéquie", "DK": "Danemark",
    "IE": "Irlande", "PT": "Portugal", "TR": "Turquie", "IN": "Inde",
    "BR": "Brésil", "KR": "Corée du Sud", "NO": "Norvège", "RU": "Russie",
    "CA": "Canada", "MX": "Mexique", "AU": "Australie", "ZA": "Afrique du Sud",
    "HU": "Hongrie", "RO": "Roumanie", "SG": "Singapour", "LU": "Luxembourg"
}

def get_country_name(iso2):
    return ISO2_NAMES.get(str(iso2).upper(), str(iso2))


def get_partner_products(partner_code, flow, year, level=2):
    """
    Unified product extractor for any trading partner across HS2, HS4, and CN8.
    Returns (df, is_fallback, level_label).
    """
    level = int(level)
    partner_code = str(partner_code).upper()
    top_5 = ["BE", "DE", "FR", "NL", "US"]

    if level == 8 and partner_code in top_5:
        df8 = load_drilldown_lvl8()
        sub = df8[(df8["partner_code"] == partner_code) & (df8["flow"] == flow)].copy()
        if not sub.empty:
            sub = sub.sort_values("value_eur", ascending=False)
            sub["short_name"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:50] + ".." if len(str(s)) > 50 else str(s))
            return sub, False, "CN8 (Lignes tarifaires douanières à 8 chiffres)"

    if level == 4 and partner_code in top_5:
        df4 = load_drilldown_lvl4()
        sub = df4[(df4["partner_code"] == partner_code) & (df4["flow"] == flow)].copy()
        if not sub.empty:
            sub = sub.sort_values("value_eur", ascending=False)
            sub["short_name"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:50] + ".." if len(str(s)) > 50 else str(s))
            return sub, False, "HS4 (Sous-positions tarifaires à 4 chiffres)"

    # Universal Fallback for any of the 238 countries in product_partners
    partners_df = load_product_partners()
    valid_years = sorted(partners_df["year"].unique())
    target_year = year if year in valid_years else max(valid_years)

    sub = partners_df[(partners_df["partner_code"] == partner_code) &
                      (partners_df["flow"] == flow) &
                      (partners_df["year"] == target_year)].copy()

    if sub.empty:
        sub = partners_df[(partners_df["partner_code"] == partner_code) & (partners_df["flow"] == flow)].copy()
        if not sub.empty:
            target_year = sub["year"].max()
            sub = sub[sub["year"] == target_year]

    if not sub.empty:
        sub = sub.rename(columns={"hs2_code": "product_code", "hs2_name": "product_name"})
        sub = sub.sort_values("value_eur", ascending=False)
        sub["short_name"] = "Ch." + sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:50] + ".." if len(str(s)) > 50 else str(s))
        is_fallback = (level in [4, 8] and partner_code not in top_5)
        return sub, is_fallback, "HS2 (Chapitres à 2 chiffres)"

    return pd.DataFrame(), False, "Données non disponibles"


def render_studio_tab(selected_year):
    prod_df = load_product_rankings()
    prod_options = []
    if not prod_df.empty:
        hs2_unique = prod_df[["hs2_code", "hs2_name"]].drop_duplicates().sort_values("hs2_code")
        prod_options = [
            {"label": f"Ch. {r['hs2_code']} — {r['hs2_name'][:45]}", "value": str(r["hs2_code"])}
            for _, r in hs2_unique.iterrows()
        ]
    default_prod = "87" if any(o["value"] == "87" for o in prod_options) else (prod_options[0]["value"] if prod_options else "87")

    initial_layout = render_studio_perspective_layout("country", selected_year)

    return html.Div([
        # Section Header with Info Tooltip
        create_section_header(
            f"STUDIO GÉO-TARIFAIRE & DRILL-DOWN BILATÉRAL ({selected_year})",
            "Espace analytique unifié interconnecté : cliquez sur n'importe quel pays sur la carte ou dans le palmarès pour projeter en temps réel son panier de produits (Q2), ses fournisseurs alternatifs (Q3) et plonger jusqu'aux lignes douanières CN8 à 8 chiffres (Q4).",
            badge_text="Eurostat Q1 • Q2 • Q3 • Q4",
            badge_color=STATEC_BLUE,
            info_title="Studio Unifié & Niveaux de Nomenclature Douanière",
            info_content=[
                html.P("Ce studio interconnecte les 4 dimensions fondamentales du commerce extérieur :", style={"fontWeight": "600", "marginBottom": "6px"}),
                html.Ul([
                    html.Li("Q1 (Partenaires) : Carte choroplèthe mondiale et classement des flux bilatéraux."),
                    html.Li("Q2 (Produits) : Répartition du panier d'échanges et sections macroéconomiques."),
                    html.Li("Q3 (Fournisseurs & HHI) : Indice de dépendance et cartographie des pays d'origine par produit."),
                    html.Li("Q4 (Drill-Down Tarifaire) : Du chapitre (HS2) à la sous-position (HS4) et à la ligne fine douanière (CN8)."),
                ], style={"paddingLeft": "18px", "marginBottom": "0"})
            ],
            info_icon="bi bi-grid-1x2-fill",
            info_variant="primary"
        ),

        # Master Interactive Studio Control Ribbon
        html.Div([
            dbc.Row([
                # Perspective Toggle
                dbc.Col([
                    html.Label([
                        html.I(className="bi bi-sliders me-1 text-primary"),
                        html.Span("Mode d'Exploration :", style={"fontWeight": "700", "fontSize": "11.5px", "color": STATEC_NAVY})
                    ], className="d-block mb-1"),
                    dbc.RadioItems(
                        id="studio-perspective-radio",
                        options=[
                            {"label": "🌍 Par Pays (Q1 & Q4)", "value": "country"},
                            {"label": "📦 Par Produit (Q2 & Q3)", "value": "product"},
                        ],
                        value="country",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-primary btn-sm px-3 py-1",
                        label_checked_class_name="btn btn-primary btn-sm px-3 py-1 text-white fw-bold",
                        style={"fontSize": "12px"}
                    )
                ], md=4, sm=12, className="mb-2 mb-md-0"),

                # Flow Radio
                dbc.Col([
                    html.Label([
                        html.I(className="bi bi-arrow-left-right me-1 text-primary"),
                        html.Span("Flux Douanier :", style={"fontWeight": "700", "fontSize": "11.5px", "color": STATEC_NAVY})
                    ], className="d-block mb-1"),
                    dbc.RadioItems(
                        id="studio-flow-radio",
                        options=[
                            {"label": "Importations (Fournisseurs)", "value": "IMPORT"},
                            {"label": "Exportations (Clients)", "value": "EXPORT"},
                        ],
                        value="IMPORT",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-2 py-1 text-white fw-bold",
                        style={"fontSize": "12px"}
                    )
                ], md=3, sm=6, className="mb-2 mb-md-0"),

                # Geographic Scope Radio
                dbc.Col([
                    html.Label([
                        html.I(className="bi bi-geo-alt me-1 text-primary"),
                        html.Span("Périmètre Géo :", style={"fontWeight": "700", "fontSize": "11.5px", "color": STATEC_NAVY})
                    ], className="d-block mb-1"),
                    dbc.RadioItems(
                        id="studio-scope-radio",
                        options=[
                            {"label": "Monde", "value": "GLOBAL"},
                            {"label": "UE-27", "value": "EU27"},
                            {"label": "Extra-UE", "value": "EXTRA_EU"},
                        ],
                        value="GLOBAL",
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-dark btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-dark btn-sm px-2 py-1 text-white fw-bold",
                        style={"fontSize": "12px"}
                    )
                ], md=2, sm=6, className="mb-2 mb-md-0"),

                # Granularity Selector
                dbc.Col([
                    html.Label([
                        html.I(className="bi bi-layers me-1 text-primary"),
                        html.Span("Nomenclature Tarifaire :", style={"fontWeight": "700", "fontSize": "11.5px", "color": STATEC_NAVY})
                    ], className="d-block mb-1"),
                    dbc.RadioItems(
                        id="studio-granularity-radio",
                        options=[
                            {"label": "HS2 (2 ch.)", "value": 2},
                            {"label": "HS4 (4 ch.)", "value": 4},
                            {"label": "CN8 (8 ch.)", "value": 8},
                        ],
                        value=2,
                        inline=True,
                        className="btn-group",
                        input_class_name="btn-check",
                        label_class_name="btn btn-outline-secondary btn-sm px-2 py-1",
                        label_checked_class_name="btn btn-secondary btn-sm px-2 py-1 text-white fw-bold",
                        style={"fontSize": "12px"}
                    )
                ], md=3, sm=12)
            ], align="center")
        ], style={
            "backgroundColor": "#FFFFFF", "borderRadius": "10px", "padding": "12px 18px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.04)", "border": f"1px solid {BORDER}",
            "marginBottom": "16px"
        }),

        # Stores to preserve selection state across interactions
        dcc.Store(id="studio-selected-partner", data="DE"),
        dcc.Store(id="studio-selected-product", data=default_prod),

        # Dynamic Perspective Container (pre-populated with initial layout)
        html.Div(initial_layout, id="studio-perspective-container")
    ])


# ── Studio Callbacks ───────────────────────────────────────────────────────

@callback(
    Output("studio-selected-partner", "data"),
    Input("studio-world-map", "clickData"),
    Input("studio-top-partners-bar", "clickData"),
    State("studio-selected-partner", "data")
)
def update_studio_selected_partner(map_click, bar_click, current_partner):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_partner or "DE"
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "studio-world-map" and map_click:
        pt = map_click["points"][0]
        if "customdata" in pt and pt["customdata"] is not None:
            c = pt["customdata"]
            res = c[0] if isinstance(c, (list, tuple, np.ndarray)) else str(c)
            return str(res).strip().upper()
        if "location" in pt:
            for c2, c3 in ISO2_TO_ISO3.items():
                if c3 == pt["location"]:
                    return c2
    elif trigger_id == "studio-top-partners-bar" and bar_click:
        pt = bar_click["points"][0]
        if "customdata" in pt and pt["customdata"] is not None:
            c = pt["customdata"]
            res = c[0] if isinstance(c, (list, tuple, np.ndarray)) else str(c)
            return str(res).strip().upper()
        if "y" in pt:
            y_str = str(pt["y"])
            if "(" in y_str and ")" in y_str:
                return y_str.split("(")[-1].split(")")[0].strip().upper()
            for c2, name in ISO2_NAMES.items():
                if name.lower() in y_str.lower():
                    return c2
    return current_partner or "DE"


@callback(
    Output("studio-perspective-container", "children"),
    Input("studio-perspective-radio", "value"),
    Input("global-year-dropdown", "value")
)
def render_studio_perspective_layout(perspective, year):
    year = int(year or 2024)
    if perspective == "country":
        # Pre-compute initial figures to guarantee instant display
        init_map, init_bar, init_hist = update_studio_partner_left("IMPORT", year, "GLOBAL", "DE")
        init_spotlight, init_treemap, init_prod_bar = update_studio_partner_right("DE", "IMPORT", year, 2)

        return dbc.Row([
            # Left Column (Spatial & Rankings Q1)
            dbc.Col([
                # Interactive World Map Card
                html.Div([
                    html.Div([
                        html.Div([
                            create_icon_badge("bi bi-globe-americas", color=STATEC_BLUE, bg="#DBEAFE", size=16, box_size=32),
                            html.Div([
                                html.H6("CARTOGRAPHIE MONDIALE DES ÉCHANGES (Q1)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px"}),
                                html.P("Cliquez sur un pays sur la carte ou le bar-chart pour projeter son panier de biens à droite.", style={"fontSize": "11px", "color": TEXT_MUTED, "marginBottom": "0"}),
                            ], className="ms-2")
                        ], className="d-flex align-items-center"),
                    ], className="mb-2"),
                    dcc.Graph(id="studio-world-map", figure=init_map, config={"displayModeBar": False})
                ], style={**CARD_STYLE, "marginBottom": "16px"}),

                # Top 10 Partners Bar Card
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-bar-chart-line-fill", color=PRIMARY, bg="#EFF6FF", size=15, box_size=30),
                        html.H6("PALMARÈS DES PARTENAIRES COMMERCIAUX (Q1)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px", "marginLeft": "8px"}),
                    ], className="d-flex align-items-center mb-2"),
                    dcc.Graph(id="studio-top-partners-bar", figure=init_bar, config={"displayModeBar": False})
                ], style={**CARD_STYLE, "marginBottom": "16px"}),

                # Historical Trade Trend Card
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-graph-up-arrow", color="#059669", bg="#D1FAE5", size=15, box_size=30),
                        html.H6("TRAJECTOIRE HISTORIQUE BILATÉRALE (2000–2024)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px", "marginLeft": "8px"}),
                    ], className="d-flex align-items-center mb-2"),
                    dcc.Graph(id="studio-partner-history-chart", figure=init_hist, config={"displayModeBar": False})
                ], style=CARD_STYLE),
            ], md=7, sm=12),

            # Right Column (Bilateral Products & CN8 Drill-Down Q2 & Q4)
            dbc.Col([
                # Selected Country Spotlight Header Card
                html.Div(init_spotlight, id="studio-partner-spotlight-container"),

                # Products Treemap Card
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-boxes", color=STATEC_BLUE, bg="#DBEAFE", size=16, box_size=32),
                        html.Div([
                            html.H6("COMPOSITION DU PANIER ÉCHANGÉ (Q2 & Q4)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px"}),
                            html.P("Survolez ou cliquez sur les rectangles pour inspecter les flux par catégorie de biens.", style={"fontSize": "11px", "color": TEXT_MUTED, "marginBottom": "0"}),
                        ], className="ms-2")
                    ], className="d-flex align-items-center mb-2"),
                    dcc.Graph(id="studio-partner-treemap", figure=init_treemap, config={"displayModeBar": False})
                ], style={**CARD_STYLE, "marginBottom": "16px"}),

                # Top Products Bar Card
                html.Div([
                    html.Div([
                        create_icon_badge("bi bi-list-ol", color=PRIMARY, bg="#EFF6FF", size=15, box_size=30),
                        html.H6("PRINCIPALES MARCHANDISES AU NIVEAU SÉLECTIONNÉ", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px", "marginLeft": "8px"}),
                    ], className="d-flex align-items-center mb-2"),
                    dcc.Graph(id="studio-partner-products-bar", figure=init_prod_bar, config={"displayModeBar": False})
                ], style=CARD_STYLE),
            ], md=5, sm=12)
        ])
    else:
        # Product Perspective (Q2 & Q3)
        prod_df = load_product_rankings()
        prod_options = []
        if not prod_df.empty:
            hs2_unique = prod_df[["hs2_code", "hs2_name"]].drop_duplicates().sort_values("hs2_code")
            prod_options = [
                {"label": f"Ch. {r['hs2_code']} — {r['hs2_name'][:50]}", "value": str(r["hs2_code"])}
                for _, r in hs2_unique.iterrows()
            ]
        default_prod = "87" if any(o["value"] == "87" for o in prod_options) else (prod_options[0]["value"] if prod_options else "87")

        init_p_map, init_p_supp, init_p_kpi, init_p_hist = update_studio_product_perspective(default_prod, "IMPORT", year, "GLOBAL")

        return html.Div([
            # Product Selector Bar
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Label([
                            create_icon_badge("bi bi-box-seam", color=PRIMARY, bg="#EFF6FF", size=14, box_size=28),
                            html.Span("Sélectionnez la Marchandise / Chapitre HS2 à Analyser :", style={"fontWeight": "700", "fontSize": "12px", "color": STATEC_NAVY, "marginLeft": "8px"})
                        ], className="d-flex align-items-center mb-1"),
                        dcc.Dropdown(
                            id="studio-product-dropdown",
                            options=prod_options,
                            value=default_prod,
                            clearable=False,
                            style={"fontSize": "13px"}
                        )
                    ], md=12)
                ])
            ], style={"backgroundColor": "#FFFFFF", "borderRadius": "8px", "padding": "12px 16px", "border": f"1px solid {BORDER}", "marginBottom": "16px"}),

            dbc.Row([
                # Left Column: Supplier Map & Concentration Bar (Q3)
                dbc.Col([
                    html.Div([
                        html.Div([
                            create_icon_badge("bi bi-pin-map-fill", color=STATEC_BLUE, bg="#DBEAFE", size=16, box_size=32),
                            html.Div([
                                html.H6("CARTOGRAPHIE DES FOURNISSEURS / CLIENTS DE CE BIEN (Q3)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px"}),
                                html.P("Intensité géographique des pays d'origine ou de destination pour le produit sélectionné.", style={"fontSize": "11px", "color": TEXT_MUTED, "marginBottom": "0"}),
                            ], className="ms-2")
                        ], className="d-flex align-items-center mb-2"),
                        dcc.Graph(id="studio-product-map", figure=init_p_map, config={"displayModeBar": False})
                    ], style={**CARD_STYLE, "marginBottom": "16px"}),

                    html.Div([
                        html.Div([
                            create_icon_badge("bi bi-bar-chart-steps", color=PRIMARY, bg="#EFF6FF", size=15, box_size=30),
                            html.H6("RÉPARTITION DES PAYS SOURCES & PARTS DE MARCHÉ (Q3)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px", "marginLeft": "8px"}),
                        ], className="d-flex align-items-center mb-2"),
                        dcc.Graph(id="studio-product-suppliers-bar", figure=init_p_supp, config={"displayModeBar": False})
                    ], style=CARD_STYLE),
                ], md=7, sm=12),

                # Right Column: Vulnerability & Historical Shifts (Q2 & Q3)
                dbc.Col([
                    html.Div(init_p_kpi, id="studio-product-kpi-container"),

                    html.Div([
                        html.Div([
                            create_icon_badge("bi bi-clock-history", color="#059669", bg="#D1FAE5", size=15, box_size=30),
                            html.H6("ÉVOLUTION HISTORIQUE DE CE BIEN (2000–2024) (Q2)", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13px", "marginLeft": "8px"}),
                        ], className="d-flex align-items-center mb-2"),
                        dcc.Graph(id="studio-product-history-chart", figure=init_p_hist, config={"displayModeBar": False})
                    ], style=CARD_STYLE),
                ], md=5, sm=12)
            ])
        ])


@callback(
    Output("studio-world-map", "figure"),
    Output("studio-top-partners-bar", "figure"),
    Output("studio-partner-history-chart", "figure"),
    Input("studio-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    Input("studio-scope-radio", "value"),
    Input("studio-selected-partner", "data")
)
def update_studio_partner_left(flow, year, scope, selected_partner):
    partners_df = load_partner_rankings()
    selected_partner = selected_partner or "DE"
    year = int(year or 2024)

    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].copy()
    if sub.empty:
        avail_years = partners_df["year"].unique()
        if len(avail_years) > 0:
            sub = partners_df[(partners_df["year"] == max(avail_years)) & (partners_df["flow"] == flow)].copy()

    # Apply Scope
    if scope == "EU27":
        sub = sub[sub["partner_code"].isin(list(ISO2_NAMES.keys()))].copy()
    elif scope == "EXTRA_EU":
        sub = sub[~sub["partner_code"].isin(["BE", "DE", "FR", "NL", "IT", "ES", "PL", "AT", "SE", "DK", "IE", "PT", "CZ", "HU", "RO", "BG", "HR", "SK", "SI", "LT", "LV", "EE", "CY", "MT", "GR", "FI"])].copy()

    # 1. Map Figure
    sub_map = add_iso3_column(sub)
    sub_valid = sub_map.dropna(subset=["iso3"]).copy()

    sub_valid["color_val"] = np.log10(np.maximum(10000.0, sub_valid["value_eur"]))
    cmin = 6.0
    cmax = max(7.0, sub_valid["color_val"].max())

    colorscale = [
        [0.0, "#EDE9FE"], [0.2, "#DDD6FE"], [0.4, "#A78BFA"],
        [0.65, "#6366F1"], [0.85, "#4338CA"], [1.0, "#1E1B4B"]
    ] if flow == "IMPORT" else [
        [0.0, "#E0F2FE"], [0.2, "#BAE6FD"], [0.4, "#38BDF8"],
        [0.65, "#0284C7"], [0.85, "#0066B2"], [1.0, "#001A38"]
    ]

    fig_map = go.Figure()

    # Base choropleth trace
    fig_map.add_trace(go.Choropleth(
        locations=sub_valid["iso3"],
        z=sub_valid["color_val"],
        text=sub_valid["partner_name"],
        customdata=np.stack([sub_valid["partner_code"], sub_valid["value_eur"], sub_valid["market_share_pct"]], axis=-1),
        hovertemplate="<b>%{text} (%{customdata[0]})</b><br>Volume : €%{customdata[1]:,.0f}<br>Part : %{customdata[2]:.2f}%<extra></extra>",
        colorscale=colorscale,
        zmin=cmin, zmax=cmax,
        colorbar=dict(
            title="Volume",
            tickvals=[6, 7, 8, 9, 10],
            ticktext=["1 M€", "10 M€", "100 M€", "1 Mrd€", "10 Mrd€"],
            len=0.7, thickness=12, x=0.98, y=0.5
        )
    ))

    # Luxembourg Hub Pinpoint
    fig_map.add_trace(go.Scattergeo(
        lon=[6.13], lat=[49.61],
        mode="markers+text",
        marker=dict(size=14, color=STATEC_YELLOW, symbol="star", line=dict(color=STATEC_NAVY, width=2)),
        text=["★ Luxembourg"],
        textposition="top center",
        textfont=dict(size=11, family="Montserrat", color=STATEC_NAVY),
        hoverinfo="text",
        name="Luxembourg (Hub)"
    ))

    # Selected Partner Golden Ring Highlight
    sel_iso3 = ISO2_TO_ISO3.get(selected_partner)
    if sel_iso3:
        fig_map.add_trace(go.Choropleth(
            locations=[sel_iso3],
            z=[cmax],
            colorscale=[[0.0, STATEC_YELLOW], [1.0, STATEC_YELLOW]],
            showscale=False,
            hoverinfo="skip",
            marker_line_color=STATEC_YELLOW,
            marker_line_width=3.5,
        ))

    apply_map_theme(fig_map, scope="world" if scope != "EU27" else "europe")
    fig_map.update_layout(
        title=dict(text=f"Planisphère des Partenaires ({year})", font=dict(family="Montserrat", size=13, color=STATEC_NAVY)),
        height=430,
        margin=dict(l=10, r=10, t=35, b=10)
    )

    # 2. Top 10 Partners Bar Chart
    top10 = sub.sort_values("value_eur", ascending=True).tail(10).copy()
    bar_colors = [STATEC_YELLOW if r["partner_code"] == selected_partner else (PRIMARY if flow == "EXPORT" else SECONDARY) for _, r in top10.iterrows()]

    fig_bar = go.Figure(go.Bar(
        x=top10["value_eur"] / 1e6,
        y=[f"{r['partner_name']} ({r['partner_code']})" for _, r in top10.iterrows()],
        orientation="h",
        marker_color=bar_colors,
        customdata=top10["partner_code"],
        text=[f"€{v/1e6:.1f}M ({s:.1f}%)" for v, s in zip(top10["value_eur"], top10["market_share_pct"])],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Volume : €%{x:.1f}M<extra></extra>"
    ))
    apply_plot_theme(fig_bar, title=f"Top 10 Partenaires en {year} (€M)", x_title="Millions d'Euros (€M)")
    fig_bar.update_layout(height=320, margin=dict(l=10, r=60, t=35, b=30), yaxis=dict(autorange="reversed"))

    # 3. Bilateral Historical Trade Trend (2000-2024)
    hist_sub = partners_df[(partners_df["partner_code"] == selected_partner) & (partners_df["flow"] == flow)].sort_values("year")
    fig_hist = go.Figure()
    if not hist_sub.empty:
        fig_hist.add_trace(go.Scatter(
            x=hist_sub["year"],
            y=hist_sub["value_eur"] / 1e6,
            mode="lines+markers",
            line=dict(color=PRIMARY if flow == "EXPORT" else SECONDARY, width=3),
            marker=dict(size=6, color=STATEC_YELLOW, line=dict(color=STATEC_NAVY, width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(0, 102, 178, 0.08)" if flow == "EXPORT" else "rgba(67, 56, 202, 0.08)",
            hovertemplate="Année %{x}<br>Volume : €%{y:,.1f}M<extra></extra>"
        ))
    partner_name = get_country_name(selected_partner)
    apply_plot_theme(fig_hist, title=f"Évolution des Échanges avec {partner_name} (2000–2024)", x_title="Année", y_title="M€")
    fig_hist.update_layout(height=260, margin=dict(l=10, r=20, t=35, b=30))

    return fig_map, fig_bar, fig_hist


@callback(
    Output("studio-partner-spotlight-container", "children"),
    Output("studio-partner-treemap", "figure"),
    Output("studio-partner-products-bar", "figure"),
    Input("studio-selected-partner", "data"),
    Input("studio-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    Input("studio-granularity-radio", "value")
)
def update_studio_partner_right(selected_partner, flow, year, granularity):
    selected_partner = selected_partner or "DE"
    granularity = int(granularity or 2)
    partner_name = get_country_name(selected_partner)
    year = int(year or 2024)

    # 1. Partner Metrics
    partners_df = load_partner_rankings()
    sub_p = partners_df[(partners_df["partner_code"] == selected_partner) &
                        (partners_df["flow"] == flow) &
                        (partners_df["year"] == year)]
    if sub_p.empty:
        sub_p = partners_df[(partners_df["partner_code"] == selected_partner) & (partners_df["flow"] == flow)]
        if not sub_p.empty:
            sub_p = sub_p[sub_p["year"] == sub_p["year"].max()]

    val_eur = sub_p["value_eur"].values[0] if not sub_p.empty else 0.0
    share_pct = sub_p["market_share_pct"].values[0] if not sub_p.empty else 0.0
    rank = int(sub_p["rank"].values[0]) if not sub_p.empty and "rank" in sub_p.columns else 1

    # 2. Extract Partner Products
    prod_sub, is_fallback, level_label = get_partner_products(selected_partner, flow, year, level=granularity)

    # Spotlight Header
    badge_color = SUCCESS if rank <= 3 else (PRIMARY if rank <= 10 else STATEC_GRAY)
    flow_text = "Fournisseur" if flow == "IMPORT" else "Client"

    spotlight = html.Div([
        html.Div([
            html.Div([
                create_icon_badge("bi bi-flag-fill", color="#B45309", bg="#FEF3C7", size=18, box_size=38),
                html.Div([
                    html.Div([
                        html.Span(f"{partner_name.upper()} ({selected_partner})", style={
                            "fontSize": "16px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY
                        }),
                        html.Span(f"#{rank} {flow_text}", className="badge ms-2", style={"backgroundColor": badge_color, "color": "#FFFFFF", "fontSize": "11px", "fontWeight": "700"}),
                    ]),
                    html.Span(f"Volume d'échange : {fmt_eur(val_eur)} • {share_pct:.1f}% des {flow.lower()}s du Luxembourg", style={
                        "fontSize": "12px", "color": TEXT_MUTED, "fontWeight": "600"
                    })
                ], className="ms-2")
            ], className="d-flex align-items-center"),

            # Depth Indicator
            html.Div([
                html.Span(level_label, className="badge", style={
                    "backgroundColor": "#EFF6FF", "color": PRIMARY, "border": "1px solid #BFDBFE", "fontSize": "10.5px", "fontWeight": "700"
                })
            ])
        ], className="d-flex align-items-center justify-content-between"),

        # Fallback Alert if applicable
        html.Div([
            html.I(className="bi bi-info-circle-fill me-1 text-warning"),
            html.Span("Drill-down CN8 à 8 chiffres disponible pour le Top 5 partenaires (DE, BE, FR, NL, US). Pour les autres partenaires mondiaux, affichage universel au niveau HS2 (Chapitres).", style={"fontSize": "11px", "color": "#92400E"})
        ], className="mt-2 p-2 rounded", style={"backgroundColor": "#FFFBEB", "border": "1px solid #FCD34D"}) if is_fallback else html.Div()
    ], style={
        "backgroundColor": "#FFFFFF", "borderRadius": "10px", "padding": "14px 16px",
        "boxShadow": "0 2px 6px rgba(0,0,0,0.04)", "border": f"1px solid {BORDER}",
        "borderLeft": f"4px solid {STATEC_YELLOW}", "marginBottom": "16px"
    })

    # 3. Treemap Figure
    if prod_sub.empty:
        fig_treemap = go.Figure()
        fig_treemap.add_annotation(text="Aucun détail produit disponible pour ce pays", showarrow=False)
        apply_plot_theme(fig_treemap)
        fig_treemap.update_layout(height=360)

        fig_prod_bar = go.Figure()
        apply_plot_theme(fig_prod_bar)
        fig_prod_bar.update_layout(height=300)
    else:
        top_prods = prod_sub.head(25).copy()
        fig_treemap = px.treemap(
            top_prods,
            path=["short_name"],
            values="value_eur",
            color="value_eur",
            color_continuous_scale="Viridis" if flow == "IMPORT" else "Blues"
        )
        fig_treemap.update_traces(
            hovertemplate="<b>%{label}</b><br>Valeur : €%{value:,.0f}<extra></extra>",
            textinfo="label+value"
        )
        apply_plot_theme(fig_treemap, title=f"Panier de Biens — {partner_name} ({len(top_prods)} flux)")
        fig_treemap.update_layout(height=370, margin=dict(l=10, r=10, t=35, b=10), coloraxis_showscale=False)

        # 4. Top Products Horizontal Bar Chart
        bar_sub = prod_sub.head(10).sort_values("value_eur", ascending=True)
        fig_prod_bar = go.Figure(go.Bar(
            x=bar_sub["value_eur"] / 1e6,
            y=bar_sub["short_name"],
            orientation="h",
            marker_color=PRIMARY if flow == "EXPORT" else SECONDARY,
            text=[fmt_eur(v) for v in bar_sub["value_eur"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Valeur : €%{x:.2f}M<extra></extra>"
        ))
        apply_plot_theme(fig_prod_bar, title=f"Top Marchandises avec {partner_name} ({level_label.split(' ')[0]})", x_title="Millions d'Euros (€M)")
        fig_prod_bar.update_layout(height=320, margin=dict(l=10, r=50, t=35, b=25), yaxis=dict(autorange="reversed"))

    return spotlight, fig_treemap, fig_prod_bar


@callback(
    Output("studio-product-map", "figure"),
    Output("studio-product-suppliers-bar", "figure"),
    Output("studio-product-kpi-container", "children"),
    Output("studio-product-history-chart", "figure"),
    Input("studio-product-dropdown", "value"),
    Input("studio-flow-radio", "value"),
    Input("global-year-dropdown", "value"),
    Input("studio-scope-radio", "value")
)
def update_studio_product_perspective(product_code, flow, year, scope):
    product_code = str(product_code or "87")
    partners_df = load_product_partners()
    year = int(year or 2024)

    valid_years = sorted(partners_df["year"].unique())
    target_year = year if year in valid_years else max(valid_years)

    sub = partners_df[(partners_df["hs2_code"] == product_code) &
                      (partners_df["flow"] == flow) &
                      (partners_df["year"] == target_year)].copy()

    if sub.empty:
        sub = partners_df[(partners_df["hs2_code"] == product_code) & (partners_df["flow"] == flow)].copy()
        if not sub.empty:
            target_year = sub["year"].max()
            sub = sub[sub["year"] == target_year]

    prod_name = sub["hs2_name"].iloc[0] if not sub.empty else f"Produit {product_code}"
    hhi_val = sub["hhi"].iloc[0] if not sub.empty and "hhi" in sub.columns else 1200.0
    tot_eur = sub["total_eur"].iloc[0] if not sub.empty and "total_eur" in sub.columns else sub["value_eur"].sum()

    # 1. Product Map
    sub_map = add_iso3_column(sub)
    sub_valid = sub_map.dropna(subset=["iso3"]).copy()

    fig_map = go.Figure()
    if not sub_valid.empty:
        sub_valid["color_val"] = np.log10(np.maximum(1000.0, sub_valid["value_eur"]))
        cmin = 4.0
        cmax = max(5.0, sub_valid["color_val"].max())

        fig_map.add_trace(go.Choropleth(
            locations=sub_valid["iso3"],
            z=sub_valid["color_val"],
            text=sub_valid["partner_name"],
            customdata=np.stack([sub_valid["partner_code"], sub_valid["value_eur"], sub_valid["partner_share_pct"]], axis=-1),
            hovertemplate="<b>%{text} (%{customdata[0]})</b><br>Fourniture : €%{customdata[1]:,.0f}<br>Part : %{customdata[2]:.1f}%<extra></extra>",
            colorscale=[[0.0, "#ECFDF5"], [0.3, "#A7F3D0"], [0.6, "#10B981"], [0.85, "#047857"], [1.0, "#064E3B"]],
            zmin=cmin, zmax=cmax,
            colorbar=dict(title="Volume", len=0.7, thickness=12, x=0.98, y=0.5)
        ))

    # Luxembourg Hub
    fig_map.add_trace(go.Scattergeo(
        lon=[6.13], lat=[49.61],
        mode="markers+text",
        marker=dict(size=13, color=STATEC_YELLOW, symbol="star", line=dict(color=STATEC_NAVY, width=2)),
        text=["★ Luxembourg"],
        textposition="top center",
        name="Luxembourg (Hub)"
    ))

    apply_map_theme(fig_map, scope="world" if scope != "EU27" else "europe")
    fig_map.update_layout(
        title=dict(text=f"Fournisseurs / Clients — Ch. {product_code} ({target_year})", font=dict(family="Montserrat", size=13, color=STATEC_NAVY)),
        height=410,
        margin=dict(l=10, r=10, t=35, b=10)
    )

    # 2. Top Suppliers Bar Chart
    top10_supp = sub.sort_values("value_eur", ascending=True).tail(10).copy()
    fig_supp = go.Figure(go.Bar(
        x=top10_supp["value_eur"] / 1e6,
        y=[f"{r['partner_name']} ({r['partner_code']})" for _, r in top10_supp.iterrows()],
        orientation="h",
        marker_color="#059669" if flow == "IMPORT" else PRIMARY,
        text=[f"€{v/1e6:.1f}M ({s:.1f}%)" for v, s in zip(top10_supp["value_eur"], top10_supp["partner_share_pct"])],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Valeur : €%{x:.2f}M<extra></extra>"
    ))
    apply_plot_theme(fig_supp, title=f"Origine des Flux pour Ch. {product_code} en {target_year}", x_title="Millions d'Euros (€M)")
    fig_supp.update_layout(height=320, margin=dict(l=10, r=60, t=35, b=25), yaxis=dict(autorange="reversed"))

    # 3. Product KPI & Vulnerability Card
    hhi_badge = get_concentration_badge(hhi_val)
    top3_share = top10_supp.tail(3)["partner_share_pct"].sum() if not top10_supp.empty else 0.0

    kpi_card = html.Div([
        html.Div([
            html.Div([
                create_icon_badge("bi bi-shield-check" if hhi_val < 1500 else ("bi bi-shield-exclamation" if hhi_val < 2500 else "bi bi-exclamation-triangle-fill"),
                                  color=SUCCESS if hhi_val < 1500 else (WARNING if hhi_val < 2500 else DANGER),
                                  bg="#DCFCE7" if hhi_val < 1500 else ("#FEF3C7" if hhi_val < 2500 else "#FEE2E2"),
                                  size=18, box_size=38),
                html.Div([
                    html.H6(f"CH. {product_code} — {prod_name[:40]}", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "marginBottom": "0", "fontSize": "13.5px"}),
                    html.Span(f"Total annuel : {fmt_eur(tot_eur)} • Top-3 pays concentrent {top3_share:.1f}% des flux", style={"fontSize": "11.5px", "color": TEXT_MUTED})
                ], className="ms-2")
            ], className="d-flex align-items-center"),
            html.Div(hhi_badge)
        ], className="d-flex align-items-center justify-content-between mb-2"),

        html.Div([
            html.Small([
                html.Strong("Diagnostic de Résilience : "),
                f"Ce produit présente un niveau de concentration {'faible et bien diversifié' if hhi_val < 1500 else ('modéré nécessitant une veille' if hhi_val < 2500 else 'critique avec dépendance aiguë à un oligopole de fournisseurs')}."
            ], style={"fontSize": "11px", "color": TEXT_MUTED})
        ], className="p-2 rounded", style={"backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}"})
    ], style={**CARD_STYLE, "marginBottom": "16px"})

    # 4. Long-Term Historical Trajectory (2000-2024)
    all_rankings = load_product_rankings()
    prod_hist = all_rankings[(all_rankings["hs2_code"] == product_code) & (all_rankings["flow"] == flow)].sort_values("year")
    fig_hist = go.Figure()
    if not prod_hist.empty:
        fig_hist.add_trace(go.Scatter(
            x=prod_hist["year"],
            y=prod_hist["value_eur"] / 1e6,
            mode="lines+markers",
            line=dict(color="#059669" if flow == "IMPORT" else PRIMARY, width=3),
            marker=dict(size=5, color=STATEC_YELLOW),
            fill="tozeroy",
            fillcolor="rgba(5, 150, 105, 0.08)" if flow == "IMPORT" else "rgba(0, 102, 178, 0.08)",
            hovertemplate="Année %{x}<br>Volume : €%{y:,.1f}M<extra></extra>"
        ))
    apply_plot_theme(fig_hist, title=f"Évolution 2000–2024 de Ch. {product_code} (€M)", x_title="Année", y_title="M€")
    fig_hist.update_layout(height=280, margin=dict(l=10, r=20, t=35, b=30))

    return fig_map, fig_supp, kpi_card, fig_hist


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
        create_section_header(
            f"BENCHMARKS COMPARATIFS RÉGIONAUX ({selected_year})",
            "Positionnement du commerce extérieur de marchandises du Luxembourg par rapport aux pays pairs (France, Allemagne, Belgique, Pays-Bas).",
            badge_text="Eurostat Q5",
            badge_color=STATEC_NAVY,
            info_title="Méthodologie Comparative : Base 100 & Taux de Couverture",
            info_content="1. L'indice d'expansion (Base 100 = 2000) compare la trajectoire relative des échanges indépendamment de la taille des pays. Le Luxembourg (+89%) évolue au même rythme que la France (+84%), alors que les hubs portuaires mondiaux (NL, BE) surperforment. 2. Le taux de couverture physique (~62%) reflète la vocation tertiaire du Grand-Duché : la balance des biens est gagée par l'excédent massif des services financiers.",
            info_icon="bi bi-bar-chart-line-fill",
            info_variant="navy"
        ),
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
            html.H6("ENSEIGNEMENTS COMPARATIFS : LUXEMBOURG VS PEERS EUROPÉENS", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
            html.Ul([
                html.Li("Dynamisme des flux : Le volume des biens échangés par le Luxembourg a progressé de +89% depuis 2000, un rythme comparable à celui de la France (+84%), tandis que les hubs de réexportation portuaire (Pays-Bas +236%, Belgique +168%) enregistrent une démultiplication due aux terminaux de Rotterdam et d'Anvers."),
                html.Li("Asymétrie du taux de couverture : Alors que l'Allemagne (116%) et les Pays-Bas (111%) affichent d'importants excédents de biens, le Luxembourg présente un taux de couverture d'environ 65%, les importations de marchandises étant structurellement financées par l'immense surplus des services financiers et de fonds (+25 Mrd €)."),
            ], style={"fontSize": "13px", "color": TEXT_MUTED, "marginBottom": "0"})
        ], style={**CARD_STYLE, "backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}", "borderLeft": f"4px solid {STATEC_YELLOW}"})
    ])


# ───────────────────────────────────────────────────────────────────────────
# TAB 6: SEASONALITY & TREND LAB (Q6)
# ───────────────────────────────────────────────────────────────────────────
def render_tab_seasonality():
    return html.Div([
        create_section_header(
            "LABORATOIRE DE DÉCOMPOSITION SAISONNIÈRE (2000–2026)",
            "Décomposition économétrique par moyenne mobile centrée 12 mois : tendance de fond, coefficients mensuels saisonniers et flux désaisonnalisés.",
            badge_text="Économétrie Q6",
            badge_color=STATEC_NAVY,
            info_title="Décomposition Économétrique (Moyenne Mobile Centrée)",
            info_content="1. Tendance de fond : filtre les fluctuations passagères pour isoler la trajectoire macroéconomique réelle. 2. Facteur Saisonnier Mensuel : mesure l'écart systématique au fil de l'année (1,0 = neutre). Un facteur de 0,856 en août indique une baisse prévisible de -14,4% par rapport à la moyenne annuelle, provoquée par le congé collectif de la construction et les arrêts d'usines en Europe.",
            info_icon="bi bi-graph-up-arrow",
            info_variant="primary"
        ),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("SÉRIES MENSUELLES & TENDANCE DE FOND", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                    html.P("Comparaison directe des données brutes constatées et des séries corrigées des variations saisonnières.", className="text-muted", style={"fontSize": "12px"}),

                    dbc.Row([
                        dbc.Col([
                            html.Label("SECTEUR / PRODUIT :", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "fontSize": "11px", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
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
                            html.Label("FLUX COMMERCIAL :", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "fontSize": "11px", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                            dbc.RadioItems(
                                id="season-flow-radio",
                                options=[
                                    {"label": "Exportations", "value": "EXPORT"},
                                    {"label": "Importations", "value": "IMPORT"},
                                ],
                                value="EXPORT",
                                inline=True,
                                style={"fontSize": "12.5px", "marginTop": "6px"}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("SÉRIES VISIBLES :", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "fontSize": "11px", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                            dbc.Checklist(
                                id="season-series-check",
                                options=[
                                    {"label": "Brut", "value": "raw"},
                                    {"label": "Tendance (12M)", "value": "trend"},
                                    {"label": "Désaisonnalisé (CVS)", "value": "adjusted"},
                                ],
                                value=["raw", "trend", "adjusted"],
                                inline=True,
                                style={"fontSize": "12.5px", "marginTop": "6px"}
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
                    html.H6(id="season-factor-title", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                    html.P("Indices saisonniers empiriques (1,0 = niveau neutre). Remarquez la chute sévère et systématique en août (-14,4%) causée par les congés industriels et le congé collectif de la construction.", className="text-muted", style={"fontSize": "12px"}),
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
                    create_icon_badge("bi bi-lightning-charge-fill", color="#DC2626", bg="#FEE2E2", size=15, box_size=30),
                    html.Strong("VULNÉRABILITÉ ÉNERGIE", style={"fontSize": "11.5px", "fontFamily": "'Montserrat', sans-serif", "color": "#991B1B", "marginLeft": "8px"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Dépendance extrême (HHI > 3 800) : plus de 50% des carburants et gaz transitent par les réseaux de pipelines et raffineries belges et néerlandais.", style={"fontSize": "11px", "color": "#7F1D1D", "marginBottom": "0"})
            ], style={"backgroundColor": "#FEF2F2", "border": "1px solid #FCA5A5", "borderRadius": "8px", "padding": "12px 14px", "height": "100%", "borderLeft": "4px solid #EA152C"})
        ], md=3, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Div([
                    create_icon_badge("bi bi-water", color="#D97706", bg="#FEF3C7", size=15, box_size=30),
                    html.Strong("DÉPENDANCE TRANSIT PORTUAIRE", style={"fontSize": "11.5px", "fontFamily": "'Montserrat', sans-serif", "color": "#92400E", "marginLeft": "8px"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Goulot Anvers-Rotterdam : ~33% des biens physiques transitent par les terminaux de la mer du Nord avant d'atteindre le territoire national.", style={"fontSize": "11px", "color": "#78350F", "marginBottom": "0"})
            ], style={"backgroundColor": "#FFFBEB", "border": "1px solid #FCD34D", "borderRadius": "8px", "padding": "12px 14px", "height": "100%", "borderLeft": f"4px solid {STATEC_YELLOW}"})
        ], md=3, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Div([
                    create_icon_badge("bi bi-shield-fill-check", color="#059669", bg="#D1FAE5", size=15, box_size=30),
                    html.Strong("BOUCLIER DES SERVICES", style={"fontSize": "11.5px", "fontFamily": "'Montserrat', sans-serif", "color": "#065F46", "marginLeft": "8px"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Déficit des biens financé : Le solde négatif des marchandises (-9,12 Mrd €) est compensé par l'excédent massif des services financiers (+25 Mrd €).", style={"fontSize": "11px", "color": "#064E3B", "marginBottom": "0"})
            ], style={"backgroundColor": "#ECFDF5", "border": "1px solid #6EE7B7", "borderRadius": "8px", "padding": "12px 14px", "height": "100%", "borderLeft": "4px solid #059669"})
        ], md=3, sm=6, className="mb-2"),

        dbc.Col([
            html.Div([
                html.Div([
                    create_icon_badge("bi bi-calendar3-range", color=PRIMARY, bg="#DBEAFE", size=15, box_size=30),
                    html.Strong("CHOC SAISONNIER D'AOÛT", style={"fontSize": "11.5px", "fontFamily": "'Montserrat', sans-serif", "color": "#1E40AF", "marginLeft": "8px"})
                ], className="d-flex align-items-center mb-1"),
                html.P("Contraction prévisible (-14,4%) chaque mois d'août liée au congé collectif du BTP et aux congés d'usines en Europe : anticiper les stocks en juin/juillet.", style={"fontSize": "11px", "color": "#1E3A8A", "marginBottom": "0"})
            ], style={"backgroundColor": "#EFF6FF", "border": "1px solid #93C5FD", "borderRadius": "8px", "padding": "12px 14px", "height": "100%", "borderLeft": f"4px solid {PRIMARY}"})
        ], md=3, sm=6, className="mb-2"),
    ], className="mb-3")

    return html.Div([
        create_section_header(
            f"RADAR DE RÉSILIENCE SOUVERAINE & APPROVISIONNEMENT CRITIQUE ({use_year})",
            "Évaluation de l'autonomie stratégique et des vulnérabilités d'approvisionnement par panier de biens vitaux (Énergie, Alimentation, Santé, Métaux, Technologies). Détection des fournisseurs uniques et des goulots de transit portuaires.",
            badge_text="Priorité Décideurs",
            badge_color=STATEC_NAVY,
            info_title="Indice HHI de Concentration & Seuils de Vulnérabilité",
            info_content=[
                html.Span("L'indice d'Herfindahl-Hirschman (HHI) mesure la dépendance d'approvisionnement (somme des carrés des parts des pays fournisseurs) : "),
                html.Div([
                    html.Span("HHI < 1 500 : Marché diversifié", className="badge bg-success text-white me-2", style={"fontWeight": "700"}),
                    html.Span("1 500 – 2 500 : Concentration modérée", className="badge bg-warning text-dark me-2", style={"fontWeight": "700"}),
                    html.Span("HHI > 2 500 : Dépendance critique / Risque de rupture", className="badge bg-danger text-white", style={"fontWeight": "700"}),
                ], className="mt-2")
            ],
            info_icon="bi bi-shield-shaded",
            info_variant="gold"
        ),

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
                    html.H6("RECOMMANDATIONS STRATÉGIQUES & DISPOSITIFS DE SOUVERAINETÉ", style={"fontWeight": "800", "fontFamily": "'Montserrat', sans-serif", "color": STATEC_NAVY, "letterSpacing": "0.4px"}),
                    html.Ul([
                        html.Li("Souveraineté Énergétique : Les produits pétroliers raffinés présentent un HHI critique > 3 800 (dépendance quasi-exclusive aux raffineries et oléoducs de Belgique/Pays-Bas). Consolider les réserves bilatérales stratégiques et accélérer l'électrification."),
                        html.Li("L'Effet 'Rotterdam-Anvers' : Plus de 33% des importations physiques transitent par les terminaux maritimes belges et néerlandais. Mettre en place des corridors ferroviaires et fluviaux de délestage via les réseaux français en cas d'engorgement en mer du Nord."),
                        html.Li("Excellente diversification technologique : Les biens d'équipement, machines et technologies de pointe bénéficient d'une saine diversification entre l'Allemagne, la France, les États-Unis et le Japon (HHI ~1 500)."),
                        html.Li("Bouclier Pharmaceutique : Sécuriser un stock tampon souverain de 90 jours pour les principes actifs critiques et médicaments d'urgence avant le ralentissement de production estival d'août."),
                    ], style={"fontSize": "13px", "color": TEXT_MUTED, "marginBottom": "0"})
                ], style={**CARD_STYLE, "backgroundColor": "#F8FAFC", "border": f"1px solid {BORDER}", "borderLeft": f"4px solid {STATEC_YELLOW}"})
            ], md=12)
        ])
    ])


# ── Run Server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
