"""Data loader module for the dashboard.
Loads processed CSV datasets directly using pandas.read_csv with smart mtime cache invalidation.
"""

from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import PROCESSED_DIR

_CACHE = {}
_MTIME = {}


def _load_csv_cached(filename: str, dtype: dict = None) -> pd.DataFrame:
    """Load CSV with automatic cache invalidation when file mtime changes."""
    path = PROCESSED_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        mtime = path.stat().st_mtime
        if filename in _CACHE and _MTIME.get(filename) == mtime and not _CACHE[filename].empty:
            return _CACHE[filename]
        df = pd.read_csv(path, dtype=dtype)
        if not df.empty:
            # Normalize product codes if present
            if "hs2_code" in df.columns:
                df["hs2_code"] = df["hs2_code"].astype(str).str.zfill(2)
            if "hs4_code" in df.columns:
                df["hs4_code"] = df["hs4_code"].astype(str).str.zfill(4)
            if "hs2_parent" in df.columns:
                df["hs2_parent"] = df["hs2_parent"].astype(str).str.zfill(2)
            if "product_code" in df.columns:
                df["product_code"] = df["product_code"].astype(str)
            _CACHE[filename] = df
            _MTIME[filename] = mtime
        return df
    except Exception as e:
        if filename in _CACHE:
            return _CACHE[filename]
        return pd.DataFrame()


def load_overview_kpis() -> pd.DataFrame:
    return _load_csv_cached("overview_kpis.csv")


def load_partner_rankings() -> pd.DataFrame:
    return _load_csv_cached("partner_rankings.csv", dtype={"partner_code": str})


def load_product_rankings() -> pd.DataFrame:
    return _load_csv_cached("product_rankings.csv", dtype={"hs2_code": str})


def load_hs4_product_rankings() -> pd.DataFrame:
    return _load_csv_cached("hs4_product_rankings.csv", dtype={"hs4_code": str, "hs2_parent": str})


def load_product_partners() -> pd.DataFrame:
    return _load_csv_cached("product_partners.csv", dtype={"hs2_code": str, "partner_code": str})



def load_seasonal_decomposition() -> pd.DataFrame:
    return _load_csv_cached("seasonal_decomposition.csv")


def load_country_benchmarks() -> pd.DataFrame:
    return _load_csv_cached("country_benchmarks.csv")


def load_drilldown_lvl2() -> pd.DataFrame:
    return _load_csv_cached("partner_drilldown_lvl2.csv")


def load_drilldown_lvl4() -> pd.DataFrame:
    return _load_csv_cached("partner_drilldown_lvl4.csv")


def load_drilldown_lvl8() -> pd.DataFrame:
    return _load_csv_cached("partner_drilldown_lvl8.csv")


def clear_loader_cache():
    """Clear memory caches when datasets are re-processed."""
    _CACHE.clear()
    _MTIME.clear()
