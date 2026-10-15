import sys
from pathlib import Path

STUDIO_REPLACEMENT = '''# ───────────────────────────────────────────────────────────────────────────
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
'''

def main():
    app_path = Path("src/dashboard/app.py")
    lines = app_path.read_text(encoding="utf-8").splitlines(keepends=True)
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if "TAB 1 (ANALYST): STUDIO GÉO-TARIFAIRE & DRILL-DOWN BILATÉRAL" in line:
            start_idx = i - 1
        if "TAB 5: PEER BENCHMARKS (Q5)" in line:
            end_idx = i - 1
            break
            
    print(f"Start index: {start_idx} (line {start_idx+1})")
    print(f"End index: {end_idx} (line {end_idx+1})")
    
    new_lines = lines[:start_idx] + [STUDIO_REPLACEMENT + "\n\n"] + lines[end_idx:]
    app_path.write_text("".join(new_lines), encoding="utf-8")
    print("Successfully updated src/dashboard/app.py!")

if __name__ == "__main__":
    main()
