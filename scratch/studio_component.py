import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State

from src.dashboard.data_loader import (
    load_partner_rankings,
    load_product_rankings,
    load_product_partners,
    load_hs4_product_rankings,
    load_drilldown_lvl2,
    load_drilldown_lvl4,
    load_drilldown_lvl8,
)
from src.dashboard.design_system import (
    PRIMARY, SECONDARY, ACCENT, STATEC_BLUE, STATEC_NAVY, STATEC_RED,
    STATEC_YELLOW, STATEC_GRAY, STATEC_LIGHT, BG_CARD, TEXT_PRIMARY,
    TEXT_MUTED, BORDER, SUCCESS, WARNING, DANGER,
    CARD_STYLE, create_section_header, create_icon_badge,
    apply_plot_theme, apply_map_theme, fmt_eur, fmt_pct, EU27_COUNTRIES
)

# ── Helper: Map 2-letter ISO to 3-letter ISO for Plotly Choropleths ──────────
ISO2_TO_ISO3 = {
    "DE": "DEU", "FR": "FRA", "BE": "BEL", "NL": "NLD", "US": "USA",
    "IT": "ITA", "GB": "GBR", "ES": "ESP", "CN": "CHN", "CH": "CHE",
    "PL": "POL", "AT": "AUT", "SE": "SWE", "JP": "JPN", "CZ": "CZE",
    "DK": "DNK", "IE": "IRL", "PT": "PRT", "TR": "TUR", "IN": "IND",
    "BR": "BRA", "KR": "KOR", "NO": "NOR", "RU": "RUS", "CA": "CAN",
    "MX": "MEX", "AU": "AUS", "ZA": "ZAF", "HU": "HUN", "RO": "ROU",
    "SG": "SGP", "LU": "LUX", "GR": "GRC", "FI": "FIN", "SK": "SVK",
    "BG": "BGR", "HR": "HRV", "SI": "SVN", "LT": "LTU", "LV": "LVA",
    "EE": "EST", "CY": "CYP", "MT": "MLT"
}

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

def get_iso3(iso2):
    return ISO2_TO_ISO3.get(str(iso2).upper(), None)

def get_country_name(iso2):
    return ISO2_NAMES.get(str(iso2).upper(), str(iso2))

def get_studio_partner_products(partner_code, flow, year, level=2):
    """
    Retrieves products traded with partner_code at requested granularity (2, 4, or 8).
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
            return sub, False, "CN8 (Lignes tarifaires à 8 chiffres)"
            
    if level == 4 and partner_code in top_5:
        df4 = load_drilldown_lvl4()
        sub = df4[(df4["partner_code"] == partner_code) & (df4["flow"] == flow)].copy()
        if not sub.empty:
            sub = sub.sort_values("value_eur", ascending=False)
            sub["short_name"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:50] + ".." if len(str(s)) > 50 else str(s))
            return sub, False, "HS4 (Sous-positions à 4 chiffres)"

    # HS2 Fallback / Universal for all 238 countries
    partners_df = load_product_partners()
    valid_years = sorted(partners_df["year"].unique())
    target_year = year if year in valid_years else max(valid_years)
    
    sub = partners_df[(partners_df["partner_code"] == partner_code) & 
                        (partners_df["flow"] == flow) & 
                        (partners_df["year"] == target_year)].copy()
    
    if sub.empty:
        # Try any year
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
        
    return pd.DataFrame(), False, "Aucune donnée disponible"

print("Studio helper functions compiled successfully!")
