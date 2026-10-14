"""Data ingestion script for Eurostat ds-045409 Comext trade data.
Pulls:
1. Annual partner data for Luxembourg (2000-2026)
2. Annual HS2 product data for Luxembourg (2000-2026)
3. Annual benchmark data for peer countries (LU, BE, DE, FR, NL) (2000-2026)
4. Monthly time series data for seasonality analysis (2000-2026)
5. Hierarchical drill-down data (HS2, HS4, HS6, CN8) for top partner countries

Saves raw data into data/bronze/ as cached JSON files.
"""

import os
import json
import time
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
import urllib3

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    COMEXT_API_URL,
    BRONZE_DIR,
    START_YEAR,
    END_YEAR,
    PRIMARY_REPORTER,
    PEER_REPORTERS,
    ALL_HS2_CHAPTERS,
)

# Suppress SSL insecure request warnings (necessary in environments with custom proxy certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Key trading partners to acquire hierarchical CN8/HS4 drilldown data for
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


def fetch_url(url: str, cache_file: Path, force_reload: bool = False, max_retries: int = 3) -> Dict[str, Any]:
    """Fetch JSON from Eurostat Comext API with local file caching and retry logic."""
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    if cache_file.exists() and not force_reload:
        logger.info(f"Loading cached file: {cache_file.name}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Fetching from Eurostat: {url[:100]}... (Attempt {attempt}/{max_retries})")
            t0 = time.time()
            response = requests.get(url, verify=False, timeout=60)
            if response.status_code == 200:
                data = response.json()
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                logger.info(f"Saved {cache_file.name} ({len(response.content)/1024:.1f} KB in {time.time()-t0:.2f}s)")
                return data
            else:
                logger.warning(f"HTTP {response.status_code} for {url[:100]}: {response.text[:200]}")
        except Exception as e:
            logger.warning(f"Error fetching {url[:100]}: {e}")
        time.sleep(2 * attempt)

    raise RuntimeError(f"Failed to fetch data after {max_retries} attempts for: {url}")


def fetch_partners_annual(force_reload: bool = False) -> Dict[str, Any]:
    """Fetch Luxembourg annual trade with all partner countries (product=TOTAL) from 2000 to 2026."""
    url = (
        f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}&product=TOTAL"
        f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}&untilTimePeriod={END_YEAR}"
    )
    cache_file = BRONZE_DIR / "partners_annual_2000_2026.json"
    return fetch_url(url, cache_file, force_reload=force_reload)


def fetch_hs2_products_annual(force_reload: bool = False) -> List[Dict[str, Any]]:
    """Fetch Luxembourg annual trade for all HS2 chapters (01-99) with partner=WORLD from 2000 to 2026."""
    results = []
    # Query in batches of 25 chapters to ensure robust API response
    chunk_size = 25
    for i in range(0, len(ALL_HS2_CHAPTERS), chunk_size):
        chunk = ALL_HS2_CHAPTERS[i : i + chunk_size]
        products_param = "&".join([f"product={code}" for code in chunk])
        url = (
            f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}&partner=WORLD"
            f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}&untilTimePeriod={END_YEAR}&{products_param}"
        )
        cache_file = BRONZE_DIR / f"hs2_products_annual_batch_{i//chunk_size}.json"
        data = fetch_url(url, cache_file, force_reload=force_reload)
        results.append(data)
    return results


def fetch_country_benchmarks(force_reload: bool = False) -> Dict[str, Any]:
    """Fetch annual trade for peer countries (LU, BE, DE, FR, NL) with partner=WORLD from 2000 to 2026."""
    reporters_param = "&".join([f"reporter={r}" for r in PEER_REPORTERS])
    url = (
        f"{COMEXT_API_URL}?freq=A&{reporters_param}&partner=WORLD&product=TOTAL"
        f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}&untilTimePeriod={END_YEAR}"
    )
    cache_file = BRONZE_DIR / "country_benchmarks_annual_2000_2026.json"
    return fetch_url(url, cache_file, force_reload=force_reload)


def fetch_monthly_seasonality(force_reload: bool = False) -> List[Dict[str, Any]]:
    """Fetch monthly trade for Luxembourg with partner=WORLD for TOTAL and key product chapters (2000-2026)."""
    results = []
    for chapter in TOP_SEASONAL_CHAPTERS:
        url = (
            f"{COMEXT_API_URL}?freq=M&reporter={PRIMARY_REPORTER}&partner=WORLD&product={chapter}"
            f"&indicators=VALUE_IN_EUROS&sinceTimePeriod={START_YEAR}-01&untilTimePeriod={END_YEAR}-12"
        )
        cache_file = BRONZE_DIR / f"monthly_seasonality_{chapter}.json"
        data = fetch_url(url, cache_file, force_reload=force_reload)
        results.append(data)
    return results


def fetch_partner_drilldown(partners: List[str] = KEY_PARTNERS, years: List[int] = [2023, 2024], force_reload: bool = False) -> List[Dict[str, Any]]:
    """Fetch complete hierarchical product drill-down (HS2, HS4, HS6, CN8) for key trading partners."""
    results = []
    for partner in partners:
        for year in years:
            url = (
                f"{COMEXT_API_URL}?freq=A&reporter={PRIMARY_REPORTER}&partner={partner}"
                f"&time={year}&indicators=VALUE_IN_EUROS"
            )
            cache_file = BRONZE_DIR / f"partner_drilldown_{partner}_{year}.json"
            try:
                data = fetch_url(url, cache_file, force_reload=force_reload)
                results.append(data)
            except Exception as e:
                logger.error(f"Failed to fetch drill-down for {partner} in {year}: {e}")
    return results


def run_all_ingestion(force_reload: bool = False):
    """Run full ingestion pipeline across all data dimensions."""
    logger.info("=== Starting Bronze Ingestion Pipeline (Eurostat Comext ds-045409) ===")
    
    logger.info("1/5: Fetching annual partner trade (2000-2026)...")
    fetch_partners_annual(force_reload=force_reload)

    logger.info("2/5: Fetching annual HS2 product trade (2000-2026)...")
    fetch_hs2_products_annual(force_reload=force_reload)

    logger.info("3/5: Fetching peer country benchmarks (2000-2026)...")
    fetch_country_benchmarks(force_reload=force_reload)

    logger.info("4/5: Fetching monthly seasonality data (2000-2026)...")
    fetch_monthly_seasonality(force_reload=force_reload)

    logger.info("5/5: Fetching hierarchical partner drilldown (HS2 -> CN8)...")
    fetch_partner_drilldown(partners=KEY_PARTNERS[:5], years=[2023], force_reload=force_reload)

    logger.info("=== Bronze Ingestion Pipeline Completed Successfully ===")


if __name__ == "__main__":
    run_all_ingestion()
