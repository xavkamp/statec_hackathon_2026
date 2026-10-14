"""Processing and analytical transformation script for STATEC Hackathon 2026.
Reads raw extracted CSV tables from data/raw/, applies data cleansing,
computes rankings, KPIs, seasonal decomposition, and peer benchmarks,
and writes the processed tables directly as CSV in data/processed/.
No Parquet or JSON formats are used.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import RAW_DIR, PROCESSED_DIR, get_hs_section

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

AGGREGATE_PARTNER_CODES = {
    "WORLD", "INT_EU", "EXT_EU", "INT_EU27_2020", "EXT_EU27_2020",
    "INT_EA", "EXT_EA", "INT_EA21", "EXT_EA21"
}


def process_overview_kpis() -> pd.DataFrame:
    """Compute annual macro KPIs from raw partners CSV."""
    raw_path = RAW_DIR / "partners_annual_raw.csv"
    logger.info(f"Processing overview KPIs from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")

    # Filter for WORLD total trade
    world_df = df[df["partner"] == "WORLD"].copy()
    pivoted = world_df.pivot_table(index="year", columns="flow", values="value_eur", aggfunc="sum").reset_index()
    pivoted.columns.name = None

    if "EXPORT" not in pivoted.columns:
        pivoted["EXPORT"] = 0.0
    if "IMPORT" not in pivoted.columns:
        pivoted["IMPORT"] = 0.0

    pivoted["trade_volume_eur"] = pivoted["EXPORT"] + pivoted["IMPORT"]
    pivoted["trade_balance_eur"] = pivoted["EXPORT"] - pivoted["IMPORT"]
    pivoted["coverage_ratio_pct"] = np.where(pivoted["IMPORT"] > 0, (pivoted["EXPORT"] / pivoted["IMPORT"]) * 100, np.nan)

    pivoted = pivoted.sort_values("year")
    pivoted["export_yoy_growth_pct"] = pivoted["EXPORT"].pct_change() * 100
    pivoted["import_yoy_growth_pct"] = pivoted["IMPORT"].pct_change() * 100
    pivoted["volume_yoy_growth_pct"] = pivoted["trade_volume_eur"].pct_change() * 100

    # Intra-EU share: use INT_EU27_2020 preferentially; fall back to INT_EU when INT_EU27_2020 is absent
    eu27_df = df[df["partner"] == "INT_EU27_2020"].copy()
    eu_old_df = df[df["partner"] == "INT_EU"].copy()
    # Combine: prefer INT_EU27_2020; use INT_EU for years missing from INT_EU27_2020
    eu27_years = set(eu27_df["year"].unique()) if not eu27_df.empty else set()
    eu_old_fill = eu_old_df[~eu_old_df["year"].isin(eu27_years)].copy() if not eu_old_df.empty else pd.DataFrame()
    eu_df = pd.concat([eu27_df, eu_old_fill], ignore_index=True)
    if not eu_df.empty:
        eu_piv = eu_df.pivot_table(index="year", columns="flow", values="value_eur", aggfunc="sum").reset_index()
        eu_piv.columns.name = None
        eu_piv = eu_piv.rename(columns={"EXPORT": "EXPORT_eu", "IMPORT": "IMPORT_eu"})
        pivoted = pivoted.merge(eu_piv, on="year", how="left")
        pivoted["intra_eu_export_share_pct"] = np.where(
            pivoted["EXPORT"] > 0, (pivoted["EXPORT_eu"] / pivoted["EXPORT"]) * 100, np.nan
        )
        pivoted["intra_eu_import_share_pct"] = np.where(
            pivoted["IMPORT"] > 0, (pivoted["IMPORT_eu"] / pivoted["IMPORT"]) * 100, np.nan
        )
        pivoted = pivoted.drop(columns=["EXPORT_eu", "IMPORT_eu"], errors="ignore")

    out_file = PROCESSED_DIR / "overview_kpis.csv"
    pivoted.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(pivoted)} rows")
    return pivoted


def process_partner_rankings() -> pd.DataFrame:
    """Compute partner rankings and market shares from raw partners CSV."""
    raw_path = RAW_DIR / "partners_annual_raw.csv"
    logger.info(f"Processing partner rankings from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["partner_code"] = df["partner"]
    df["partner_name"] = df["partner_label"].apply(lambda s: str(s).split("(")[0].strip())
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")
    df["is_aggregate"] = df["partner_code"].isin(AGGREGATE_PARTNER_CODES)

    countries_df = df[~df["is_aggregate"]].copy()
    totals = countries_df.groupby(["year", "flow"])["value_eur"].transform("sum")
    countries_df["total_eur"] = totals
    countries_df["market_share_pct"] = (countries_df["value_eur"] / countries_df["total_eur"]) * 100

    countries_df = countries_df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    countries_df["rank"] = countries_df.groupby(["year", "flow"]).cumcount() + 1
    countries_df["cumulative_share_pct"] = countries_df.groupby(["year", "flow"])["market_share_pct"].cumsum()
    countries_df["is_top_10"] = countries_df["rank"] <= 10

    cols = ["year", "flow", "partner_code", "partner_name", "value_eur", "total_eur", "market_share_pct", "rank", "cumulative_share_pct", "is_top_10"]
    res = countries_df[cols].copy()

    out_file = PROCESSED_DIR / "partner_rankings.csv"
    res.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(res):,} rows")
    return res


def process_product_rankings() -> pd.DataFrame:
    """Compute HS2 product rankings, sections, and structural shifts from raw HS2 CSV."""
    raw_path = RAW_DIR / "hs2_products_annual_raw.csv"
    logger.info(f"Processing product rankings from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["hs2_code"] = df["product"].astype(str).str.zfill(2)
    df["hs2_name"] = df["product_label"]
    df["hs_section"] = df["hs2_code"].apply(get_hs_section)
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")

    totals = df.groupby(["year", "flow"])["value_eur"].transform("sum")
    df["total_eur"] = totals
    df["product_share_pct"] = (df["value_eur"] / df["total_eur"]) * 100

    df = df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    df["rank"] = df.groupby(["year", "flow"]).cumcount() + 1
    df["cumulative_share_pct"] = df.groupby(["year", "flow"])["product_share_pct"].cumsum()
    df["is_top_10"] = df["rank"] <= 10

    # Base year 2000 index
    base_2000 = df[df["year"] == 2000].set_index(["flow", "hs2_code"])["value_eur"].to_dict()
    df["base_2000_val"] = df.apply(lambda r: base_2000.get((r["flow"], r["hs2_code"]), np.nan), axis=1)
    df["index_2000"] = np.where(df["base_2000_val"] > 0, (df["value_eur"] / df["base_2000_val"]) * 100, np.nan)
    df = df.drop(columns=["base_2000_val"])

    cols = ["year", "flow", "hs2_code", "hs2_name", "hs_section", "value_eur", "total_eur", "product_share_pct", "rank", "cumulative_share_pct", "is_top_10", "index_2000"]
    res = df[cols].copy()

    out_file = PROCESSED_DIR / "product_rankings.csv"
    res.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(res):,} rows")
    return res


def process_seasonal_decomposition() -> pd.DataFrame:
    """Decompose monthly time-series into trend, seasonal factor, adjusted series, and residuals."""
    raw_path = RAW_DIR / "monthly_seasonality_raw.csv"
    logger.info(f"Processing seasonal decomposition from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["time_str"] = df["time"].astype(str)
    parts = df["time_str"].str.split("-", expand=True)
    df["year"] = pd.to_numeric(parts[0], errors="coerce").astype("int16")
    df["month"] = pd.to_numeric(parts[1], errors="coerce").astype("int8")
    df["date"] = df["time_str"] + "-01"
    df["flow"] = df["flow_label"].str.upper()
    df["product_code"] = df["product"]
    df["product_name"] = df["product_label"]
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")

    results = []
    for (prod_code, flow), group in df.groupby(["product_code", "flow"]):
        g = group.sort_values("date").copy()

        # 12-month centered rolling moving average for trend
        g["trend_eur"] = g["value_eur"].rolling(window=12, center=True, min_periods=6).mean()
        # Detrended ratio
        g["ratio_to_trend"] = np.where(g["trend_eur"] > 0, g["value_eur"] / g["trend_eur"], np.nan)
        # Monthly factor (median of ratio for that calendar month)
        monthly_factors = g.groupby("month")["ratio_to_trend"].transform("median")
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
    cols = ["date", "year", "month", "product_code", "product_name", "flow", "value_eur", "trend_eur", "seasonal_factor", "seasonally_adjusted_eur", "residual_eur"]
    res = res_df[cols].copy()

    out_file = PROCESSED_DIR / "seasonal_decomposition.csv"
    res.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(res):,} rows")
    return res


def process_country_benchmarks() -> pd.DataFrame:
    """Compute comparative trade metrics across Luxembourg and peer countries."""
    raw_path = RAW_DIR / "country_benchmarks_annual_raw.csv"
    logger.info(f"Processing country benchmarks from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["reporter_code"] = df["reporter"]
    df["reporter_name"] = df["reporter_label"].apply(lambda s: str(s).split("(")[0].strip())
    df["flow"] = df["flow_label"].str.upper()
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")

    piv = df.pivot_table(
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

    piv = piv.sort_values(["reporter_code", "year"])
    base_years = piv[piv["year"] == 2000].set_index("reporter_code")
    base_export = base_years["EXPORT"].to_dict()
    base_import = base_years["IMPORT"].to_dict()
    base_volume = base_years["trade_volume_eur"].to_dict()

    piv["export_index_2000"] = piv.apply(lambda r: (r["EXPORT"] / base_export[r["reporter_code"]]) * 100 if base_export.get(r["reporter_code"], 0) > 0 else np.nan, axis=1)
    piv["import_index_2000"] = piv.apply(lambda r: (r["IMPORT"] / base_import[r["reporter_code"]]) * 100 if base_import.get(r["reporter_code"], 0) > 0 else np.nan, axis=1)
    piv["volume_index_2000"] = piv.apply(lambda r: (r["trade_volume_eur"] / base_volume[r["reporter_code"]]) * 100 if base_volume.get(r["reporter_code"], 0) > 0 else np.nan, axis=1)

    out_file = PROCESSED_DIR / "country_benchmarks.csv"
    piv.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(piv)} rows")
    return piv


def process_partner_drilldown() -> pd.DataFrame:
    """Pre-aggregate partner drilldown data across 2-digit, 4-digit, and 8-digit CN8 codes."""
    raw_path = RAW_DIR / "partner_drilldown_raw.csv"
    logger.info(f"Processing partner drilldown from {raw_path.name}")
    if not raw_path.exists():
        logger.warning(f"{raw_path.name} not found, skipping drilldown processing.")
        return pd.DataFrame()

    df = pd.read_csv(raw_path)
    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["partner_code"] = df["partner"]
    df["partner_name"] = df["partner_label"].apply(lambda s: str(s).split("(")[0].strip())
    df["flow"] = df["flow_label"].str.upper()
    df["product_code"] = df["product"].astype(str)
    df["product_name"] = df["product_label"]
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")

    df["code_level"] = df["product_code"].str.len().astype("int8")
    df["hs2_parent"] = df["product_code"].str[:2]
    df["hs4_parent"] = np.where(df["code_level"] >= 4, df["product_code"].str[:4], None)
    df["hs6_parent"] = np.where(df["code_level"] >= 6, df["product_code"].str[:6], None)
    df["hs_section"] = df["hs2_parent"].apply(get_hs_section)

    lvl2 = df[df["code_level"] == 2].copy()
    lvl4 = df[df["code_level"] == 4].copy()
    lvl8 = df[df["code_level"] == 8].copy()

    # Calculate level 2 share
    tot = lvl2.groupby(["partner_code", "flow"])["value_eur"].transform("sum")
    lvl2["chapter_share_pct"] = (lvl2["value_eur"] / tot) * 100
    lvl2 = lvl2.sort_values(by=["partner_code", "flow", "value_eur"], ascending=[True, True, False])
    lvl2["rank_in_partner"] = lvl2.groupby(["partner_code", "flow"]).cumcount() + 1
    lvl2["is_significant"] = lvl2["rank_in_partner"] <= 10

    out_lvl2 = PROCESSED_DIR / "partner_drilldown_lvl2.csv"
    lvl2.to_csv(out_lvl2, index=False, encoding="utf-8")
    logger.info(f"Saved {out_lvl2.name}: {len(lvl2):,} rows")

    out_lvl4 = PROCESSED_DIR / "partner_drilldown_lvl4.csv"
    lvl4.to_csv(out_lvl4, index=False, encoding="utf-8")
    logger.info(f"Saved {out_lvl4.name}: {len(lvl4):,} rows")

    # Keep top 100 CN8 lines per partner and flow for fast UI rendering
    lvl8 = lvl8.sort_values(by=["partner_code", "flow", "value_eur"], ascending=[True, True, False])
    top_lvl8 = lvl8.groupby(["partner_code", "flow"]).head(100).copy()
    out_lvl8 = PROCESSED_DIR / "partner_drilldown_lvl8.csv"
    top_lvl8.to_csv(out_lvl8, index=False, encoding="utf-8")
    logger.info(f"Saved {out_lvl8.name}: {len(top_lvl8):,} rows")

    return lvl2


def process_product_partners() -> pd.DataFrame:
    """Compute partner rankings and concentration metrics for each HS2 product category (Q3)."""
    raw_path = RAW_DIR / "product_partners_raw.csv"
    if not raw_path.exists():
        logger.warning(f"{raw_path.name} not found, skipping product partner processing.")
        return pd.DataFrame()

    logger.info(f"Processing product partners from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["hs2_code"] = df["product"].astype(str).str.zfill(2)
    df["hs2_name"] = df["product_label"]
    df["hs_section"] = df["hs2_code"].apply(get_hs_section)
    df["partner_code"] = df["partner"]
    df["partner_name"] = df["partner_label"].apply(lambda s: str(s).split("(")[0].strip())
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce").fillna(0.0)

    # Exclude aggregate partner codes
    df = df[~df["partner_code"].isin(AGGREGATE_PARTNER_CODES)].copy()
    df = df[df["value_eur"] > 0].copy()

    # Total trade per product, year, flow
    totals = df.groupby(["year", "flow", "hs2_code"])["value_eur"].transform("sum")
    df["total_eur"] = totals
    df["partner_share_pct"] = np.where(df["total_eur"] > 0, (df["value_eur"] / df["total_eur"]) * 100, 0.0)

    # Sort and rank partners
    df = df.sort_values(by=["year", "flow", "hs2_code", "value_eur"], ascending=[True, True, True, False])
    df["rank"] = df.groupby(["year", "flow", "hs2_code"]).cumcount() + 1
    df["cumulative_share_pct"] = df.groupby(["year", "flow", "hs2_code"])["partner_share_pct"].cumsum()

    # Herfindahl-Hirschman Index (HHI) for concentration
    hhi_df = df.groupby(["year", "flow", "hs2_code"])["partner_share_pct"].apply(lambda s: (s ** 2).sum()).reset_index()
    hhi_df = hhi_df.rename(columns={"partner_share_pct": "hhi"})
    hhi_df["concentration_level"] = np.where(
        hhi_df["hhi"] >= 2500, "High Concentration",
        np.where(hhi_df["hhi"] >= 1500, "Moderate Concentration", "Diversified")
    )

    df = df.merge(hhi_df, on=["year", "flow", "hs2_code"], how="left")

    cols = [
        "year", "flow", "hs2_code", "hs2_name", "hs_section",
        "partner_code", "partner_name", "value_eur", "total_eur",
        "partner_share_pct", "rank", "cumulative_share_pct",
        "hhi", "concentration_level"
    ]
    res = df[cols].copy()

    out_file = PROCESSED_DIR / "product_partners.csv"
    res.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(res):,} rows")
    return res


def process_hs4_products() -> pd.DataFrame:
    """Compute 4-digit HS subheading rankings and parent chapter contributions."""
    raw_path = RAW_DIR / "hs4_products_annual_raw.csv"
    if not raw_path.exists():
        logger.warning(f"{raw_path.name} not found, skipping HS4 processing.")
        return pd.DataFrame()

    logger.info(f"Processing 4-digit HS subheadings from {raw_path.name}")
    df = pd.read_csv(raw_path)

    df["year"] = pd.to_numeric(df["time"], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["hs4_code"] = df["product"].astype(str).str.zfill(4)
    df["hs4_name"] = df["product_label"]
    df["hs2_parent"] = df["hs4_code"].str[:2]
    df["hs_section"] = df["hs2_parent"].apply(get_hs_section)
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce").fillna(0.0)

    # Filter positive trade values
    df = df[df["value_eur"] > 0].copy()

    # Total trade per year and flow
    totals = df.groupby(["year", "flow"])["value_eur"].transform("sum")
    df["total_eur"] = totals
    df["product_share_pct"] = np.where(df["total_eur"] > 0, (df["value_eur"] / df["total_eur"]) * 100, 0.0)

    # Contribution within parent 2-digit chapter
    ch_totals = df.groupby(["year", "flow", "hs2_parent"])["value_eur"].transform("sum")
    df["share_in_chapter_pct"] = np.where(ch_totals > 0, (df["value_eur"] / ch_totals) * 100, 0.0)

    # Overall rank and rank within chapter
    df = df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    df["overall_rank"] = df.groupby(["year", "flow"]).cumcount() + 1
    df["rank_in_chapter"] = df.groupby(["year", "flow", "hs2_parent"]).cumcount() + 1

    cols = [
        "year", "flow", "hs4_code", "hs4_name", "hs2_parent", "hs_section",
        "value_eur", "total_eur", "product_share_pct", "share_in_chapter_pct",
        "overall_rank", "rank_in_chapter"
    ]
    res = df[cols].copy()

    out_file = PROCESSED_DIR / "hs4_product_rankings.csv"
    res.to_csv(out_file, index=False, encoding="utf-8")
    logger.info(f"Saved {out_file.name}: {len(res):,} rows")
    return res


def run_all_processing():
    """Run full processing pipeline generating processed CSV files."""
    logger.info("=== Starting Processing Pipeline (Raw CSV -> Processed CSV) ===")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    process_overview_kpis()
    process_partner_rankings()
    process_product_rankings()
    process_seasonal_decomposition()
    process_country_benchmarks()
    process_partner_drilldown()
    process_product_partners()
    process_hs4_products()
    logger.info("=== Tabular CSV Processing Completed Successfully ===")


if __name__ == "__main__":
    run_all_processing()


