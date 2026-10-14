"""Gold Layer transformation and analytical modeling script.
Computes business metrics, KPI aggregates, ranking tables,
time-series seasonal decomposition, and peer benchmarks.
Outputs ready-to-serve Parquet tables in data/gold/.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Ensure project root is in path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import SILVER_DIR, GOLD_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_gold_overview_kpis() -> pd.DataFrame:
    """Build high-level annual KPIs for Luxembourg trade (2000-2026)."""
    logger.info("Building gold_overview_kpis...")
    partners_df = pd.read_parquet(SILVER_DIR / "silver_partners_annual.parquet")

    # Aggregate totals from WORLD partner
    world_df = partners_df[partners_df["partner_code"] == "WORLD"].copy()
    pivoted = world_df.pivot_table(index="year", columns="flow", values="value_eur", aggfunc="sum").reset_index()
    pivoted.columns.name = None

    if "EXPORT" not in pivoted.columns:
        pivoted["EXPORT"] = 0.0
    if "IMPORT" not in pivoted.columns:
        pivoted["IMPORT"] = 0.0

    pivoted["trade_volume_eur"] = pivoted["EXPORT"] + pivoted["IMPORT"]
    pivoted["trade_balance_eur"] = pivoted["EXPORT"] - pivoted["IMPORT"]
    pivoted["coverage_ratio_pct"] = np.where(pivoted["IMPORT"] > 0, (pivoted["EXPORT"] / pivoted["IMPORT"]) * 100, np.nan)

    # YoY growth
    pivoted = pivoted.sort_values("year")
    pivoted["export_yoy_growth_pct"] = pivoted["EXPORT"].pct_change() * 100
    pivoted["import_yoy_growth_pct"] = pivoted["IMPORT"].pct_change() * 100
    pivoted["volume_yoy_growth_pct"] = pivoted["trade_volume_eur"].pct_change() * 100

    # Intra-EU vs Extra-EU share
    eu_df = partners_df[partners_df["partner_code"].isin(["INT_EU27_2020", "INT_EU"])].copy()
    if not eu_df.empty:
        eu_piv = eu_df.pivot_table(index="year", columns="flow", values="value_eur", aggfunc="sum").reset_index()
        pivoted = pivoted.merge(eu_piv, on="year", how="left", suffixes=("", "_eu"))
        pivoted["intra_eu_export_share_pct"] = np.where(pivoted["EXPORT"] > 0, (pivoted["EXPORT_eu"] / pivoted["EXPORT"]) * 100, np.nan)
        pivoted["intra_eu_import_share_pct"] = np.where(pivoted["IMPORT"] > 0, (pivoted["IMPORT_eu"] / pivoted["IMPORT"]) * 100, np.nan)
        pivoted = pivoted.drop(columns=[c for c in pivoted.columns if c.endswith("_eu")])

    output_path = GOLD_DIR / "gold_overview_kpis.parquet"
    pivoted.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(pivoted)} rows")
    return pivoted


def build_gold_partner_rankings() -> pd.DataFrame:
    """Build partner rankings, market shares, and cumulative distributions."""
    logger.info("Building gold_partner_rankings...")
    partners_df = pd.read_parquet(SILVER_DIR / "silver_partners_annual.parquet")

    # Exclude aggregate groupings to get pure countries
    countries_df = partners_df[~partners_df["is_aggregate"]].copy()

    # Calculate total per year and flow
    totals = countries_df.groupby(["year", "flow"])["value_eur"].transform("sum")
    countries_df["total_eur"] = totals
    countries_df["market_share_pct"] = (countries_df["value_eur"] / countries_df["total_eur"]) * 100

    # Rank partners per year and flow
    countries_df = countries_df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    countries_df["rank"] = countries_df.groupby(["year", "flow"]).cumcount() + 1
    countries_df["cumulative_share_pct"] = countries_df.groupby(["year", "flow"])["market_share_pct"].cumsum()
    countries_df["is_top_10"] = countries_df["rank"] <= 10

    output_path = GOLD_DIR / "gold_partner_rankings.parquet"
    countries_df.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(countries_df)} rows")
    return countries_df


def build_gold_product_rankings() -> pd.DataFrame:
    """Build HS2 product rankings, section shares, and historical structural shifts."""
    logger.info("Building gold_product_rankings...")
    hs2_df = pd.read_parquet(SILVER_DIR / "silver_hs2_products_annual.parquet")

    # Calculate annual total per flow
    totals = hs2_df.groupby(["year", "flow"])["value_eur"].transform("sum")
    hs2_df["total_eur"] = totals
    hs2_df["product_share_pct"] = (hs2_df["value_eur"] / hs2_df["total_eur"]) * 100

    # Rank products per year and flow
    hs2_df = hs2_df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    hs2_df["rank"] = hs2_df.groupby(["year", "flow"]).cumcount() + 1
    hs2_df["cumulative_share_pct"] = hs2_df.groupby(["year", "flow"])["product_share_pct"].cumsum()
    hs2_df["is_top_10"] = hs2_df["rank"] <= 10

    # Historical growth index (2000 = 100)
    base_2000 = hs2_df[hs2_df["year"] == 2000].set_index(["flow", "hs2_code"])["value_eur"].to_dict()
    hs2_df["base_2000_val"] = hs2_df.apply(lambda r: base_2000.get((r["flow"], r["hs2_code"]), np.nan), axis=1)
    hs2_df["index_2000"] = np.where(hs2_df["base_2000_val"] > 0, (hs2_df["value_eur"] / hs2_df["base_2000_val"]) * 100, np.nan)
    hs2_df = hs2_df.drop(columns=["base_2000_val"])

    output_path = GOLD_DIR / "gold_product_rankings.parquet"
    hs2_df.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(hs2_df)} rows")
    return hs2_df


def build_gold_seasonal_decomposition() -> pd.DataFrame:
    """Perform time-series seasonal decomposition and compute seasonally adjusted series."""
    logger.info("Building gold_seasonal_decomposition...")
    monthly_df = pd.read_parquet(SILVER_DIR / "silver_monthly_seasonality.parquet")

    results = []
    # Group by product and flow
    for (prod_code, flow), group in monthly_df.groupby(["product_code", "flow"]):
        g = group.sort_values("date").copy()
        prod_name = g["product_name"].iloc[0]

        # 12-month centered rolling moving average for trend
        g["trend_eur"] = g["value_eur"].rolling(window=12, center=True, min_periods=6).mean()

        # Detrended ratio (multiplicative model)
        g["ratio_to_trend"] = np.where(g["trend_eur"] > 0, g["value_eur"] / g["trend_eur"], np.nan)

        # Monthly seasonal factor (average ratio for each month 1-12 across all years)
        monthly_factors = g.groupby("month")["ratio_to_trend"].transform("median")
        # Normalize factors so mean factor across 12 months is 1.0
        avg_factor = monthly_factors.mean()
        if avg_factor > 0:
            monthly_factors = monthly_factors / avg_factor
        g["seasonal_factor"] = monthly_factors

        # Seasonally adjusted series
        g["seasonally_adjusted_eur"] = np.where(g["seasonal_factor"] > 0, g["value_eur"] / g["seasonal_factor"], g["value_eur"])
        # Residual
        g["residual_eur"] = g["value_eur"] - (g["trend_eur"] * g["seasonal_factor"])

        results.append(g)

    res_df = pd.concat(results, ignore_index=True)
    output_path = GOLD_DIR / "gold_seasonal_decomposition.parquet"
    res_df.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(res_df)} rows")
    return res_df


def build_gold_country_benchmarks() -> pd.DataFrame:
    """Compute benchmark comparison metrics across Luxembourg and peer nations."""
    logger.info("Building gold_country_benchmarks...")
    bench_df = pd.read_parquet(SILVER_DIR / "silver_country_benchmarks.parquet")

    # Pivot imports and exports
    piv = bench_df.pivot_table(
        index=["year", "reporter_code", "reporter_name"],
        columns="flow",
        values="value_eur",
        aggfunc="sum"
    ).reset_index()
    piv.columns.name = None

    if "EXPORT" not in piv.columns:
        piv["EXPORT"] = 0.0
    if "IMPORT" not in piv.columns:
        piv["IMPORT"] = 0.0

    piv["trade_volume_eur"] = piv["EXPORT"] + piv["IMPORT"]
    piv["trade_balance_eur"] = piv["EXPORT"] - piv["IMPORT"]
    piv["coverage_ratio_pct"] = np.where(piv["IMPORT"] > 0, (piv["EXPORT"] / piv["IMPORT"]) * 100, np.nan)

    # Base year 2000 indexed growth (Index 2000 = 100)
    piv = piv.sort_values(["reporter_code", "year"])
    base_years = piv[piv["year"] == 2000].set_index("reporter_code")
    base_export = base_years["EXPORT"].to_dict()
    base_import = base_years["IMPORT"].to_dict()
    base_volume = base_years["trade_volume_eur"].to_dict()

    piv["export_index_2000"] = piv.apply(lambda r: (r["EXPORT"] / base_export[r["reporter_code"]]) * 100 if base_export.get(r["reporter_code"], 0) > 0 else np.nan, axis=1)
    piv["import_index_2000"] = piv.apply(lambda r: (r["IMPORT"] / base_import[r["reporter_code"]]) * 100 if base_import.get(r["reporter_code"], 0) > 0 else np.nan, axis=1)
    piv["volume_index_2000"] = piv.apply(lambda r: (r["trade_volume_eur"] / base_volume[r["reporter_code"]]) * 100 if base_volume.get(r["reporter_code"], 0) > 0 else np.nan, axis=1)

    output_path = GOLD_DIR / "gold_country_benchmarks.parquet"
    piv.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(piv)} rows")
    return piv


def build_gold_partner_drilldown_summary() -> pd.DataFrame:
    """Pre-aggregate partner drilldown data to provide fast, uncluttered hierarchical exploration."""
    logger.info("Building gold_partner_drilldown_summary...")
    drill_file = SILVER_DIR / "silver_partner_drilldown.parquet"
    if not drill_file.exists():
        logger.warning("silver_partner_drilldown.parquet not found, skipping.")
        return pd.DataFrame()

    df = pd.read_parquet(drill_file)

    # Separate into levels
    lvl2 = df[df["code_level"] == 2].copy()
    lvl4 = df[df["code_level"] == 4].copy()
    lvl8 = df[df["code_level"] == 8].copy()

    # Calculate total per partner and flow at level 2
    tot = lvl2.groupby(["partner_code", "flow"])["value_eur"].transform("sum")
    lvl2["chapter_share_pct"] = (lvl2["value_eur"] / tot) * 100

    # Tag top significance
    lvl2 = lvl2.sort_values(by=["partner_code", "flow", "value_eur"], ascending=[True, True, False])
    lvl2["rank_in_partner"] = lvl2.groupby(["partner_code", "flow"]).cumcount() + 1
    lvl2["is_significant"] = lvl2["rank_in_partner"] <= 10

    # Save summary level 2 & 4
    output_path = GOLD_DIR / "gold_partner_drilldown_lvl2.parquet"
    lvl2.to_parquet(output_path, index=False)
    logger.info(f"Saved {output_path.name}: {len(lvl2)} rows")

    output_path_lvl4 = GOLD_DIR / "gold_partner_drilldown_lvl4.parquet"
    lvl4.to_parquet(output_path_lvl4, index=False)
    logger.info(f"Saved {output_path_lvl4.name}: {len(lvl4)} rows")

    output_path_lvl8 = GOLD_DIR / "gold_partner_drilldown_lvl8.parquet"
    # Keep top 100 CN8 lines per partner and flow to ensure fast UI rendering
    lvl8 = lvl8.sort_values(by=["partner_code", "flow", "value_eur"], ascending=[True, True, False])
    top_lvl8 = lvl8.groupby(["partner_code", "flow"]).head(100).copy()
    top_lvl8.to_parquet(output_path_lvl8, index=False)
    logger.info(f"Saved {output_path_lvl8.name}: {len(top_lvl8)} rows")

    return lvl2


def run_all_gold_transforms():
    """Run all Gold analytical transformations."""
    logger.info("=== Starting Gold Transformation Pipeline ===")
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    build_gold_overview_kpis()
    build_gold_partner_rankings()
    build_gold_product_rankings()
    build_gold_seasonal_decomposition()
    build_gold_country_benchmarks()
    build_gold_partner_drilldown_summary()
    logger.info("=== Gold Transformation Pipeline Completed Successfully ===")


if __name__ == "__main__":
    run_all_gold_transforms()
