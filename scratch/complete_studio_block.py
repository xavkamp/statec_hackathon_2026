import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash

from src.dashboard.data_loader import (
    load_overview_kpis, load_partner_rankings, load_product_rankings,
    load_hs4_product_rankings, load_product_partners, load_seasonal_decomposition,
    load_country_benchmarks, load_drilldown_lvl2, load_drilldown_lvl4, load_drilldown_lvl8
)
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
    level = int(level)
    partner_code = str(partner_code).upper()
    top_5 = ["BE", "DE", "FR", "NL", "US"]

    if level == 8 and partner_code in top_5:
        df8 = load_drilldown_lvl8()
        sub = df8[(df8["partner_code"] == partner_code) & (df8["flow"] == flow)].copy()
        if not sub.empty:
            sub = sub.sort_values("value_eur", ascending=False)
            sub["short_name"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:48] + ".." if len(str(s)) > 48 else str(s))
            return sub, False, "CN8 (Nomenclature Combinée à 8 chiffres)"

    if level == 4 and partner_code in top_5:
        df4 = load_drilldown_lvl4()
        sub = df4[(df4["partner_code"] == partner_code) & (df4["flow"] == flow)].copy()
        if not sub.empty:
            sub = sub.sort_values("value_eur", ascending=False)
            sub["short_name"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:48] + ".." if len(str(s)) > 48 else str(s))
            return sub, False, "HS4 (Sous-positions à 4 chiffres)"

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
        sub["short_name"] = "Ch." + sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:48] + ".." if len(str(s)) > 48 else str(s))
        is_fallback = (level in [4, 8] and partner_code not in top_5)
        return sub, is_fallback, "HS2 (Chapitres à 2 chiffres)"

    return pd.DataFrame(), False, "Données non disponibles"

print("Compiling test studio structure...")
