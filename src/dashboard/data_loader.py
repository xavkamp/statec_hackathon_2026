"""Data loader module for the dashboard.
Provides cached access to Gold Parquet datasets.
"""

from functools import lru_cache
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import GOLD_DIR


@lru_cache(maxsize=1)
def load_overview_kpis() -> pd.DataFrame:
    path = GOLD_DIR / "gold_overview_kpis.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_partner_rankings() -> pd.DataFrame:
    path = GOLD_DIR / "gold_partner_rankings.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_product_rankings() -> pd.DataFrame:
    path = GOLD_DIR / "gold_product_rankings.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_seasonal_decomposition() -> pd.DataFrame:
    path = GOLD_DIR / "gold_seasonal_decomposition.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_country_benchmarks() -> pd.DataFrame:
    path = GOLD_DIR / "gold_country_benchmarks.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_drilldown_lvl2() -> pd.DataFrame:
    path = GOLD_DIR / "gold_partner_drilldown_lvl2.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_drilldown_lvl4() -> pd.DataFrame:
    path = GOLD_DIR / "gold_partner_drilldown_lvl4.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_drilldown_lvl8() -> pd.DataFrame:
    path = GOLD_DIR / "gold_partner_drilldown_lvl8.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()
