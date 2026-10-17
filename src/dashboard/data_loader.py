"""Data loader module for the dashboard.
Loads processed CSV datasets directly using pandas.read_csv with smart mtime cache invalidation.
"""

from pathlib import Path
from typing import Callable, Optional
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import PROCESSED_DIR, START_YEAR, END_YEAR
from src.processing.process_data import build_hs2_drilldown

_CACHE = {}
_MTIME = {}

# Code-like columns must be read as text, otherwise leading zeros are lost ("0207" -> 207).
_CODE_DTYPES = {
    "partner_code": str, "reporter_code": str, "product_code": str,
    "hs2_code": str, "hs4_code": str, "hs8_code": str,
    "hs2_parent": str, "hs4_parent": str,
}
# Zero-padded width of the hierarchical code columns.
_CODE_WIDTHS = {"hs2_code": 2, "hs4_code": 4, "hs8_code": 8, "hs2_parent": 2, "hs4_parent": 4}


def _normalize_codes(df: pd.DataFrame) -> pd.DataFrame:
    for col, width in _CODE_WIDTHS.items():
        if col in df.columns:
            df[col] = df[col].astype(str).str.zfill(width)
    if "product_code" in df.columns:
        df["product_code"] = df["product_code"].astype(str)
    return df


def _bound_years(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict a table to the configured analysis span."""
    if df.empty or "year" not in df.columns:
        return df
    return df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)]


def _load_csv_cached(filename: str, bound_years: bool = True) -> pd.DataFrame:
    """Load CSV with automatic cache invalidation when file mtime changes.

    The returned frame is already restricted to START_YEAR..END_YEAR (if it has a
    ``year`` column), so callers never need to re-apply the span.
    """
    path = PROCESSED_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        mtime = path.stat().st_mtime
        if filename in _CACHE and _MTIME.get(filename) == mtime and not _CACHE[filename].empty:
            return _CACHE[filename]
        df = pd.read_csv(path, dtype=_CODE_DTYPES, keep_default_na=False, na_values=[""])
        if not df.empty:
            df = _normalize_codes(df)
            if bound_years:
                df = _bound_years(df)
            _CACHE[filename] = df
            _MTIME[filename] = mtime
        return df
    except Exception:
        if filename in _CACHE:
            return _CACHE[filename]
        return pd.DataFrame()


def _derived_cached(name: str, source: str, builder: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
    """Cache a table derived in memory from another processed file (rebuilt when it changes)."""
    src_df = _load_csv_cached(source)
    if src_df.empty:
        return pd.DataFrame()
    stamp = _MTIME.get(source)
    if name in _CACHE and _MTIME.get(name) == stamp:
        return _CACHE[name]
    _CACHE[name] = builder(src_df)
    _MTIME[name] = stamp
    return _CACHE[name]


def load_overview_kpis() -> pd.DataFrame:
    return _load_csv_cached("overview_kpis.csv")


def load_partner_rankings() -> pd.DataFrame:
    return _load_csv_cached("partner_rankings.csv")


def load_product_rankings() -> pd.DataFrame:
    return _load_csv_cached("product_rankings.csv")


def load_hs4_product_rankings() -> pd.DataFrame:
    return _load_csv_cached("hs4_product_rankings.csv")


def load_hs8_product_rankings() -> pd.DataFrame:
    return _load_csv_cached("hs8_product_rankings.csv")


def load_product_partners() -> pd.DataFrame:
    return _load_csv_cached("product_partners.csv")


def load_seasonal_decomposition() -> pd.DataFrame:
    return _load_csv_cached("seasonal_decomposition.csv")


def load_country_benchmarks() -> pd.DataFrame:
    return _load_csv_cached("country_benchmarks.csv")


def load_drilldown_lvl2() -> pd.DataFrame:
    """HS2 tier of the partner drill-down (all partners, all years), derived from product_partners."""
    return _derived_cached("partner_drilldown_lvl2(derived)", "product_partners.csv", build_hs2_drilldown)


def load_drilldown_lvl4() -> pd.DataFrame:
    return _load_csv_cached("partner_drilldown_lvl4.csv")


def load_drilldown_lvl8() -> pd.DataFrame:
    return _load_csv_cached("partner_drilldown_lvl8.csv")


def clear_loader_cache():
    """Clear memory caches when datasets are re-processed."""
    _CACHE.clear()
    _MTIME.clear()
