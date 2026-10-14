"""Silver Layer transformation script.
Processes Bronze raw JSON files into validated, clean, typed Parquet tables in data/silver/.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Ensure project root is in path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import BRONZE_DIR, SILVER_DIR, get_hs_section
from src.ingestion.jsonstat_parser import jsonstat_to_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

AGGREGATE_PARTNER_CODES = {
    "WORLD", "INT_EU", "EXT_EU", "INT_EU27_2020", "EXT_EU27_2020",
    "INT_EA", "EXT_EA", "INT_EA21", "EXT_EA21"
}


def build_silver_partners_annual() -> pd.DataFrame:
    """Transform annual partner trade data into silver table."""
    bronze_file = BRONZE_DIR / "partners_annual_2000_2026.json"
    logger.info(f"Building silver_partners_annual from {bronze_file.name}")
    with open(bronze_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = jsonstat_to_dataframe(data)
    if df.empty:
        raise ValueError("Empty DataFrame from partners_annual_2000_2026.json")

    # Rename & select columns
    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["partner_code"] = df["partner"]
    df["partner_name"] = df["partner_label"]
    df["value_eur"] = df["value"].astype("float64")
    df["is_aggregate"] = df["partner_code"].isin(AGGREGATE_PARTNER_CODES)

    res = df[["year", "flow", "partner_code", "partner_name", "value_eur", "is_aggregate"]].copy()
    res = res.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])

    output_path = SILVER_DIR / "silver_partners_annual.parquet"
    res.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(res):,} rows")
    return res


def build_silver_hs2_products_annual() -> pd.DataFrame:
    """Transform annual HS2 product trade data into silver table."""
    dfs = []
    for batch_file in sorted(BRONZE_DIR.glob("hs2_products_annual_batch_*.json")):
        logger.info(f"Loading {batch_file.name}")
        with open(batch_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        sub_df = jsonstat_to_dataframe(data)
        if not sub_df.empty:
            dfs.append(sub_df)

    if not dfs:
        raise ValueError("No HS2 batch files found in Bronze directory")

    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["hs2_code"] = df["product"].astype(str).str.zfill(2)
    df["hs2_name"] = df["product_label"]
    df["hs_section"] = df["hs2_code"].apply(get_hs_section)
    df["value_eur"] = df["value"].astype("float64")

    res = df[["year", "flow", "hs2_code", "hs2_name", "hs_section", "value_eur"]].copy()
    res = res.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])

    output_path = SILVER_DIR / "silver_hs2_products_annual.parquet"
    res.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(res):,} rows")
    return res


def build_silver_country_benchmarks() -> pd.DataFrame:
    """Transform peer country benchmarks into silver table."""
    bronze_file = BRONZE_DIR / "country_benchmarks_annual_2000_2026.json"
    logger.info(f"Building silver_country_benchmarks from {bronze_file.name}")
    with open(bronze_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = jsonstat_to_dataframe(data)
    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["reporter_code"] = df["reporter"]
    df["reporter_name"] = df["reporter_label"].apply(lambda s: s.split("(")[0].strip())
    df["flow"] = df["flow_label"].str.upper()
    df["value_eur"] = df["value"].astype("float64")

    res = df[["year", "reporter_code", "reporter_name", "flow", "value_eur"]].copy()
    res = res.sort_values(by=["year", "reporter_code", "flow"])

    output_path = SILVER_DIR / "silver_country_benchmarks.parquet"
    res.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(res):,} rows")
    return res


def build_silver_monthly_seasonality() -> pd.DataFrame:
    """Transform monthly time series for seasonality analysis into silver table."""
    dfs = []
    for month_file in sorted(BRONZE_DIR.glob("monthly_seasonality_*.json")):
        logger.info(f"Loading {month_file.name}")
        with open(month_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        sub_df = jsonstat_to_dataframe(data)
        if not sub_df.empty:
            dfs.append(sub_df)

    if not dfs:
        raise ValueError("No monthly seasonality files found in Bronze directory")

    df = pd.concat(dfs, ignore_index=True)
    # Eurostat monthly time format is 'YYYY-MM'
    df["time_str"] = df["time"].astype(str)
    parts = df["time_str"].str.split("-", expand=True)
    df["year"] = pd.to_numeric(parts[0], errors="coerce").astype("int16")
    df["month"] = pd.to_numeric(parts[1], errors="coerce").astype("int8")
    df["date"] = pd.to_datetime(df["time_str"] + "-01")
    df["flow"] = df["flow_label"].str.upper()
    df["product_code"] = df["product"]
    df["product_name"] = df["product_label"]
    df["value_eur"] = df["value"].astype("float64")

    res = df[["date", "year", "month", "product_code", "product_name", "flow", "value_eur"]].copy()
    res = res.sort_values(by=["product_code", "flow", "date"])

    output_path = SILVER_DIR / "silver_monthly_seasonality.parquet"
    res.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(res):,} rows")
    return res


def build_silver_partner_drilldown() -> pd.DataFrame:
    """Transform hierarchical partner drill-down (HS2 -> CN8) into silver table."""
    dfs = []
    for drilldown_file in sorted(BRONZE_DIR.glob("partner_drilldown_*.json")):
        logger.info(f"Loading {drilldown_file.name}")
        with open(drilldown_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        sub_df = jsonstat_to_dataframe(data)
        if not sub_df.empty:
            dfs.append(sub_df)

    if not dfs:
        logger.warning("No partner drilldown files found")
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["partner_code"] = df["partner"]
    df["partner_name"] = df["partner_label"].apply(lambda s: s.split("(")[0].strip())
    df["flow"] = df["flow_label"].str.upper()
    df["product_code"] = df["product"].astype(str)
    df["product_name"] = df["product_label"]
    df["value_eur"] = df["value"].astype("float64")

    # Determine code level and parent codes
    df["code_level"] = df["product_code"].str.len().astype("int8")
    df["hs2_parent"] = df["product_code"].str[:2]
    df["hs4_parent"] = np.where(df["code_level"] >= 4, df["product_code"].str[:4], None)
    df["hs6_parent"] = np.where(df["code_level"] >= 6, df["product_code"].str[:6], None)
    df["hs_section"] = df["hs2_parent"].apply(get_hs_section)

    res = df[[
        "year", "partner_code", "partner_name", "flow",
        "product_code", "product_name", "code_level",
        "hs2_parent", "hs4_parent", "hs6_parent", "hs_section",
        "value_eur"
    ]].copy()
    res = res.sort_values(by=["partner_code", "flow", "code_level", "value_eur"], ascending=[True, True, True, False])

    output_path = SILVER_DIR / "silver_partner_drilldown.parquet"
    res.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(res):,} rows")
    return res


def run_all_silver_transforms():
    """Run all Silver transformations."""
    logger.info("=== Starting Silver Transformation Pipeline ===")
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    build_silver_partners_annual()
    build_silver_hs2_products_annual()
    build_silver_country_benchmarks()
    build_silver_monthly_seasonality()
    build_silver_partner_drilldown()
    logger.info("=== Silver Transformation Pipeline Completed Successfully ===")


if __name__ == "__main__":
    run_all_silver_transforms()
