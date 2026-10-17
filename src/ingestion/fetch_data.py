"""Data ingestion module for Eurostat ds-045409 Comext trade data.
Pulls data directly from Eurostat API, parses the JSON-stat response in memory,
and saves the output directly as clean tabular CSV files in data/raw/.
No raw JSON files are stored on disk.

Coverage guarantees (all driven by ``src/config.py``):
    * every annual table spans START_YEAR..END_YEAR
    * monthly seasonality and peer benchmarks cover ``TOTAL`` + every HS2 chapter
    * HS4 / CN8 tiers are fetched year by year so the year selector of the dashboard
      is never answered with data of a different year

A cached raw file is only reused when it already covers the required years, so a
previously partial extract is automatically refreshed.
"""

import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
import urllib3
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    API_YEAR_WINDOW,
    ALL_HS2_CHAPTERS,
    BENCHMARK_PRODUCTS,
    CN8_TOP_N_PER_YEAR_FLOW,
    COMEXT_API_URL,
    DRILLDOWN_TOP_N,
    END_YEAR,
    KEY_PARTNERS,
    MAX_WORKERS,
    PEER_REPORTERS,
    PRIMARY_REPORTER,
    RAW_DIR,
    SEASONAL_PRODUCTS,
    START_YEAR,
)
from src.ingestion.jsonstat_parser import jsonstat_to_dataframe

# Suppress SSL insecure request warnings (necessary in environments with custom proxy certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CHAPTER_CHUNK_SIZE = 25
# A few HS2 codes (e.g. the unused chapter 77) never carry data; they must not force a re-download.
EMPTY_CHAPTER_TOLERANCE = 3
ALL_YEARS = list(range(START_YEAR, END_YEAR + 1))


# â”€â”€ Generic helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def fetch_jsonstat_df(params: Dict[str, Any], max_retries: int = 4) -> pd.DataFrame:
    """Fetch Eurostat JSON-stat data and parse it into a DataFrame in memory.

    ``params`` is passed to ``requests`` (list values become repeated query keys).
    """
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            response = requests.get(COMEXT_API_URL, params=params, verify=False, timeout=180)
            if response.status_code == 200:
                df = jsonstat_to_dataframe(response.json())
                logger.info(f"Fetched {len(df):,} rows in {time.time() - t0:.1f}s ({_describe(params)})")
                return df
            logger.warning(f"HTTP {response.status_code} for {_describe(params)}: {response.text[:150]}")
            if response.status_code == 413:
                break  # retrying an oversized request cannot succeed
        except Exception as e:  # network / parsing errors are retried
            logger.warning(f"Error fetching {_describe(params)}: {e}")
        time.sleep(2 * attempt)
    raise RuntimeError(f"Failed to fetch data after {max_retries} attempts for: {params}")


def _describe(params: Dict[str, Any]) -> str:
    """Compact, log-friendly description of a request."""
    short = {}
    for key, value in params.items():
        if isinstance(value, (list, tuple)) and len(value) > 3:
            short[key] = f"[{value[0]}..{value[-1]}]x{len(value)}"
        else:
            short[key] = value
    return str(short)


def _fetch_many(param_list: Iterable[Dict[str, Any]], tolerate_errors: bool = False) -> List[pd.DataFrame]:
    """Fetch several requests concurrently, keeping the submission order."""
    param_list = list(param_list)

    def _one(params: Dict[str, Any]) -> pd.DataFrame:
        try:
            return fetch_jsonstat_df(params)
        except Exception as e:
            if not tolerate_errors:
                raise
            logger.error(f"Skipping failed request {_describe(params)}: {e}")
            return pd.DataFrame()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(_one, param_list))
    return [df for df in results if not df.empty]


def _chunks(items: List[str], size: int) -> List[List[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _year_windows(window: int = API_YEAR_WINDOW) -> List[tuple]:
    """Split START_YEAR..END_YEAR in (since, until) windows."""
    return [(y, min(y + window - 1, END_YEAR)) for y in range(START_YEAR, END_YEAR + 1, window)]


def _is_cached(
    path: Path,
    force_reload: bool,
    years: Optional[Iterable[int]] = None,
    products: Optional[Iterable[str]] = None,
) -> bool:
    """A raw file is reusable only if it exists and already covers the requested years/products."""
    if force_reload or not path.exists():
        return False
    try:
        cols = pd.read_csv(path, usecols=["time", "product"], dtype=str)
    except Exception:
        return False
    if years is not None:
        missing_years = set(years) - set(cols["time"].str[:4].astype(int))
        if missing_years:
            logger.info(f"{path.name} lacks years {sorted(missing_years)[:5]}..., re-extracting")
            return False
    if products is not None:
        missing_products = set(products) - set(cols["product"])
        if len(missing_products) > EMPTY_CHAPTER_TOLERANCE:
            logger.info(f"{path.name} lacks {len(missing_products)} products, re-extracting")
            return False
    logger.info(f"Using existing raw file: {path.name}")
    return True


def _save(df: pd.DataFrame, path: Path) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"Saved {path.name}: {len(df):,} rows")
    return path


def _top_n(df: pd.DataFrame, n: int, group_cols: List[str]) -> pd.DataFrame:
    """Keep the n largest lines inside each group."""
    return (
        df.sort_values("value", ascending=False)
        .groupby(group_cols, sort=False)
        .head(n)
        .sort_values(group_cols + ["value"], ascending=[True] * len(group_cols) + [False])
        .reset_index(drop=True)
    )


# â”€â”€ Annual tables â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def fetch_partners_annual_csv(force_reload: bool = False) -> Path:
    """Luxembourg annual trade with all partner countries (product=TOTAL)."""
    output_file = RAW_DIR / "partners_annual_raw.csv"
    if _is_cached(output_file, force_reload, ALL_YEARS):
        return output_file
    df = fetch_jsonstat_df({
        "freq": "A", "reporter": PRIMARY_REPORTER, "product": "TOTAL",
        "indicators": "VALUE_IN_EUROS", "sinceTimePeriod": START_YEAR, "untilTimePeriod": END_YEAR,
    })
    return _save(df, output_file)


def fetch_hs2_products_annual_csv(force_reload: bool = False) -> Path:
    """Luxembourg annual world trade for all HS2 chapters (01-99)."""
    output_file = RAW_DIR / "hs2_products_annual_raw.csv"
    if _is_cached(output_file, force_reload, ALL_YEARS):
        return output_file
    requests_ = [
        {
            "freq": "A", "reporter": PRIMARY_REPORTER, "partner": "WORLD",
            "indicators": "VALUE_IN_EUROS", "sinceTimePeriod": START_YEAR, "untilTimePeriod": END_YEAR,
            "product": chunk,
        }
        for chunk in _chunks(ALL_HS2_CHAPTERS, CHAPTER_CHUNK_SIZE)
    ]
    return _save(pd.concat(_fetch_many(requests_), ignore_index=True), output_file)


def fetch_product_partners_csv(force_reload: bool = False) -> Path:
    """Luxembourg annual trade for every HS2 chapter across every partner country."""
    output_file = RAW_DIR / "product_partners_raw.csv"
    if _is_cached(output_file, force_reload, ALL_YEARS):
        return output_file
    requests_ = [
        {
            "freq": "A", "reporter": PRIMARY_REPORTER, "indicators": "VALUE_IN_EUROS",
            "sinceTimePeriod": since, "untilTimePeriod": until, "product": chunk,
        }
        for chunk in _chunks(ALL_HS2_CHAPTERS, CHAPTER_CHUNK_SIZE)
        for since, until in _year_windows()
    ]
    return _save(pd.concat(_fetch_many(requests_), ignore_index=True), output_file)


def fetch_country_benchmarks_csv(force_reload: bool = False) -> Path:
    """Annual trade of the peer countries (LU, BE, DE, FR, NL) for TOTAL and every HS2 chapter."""
    output_file = RAW_DIR / "country_benchmarks_annual_raw.csv"
    if _is_cached(output_file, force_reload, ALL_YEARS, BENCHMARK_PRODUCTS):
        return output_file
    requests_ = [
        {
            "freq": "A", "reporter": PEER_REPORTERS, "partner": "WORLD",
            "indicators": "VALUE_IN_EUROS", "sinceTimePeriod": START_YEAR, "untilTimePeriod": END_YEAR,
            "product": chunk,
        }
        for chunk in _chunks(BENCHMARK_PRODUCTS, CHAPTER_CHUNK_SIZE)
    ]
    return _save(pd.concat(_fetch_many(requests_), ignore_index=True), output_file)


# â”€â”€ Detailed tiers: one request per year yields HS4 and CN8 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def fetch_detailed_products_annual_csv(force_reload: bool = False) -> List[Path]:
    """Luxembourg world trade for every 4-digit heading and the largest CN8 lines, per year.

    A single Eurostat call per year returns all product tiers, so HS4 and CN8 are
    extracted together (previously two identical downloads) and each year is handled
    independently to stay under the API size limit.
    """
    hs4_file = RAW_DIR / "hs4_products_annual_raw.csv"
    hs8_file = RAW_DIR / "hs8_products_annual_raw.csv"
    if _is_cached(hs4_file, force_reload, ALL_YEARS) and _is_cached(hs8_file, force_reload, ALL_YEARS):
        return [hs4_file, hs8_file]

    requests_ = [
        {
            "freq": "A", "reporter": PRIMARY_REPORTER, "partner": "WORLD",
            "indicators": "VALUE_IN_EUROS", "time": year,
        }
        for year in ALL_YEARS
    ]
    frames = _fetch_many(requests_)
    full = pd.concat(frames, ignore_index=True)
    code_len = full["product"].astype(str).str.len()

    hs4 = full[code_len == 4].reset_index(drop=True)
    hs8 = _top_n(full[code_len == 8], CN8_TOP_N_PER_YEAR_FLOW, ["time", "flow"])
    return [_save(hs4, hs4_file), _save(hs8, hs8_file)]


def fetch_partner_drilldown_csv(partners: Optional[List[str]] = None, force_reload: bool = False) -> Path:
    """Largest HS4 and CN8 lines per key partner, flow and year.

    HS2 detail for *every* partner comes from the product-partner table, so only the
    finer tiers are fetched here, keeping the DRILLDOWN_TOP_N largest lines per tier.
    """
    partners = partners or KEY_PARTNERS
    output_file = RAW_DIR / "partner_drilldown_raw.csv"
    if _is_cached(output_file, force_reload, ALL_YEARS):
        return output_file

    requests_ = [
        {
            "freq": "A", "reporter": PRIMARY_REPORTER, "partner": partner,
            "indicators": "VALUE_IN_EUROS", "time": year,
        }
        for partner in partners
        for year in ALL_YEARS
    ]

    def _reduce(df: pd.DataFrame) -> pd.DataFrame:
        code_len = df["product"].astype(str).str.len()
        kept = []
        for level in (4, 8):
            tier = df[code_len == level].copy()
            tier["code_level"] = level
            kept.append(_top_n(tier, DRILLDOWN_TOP_N, ["partner", "time", "flow"]))
        return pd.concat(kept, ignore_index=True)

    def _one(params: Dict[str, Any]) -> pd.DataFrame:
        try:
            df = fetch_jsonstat_df(params)
        except Exception as e:
            logger.error(f"Failed drill-down {params['partner']} {params['time']}: {e}")
            return pd.DataFrame()
        return _reduce(df) if not df.empty else df

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        frames = [df for df in pool.map(_one, requests_) if not df.empty]
    return _save(pd.concat(frames, ignore_index=True), output_file)


def fetch_hs4_products_annual_csv(years: List[int] = [2020, 2021, 2022, 2023, 2024, 2025], force_reload: bool = False) -> Path:
    """Fetch Luxembourg annual trade for all 4-digit HS subheadings directly to CSV."""
    output_file = RAW_DIR / "hs4_products_annual_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
# â”€â”€ Monthly table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def fetch_monthly_seasonality_csv(force_reload: bool = False) -> Path:
    """Monthly Luxembourg trade for TOTAL and every HS2 chapter."""
    output_file = RAW_DIR / "monthly_seasonality_raw.csv"
    if _is_cached(output_file, force_reload, ALL_YEARS, SEASONAL_PRODUCTS):
        return output_file
    requests_ = [
        {
            "freq": "M", "reporter": PRIMARY_REPORTER, "partner": "WORLD", "product": product,
            "indicators": "VALUE_IN_EUROS",
            "sinceTimePeriod": f"{START_YEAR}-01", "untilTimePeriod": f"{END_YEAR}-12",
        }
        for product in SEASONAL_PRODUCTS
    ]
    return _save(pd.concat(_fetch_many(requests_, tolerate_errors=True), ignore_index=True), output_file)


def run_all_ingestion(force_reload: bool = False):
    """Run full ingestion pipeline writing directly to CSV."""
    logger.info("=== Starting Eurostat Comext Ingestion to Tabular CSV (data/raw/) ===")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("1/7: Extracting annual partner trade to CSV...")
    fetch_partners_annual_csv(force_reload=force_reload)

    logger.info("2/7: Extracting annual HS2 product trade to CSV...")
    fetch_hs2_products_annual_csv(force_reload=force_reload)

    logger.info("3/7: Extracting annual HS4 headings and CN8 tariff lines to CSV...")
    fetch_detailed_products_annual_csv(force_reload=force_reload)

    logger.info("4/7: Extracting peer country benchmarks to CSV...")
    fetch_country_benchmarks_csv(force_reload=force_reload)

    logger.info("5/7: Extracting monthly seasonality data to CSV...")
    fetch_monthly_seasonality_csv(force_reload=force_reload)

    logger.info("6/7: Extracting product trading partners (HS2 across countries) to CSV...")
    fetch_product_partners_csv(force_reload=force_reload)

    logger.info("7/7: Extracting hierarchical partner drilldown (HS4 / CN8) to CSV...")
    fetch_partner_drilldown_csv(force_reload=force_reload)

    logger.info("=== Tabular CSV Ingestion Completed Successfully ===")


if __name__ == "__main__":
    run_all_ingestion()
