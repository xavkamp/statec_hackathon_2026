"""Data ingestion module for Eurostat ds-045409 Comext trade data.
Pulls data directly from Eurostat API, parses the JSON-stat response in memory,
and saves the output directly as clean tabular CSV files in data/raw/.
No raw JSON files are stored on disk.
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
import urllib3
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    COMEXT_API_URL,
    RAW_DIR,
    START_YEAR,
    END_YEAR,
    PRIMARY_REPORTER,
    PEER_REPORTERS,
    ALL_HS2_CHAPTERS,
)
from src.ingestion.jsonstat_parser import jsonstat_to_dataframe

# Suppress SSL insecure request warnings (necessary in environments with custom proxy certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Key trading partners for hierarchical CN8/HS4 drilldown
KEY_PARTNERS = ["DE", "BE", "FR", "NL", "US", "CN", "IT", "GB", "PL", "CH"]

# Top product chapters for monthly seasonality analysis
TOP_SEASONAL_CHAPTERS = [
    "TOTAL",
    "72",  # Iron and steel
    "73",  # Articles of iron or steel
    "84",  # Machinery and mechanical appliances
    "85",  # Electrical machinery and equipment
    "87",  # Vehicles and automotive
    "39",  # Plastics and articles thereof
    "40",  # Rubber and articles thereof
    "30",  # Pharmaceutical products
    "27",  # Mineral fuels, oils and products
    "48",  # Paper and paperboard
]


def fetch_jsonstat_df(url: str, max_retries: int = 3) -> pd.DataFrame:
    """Fetch Eurostat JSON-stat data over HTTP and parse directly into a pandas DataFrame in memory."""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Querying Eurostat API: {url[:100]}... (Attempt {attempt}/{max_retries})")
            t0 = time.time()
            response = requests.get(url, verify=False, timeout=60)
            if response.status_code == 200:
                raw_json = response.json()
                df = jsonstat_to_dataframe(raw_json)
                logger.info(f"Fetched and parsed {len(df):,} rows in {time.time()-t0:.2f}s")
                return df
            else:
                logger.warning(f"HTTP {response.status_code} for {url[:100]}: {response.text[:200]}")
        except Exception as e:
            logger.warning(f"Error fetching {url[:100]}: {e}")
        time.sleep(2 * attempt)

    raise RuntimeError(f"Failed to fetch data after {max_retries} attempts for: {url}")


def fetch_partners_annual_csv(force_reload: bool = False) -> Path:
    """Fetch Luxembourg annual trade with all partner countries (product=TOTAL) directly to CSV."""
    output_file = RAW_DIR / "partners_annual_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
        return output_file

    url = (
        f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}&product=TOTAL"
        f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}&untilTimePeriod={END_YEAR}"
    )
    df = fetch_jsonstat_df(url)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {output_file.name}: {len(df):,} rows")
    return output_file


def fetch_hs2_products_annual_csv(force_reload: bool = False) -> Path:
    """Fetch Luxembourg annual trade for all HS2 chapters (01-99) directly to CSV."""
    output_file = RAW_DIR / "hs2_products_annual_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
        return output_file

    dfs = []
    chunk_size = 25
    for i in range(0, len(ALL_HS2_CHAPTERS), chunk_size):
        chunk = ALL_HS2_CHAPTERS[i : i + chunk_size]
        products_param = "&".join([f"product={code}" for code in chunk])
        url = (
            f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}&partner=WORLD"
            f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}&untilTimePeriod={END_YEAR}&{products_param}"
        )
        chunk_df = fetch_jsonstat_df(url)
        if not chunk_df.empty:
            dfs.append(chunk_df)

    combined_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {output_file.name}: {len(combined_df):,} rows")
    return output_file


def fetch_country_benchmarks_csv(force_reload: bool = False) -> Path:
    """Fetch annual trade for peer countries (LU, BE, DE, FR, NL) directly to CSV."""
    output_file = RAW_DIR / "country_benchmarks_annual_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
        return output_file

    reporters_param = "&".join([f"reporter={r}" for r in PEER_REPORTERS])
    url = (
        f"{COMEXT_API_URL}?freq=A&{reporters_param}&partner=WORLD&product=TOTAL"
        f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}&untilTimePeriod={END_YEAR}"
    )
    df = fetch_jsonstat_df(url)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {output_file.name}: {len(df):,} rows")
    return output_file


def fetch_monthly_seasonality_csv(force_reload: bool = False) -> Path:
    """Fetch monthly trade for Luxembourg across key product chapters directly to CSV."""
    output_file = RAW_DIR / "monthly_seasonality_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
        return output_file

    dfs = []
    for chapter in TOP_SEASONAL_CHAPTERS:
        url = (
            f"{COMEXT_API_URL}?freq=M&reporter={PRIMARY_REPORTER}&partner=WORLD&product={chapter}"
            f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}-01&untilTimePeriod={END_YEAR}-12"
        )
        ch_df = fetch_jsonstat_df(url)
        if not ch_df.empty:
            dfs.append(ch_df)

    combined_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {output_file.name}: {len(combined_df):,} rows")
    return output_file


def fetch_partner_drilldown_csv(partners: List[str] = KEY_PARTNERS[:5], years: List[int] = [2023], force_reload: bool = False) -> Path:
    """Fetch complete hierarchical product drill-down (HS2, HS4, HS6, CN8) directly to CSV."""
    output_file = RAW_DIR / "partner_drilldown_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
        return output_file

    dfs = []
    for partner in partners:
        for year in years:
            url = (
                f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}&partner={partner}"
                f"&time={year}&indicators=VALUE_IN_EUROS"
            )
            try:
                p_df = fetch_jsonstat_df(url)
                if not p_df.empty:
                    dfs.append(p_df)
            except Exception as e:
                logger.error(f"Failed to fetch drill-down for {partner} in {year}: {e}")

    combined_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {output_file.name}: {len(combined_df):,} rows")
    return output_file


def fetch_product_partners_csv(force_reload: bool = False) -> Path:
    """Fetch Luxembourg annual trade for all HS2 chapters across all partner countries directly to CSV."""
    output_file = RAW_DIR / "product_partners_raw.csv"
    if output_file.exists() and not force_reload:
        logger.info(f"Using existing raw file: {output_file.name}")
        return output_file

    dfs = []
    chunk_size = 25
    for i in range(0, len(ALL_HS2_CHAPTERS), chunk_size):
        chunk = ALL_HS2_CHAPTERS[i : i + chunk_size]
        products_param = "&".join([f"product={code}" for code in chunk])
        url = (
            f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}"
            f"&indicators=VALUE_IN_EUROS&sinceTimePeriod=2020&untilTimePeriod={END_YEAR}&{products_param}"
        )
        try:
            chunk_df = fetch_jsonstat_df(url)
            if not chunk_df.empty:
                dfs.append(chunk_df)
        except Exception as e:
            logger.error(f"Error fetching product partners chunk {i}: {e}")

    combined_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved {output_file.name}: {len(combined_df):,} rows")
    return output_file


def run_all_ingestion(force_reload: bool = False):
    """Run full ingestion pipeline writing directly to CSV."""
    logger.info("=== Starting Eurostat Comext Ingestion to Tabular CSV (data/raw/) ===")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("1/6: Extracting annual partner trade to CSV...")
    fetch_partners_annual_csv(force_reload=force_reload)

    logger.info("2/6: Extracting annual HS2 product trade to CSV...")
    fetch_hs2_products_annual_csv(force_reload=force_reload)

    logger.info("3/6: Extracting peer country benchmarks to CSV...")
    fetch_country_benchmarks_csv(force_reload=force_reload)

    logger.info("4/6: Extracting monthly seasonality data to CSV...")
    fetch_monthly_seasonality_csv(force_reload=force_reload)

    logger.info("5/6: Extracting hierarchical partner drilldown (HS2 -> CN8) to CSV...")
    fetch_partner_drilldown_csv(force_reload=force_reload)

    logger.info("6/6: Extracting product trading partners (HS2 across countries) to CSV...")
    fetch_product_partners_csv(force_reload=force_reload)

    logger.info("=== Tabular CSV Ingestion Completed Successfully ===")


if __name__ == "__main__":
    run_all_ingestion()

