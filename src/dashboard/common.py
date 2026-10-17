# -*- coding: utf-8 -*-
"""Shared helpers for the dashboard tabs.

Everything that used to be copy-pasted across the tab renderers/callbacks lives here:
country names, basket filtering, year resolution and the horizontal-bar builder.
"""

from typing import Iterable, List, Optional

import pandas as pd
import plotly.graph_objects as go

from src.config import (  # noqa: F401  (re-exported for the dashboard modules)
    END_YEAR, RESILIENCE_BASKETS, EU27_CODES, NEIGHBOUR_CODES, TRANSIT_HUB_CODES,
)
from src.dashboard.design_system import apply_plot_theme, fmt_eur

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


# ── Baskets ────────────────────────────────────────────────────────────────
BASKET_FILTER_OPTIONS = [
    {"label": basket["filter_label"], "value": key} for key, basket in RESILIENCE_BASKETS.items()
]


def basket_chapters(basket: Optional[str]) -> List[str]:
    """HS2 chapters of a basket; empty list means "no filtering" (ALL / unknown)."""
    if not basket or basket == "ALL":
        return []
    return list(RESILIENCE_BASKETS.get(basket, {}).get("chapters", []))


def basket_short_name(basket: Optional[str]) -> str:
    return RESILIENCE_BASKETS.get(basket, {}).get("short_name", basket or "")


def filter_by_chapters(df: pd.DataFrame, code_col: str, chapters: Iterable[str]) -> pd.DataFrame:
    """Keep rows whose product code belongs (first two digits) to one of the chapters."""
    chapters = list(chapters)
    if not chapters or df.empty:
        return df
    return df[df[code_col].astype(str).str[:2].isin(chapters)]


# ── Year handling ──────────────────────────────────────────────────────────
def resolve_year(data, year, column: str = "year") -> int:
    """Return the year to display for a requested ``year``.

    Exact match whenever the dataset covers the year (always the case once the
    ingestion has covered the full span); otherwise the *nearest* available year.
    Callers must use the returned value in titles, so a label never claims a year the
    figure does not show.
    """
    series = data[column] if isinstance(data, pd.DataFrame) else pd.Series(list(data))
    years = sorted({int(y) for y in series.dropna().unique()})
    if not years:
        return int(year) if year else END_YEAR
    if year is None:
        return years[-1]
    year = int(year)
    if year in years:
        return year
    return min(years, key=lambda y: (abs(y - year), -y))


# ── Figures ────────────────────────────────────────────────────────────────
def truncate(text, limit: int) -> str:
    text = str(text)
    return text[:limit] + ".." if len(text) > limit else text


def horizontal_bar(
    x_values,
    labels,
    colors,
    text,
    hover,
    x_title: str,
    margin: dict,
    customdata=None,
    x_range_pad: float = 1.25,
) -> go.Figure:
    """Themed horizontal bar chart used by the ranking figures (2.1, 2.4, 3.1, 3.4)."""
    fig = go.Figure(go.Bar(
        x=x_values,
        y=labels,
        orientation="h",
        marker_color=colors,
        customdata=customdata,
        text=text,
        textposition="outside",
        hovertemplate=hover,
    ))
    apply_plot_theme(fig, x_title=x_title)
    x_max = float(pd.Series(x_values).max()) if len(x_values) else 100.0
    fig.update_xaxes(range=[0, x_max * x_range_pad])
    fig.update_layout(margin=margin, yaxis=dict(autorange="reversed"))
    return fig


def value_labels(values) -> List[str]:
    return [fmt_eur(v) for v in values]
