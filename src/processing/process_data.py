"""Processing and analytical transformation script for STATEC Hackathon 2026.
Reads raw extracted CSV tables from data/raw/, applies data cleansing,
computes rankings, KPIs, seasonal decomposition, and peer benchmarks,
and writes the processed tables directly as CSV in data/processed/.
No Parquet or JSON formats are used.

Design rules
------------
* Shares are always computed against the true flow totals derived from the complete
  HS2 table, never against the (possibly truncated) detailed tiers.
* Every table keeps its ``year`` column so the dashboard can honour the year selector.
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

from src.config import RAW_DIR, PROCESSED_DIR, START_YEAR, get_hs_section

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

AGGREGATE_PARTNER_CODES = {
    "WORLD", "INT_EU", "EXT_EU", "INT_EU27_2020", "EXT_EU27_2020",
    "INT_EA", "EXT_EA", "INT_EA21", "EXT_EA21"
}


# ── Shared helpers ─────────────────────────────────────────────────────────
def _read_raw(filename: str) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / filename, dtype={"product": str, "time": str}, keep_default_na=False, na_values=[""])


def _write(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / filename, index=False, encoding="utf-8")
    logger.info(f"Saved {filename}: {len(df):,} rows")
    return df


def _clean_partner_name(label_series: pd.Series) -> pd.Series:
    return label_series.apply(lambda s: str(s).split("(")[0].strip())


def _add_year_flow_value(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise the year / flow / value columns shared by every raw extract."""
    df["year"] = pd.to_numeric(df["time"].astype(str).str[:4], errors="coerce").astype("int16")
    df["flow"] = df["flow_label"].str.upper()
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def _rank_within(df: pd.DataFrame, group_cols, value_col: str = "value_eur") -> pd.Series:
    return df.groupby(group_cols)[value_col].rank(method="first", ascending=False).astype(int)


def _hs2_totals() -> pd.DataFrame:
    """Complete HS2 table (all chapters) with flow totals - the reference for shares."""
    df = _add_year_flow_value(_read_raw("hs2_products_annual_raw.csv"))
    df["hs2_code"] = df["product"].astype(str).str.zfill(2)
    df["value_eur"] = df["value_eur"].fillna(0.0)
    df["flow_total_eur"] = df.groupby(["year", "flow"])["value_eur"].transform("sum")
    return df[["year", "flow", "hs2_code", "value_eur", "flow_total_eur"]].rename(
        columns={"value_eur": "chapter_value_eur"}
    )


# ── Overview ───────────────────────────────────────────────────────────────
def process_overview_kpis() -> pd.DataFrame:
    """Compute annual macro KPIs from raw partners CSV."""
    logger.info("Processing overview KPIs from partners_annual_raw.csv")
    df = _add_year_flow_value(_read_raw("partners_annual_raw.csv"))

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

    return _write(pivoted, "overview_kpis.csv")


def process_partner_rankings() -> pd.DataFrame:
    """Compute partner rankings and market shares from raw partners CSV."""
    logger.info("Processing partner rankings from partners_annual_raw.csv")
    df = _add_year_flow_value(_read_raw("partners_annual_raw.csv"))
    df["partner_code"] = df["partner"]
    df["partner_name"] = _clean_partner_name(df["partner_label"])
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
    return _write(countries_df[cols].copy(), "partner_rankings.csv")


# ── Product tiers ──────────────────────────────────────────────────────────
def process_product_rankings() -> pd.DataFrame:
    """Compute HS2 product rankings, sections, and structural shifts from raw HS2 CSV."""
    logger.info("Processing product rankings from hs2_products_annual_raw.csv")
    df = _add_year_flow_value(_read_raw("hs2_products_annual_raw.csv"))
    df["hs2_code"] = df["product"].astype(str).str.zfill(2)
    df["hs2_name"] = df["product_label"]
    df["hs_section"] = df["hs2_code"].apply(get_hs_section)

    df["total_eur"] = df.groupby(["year", "flow"])["value_eur"].transform("sum")
    df["product_share_pct"] = (df["value_eur"] / df["total_eur"]) * 100

    df = df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    df["rank"] = df.groupby(["year", "flow"]).cumcount() + 1
    df["cumulative_share_pct"] = df.groupby(["year", "flow"])["product_share_pct"].cumsum()
    df["is_top_10"] = df["rank"] <= 10

    # Base year index (vectorised lookup of the first-year value per flow and chapter)
    base = (
        df[df["year"] == START_YEAR][["flow", "hs2_code", "value_eur"]]
        .rename(columns={"value_eur": "base_val"})
    )
    df = df.merge(base, on=["flow", "hs2_code"], how="left")
    df["index_2000"] = np.where(df["base_val"] > 0, (df["value_eur"] / df["base_val"]) * 100, np.nan)

    cols = ["year", "flow", "hs2_code", "hs2_name", "hs_section", "value_eur", "total_eur", "product_share_pct", "rank", "cumulative_share_pct", "is_top_10", "index_2000"]
    return _write(df[cols].copy(), "product_rankings.csv")


def _process_detailed_tier(raw_name: str, out_name: str, level: int) -> pd.DataFrame:
    """HS4 headings / CN8 tariff lines ranked per year and flow.

    ``total_eur`` and ``share_in_chapter_pct`` use the complete HS2 table as the
    denominator so truncated tiers (top-N CN8 lines) still report correct shares.
    """
    raw_path = RAW_DIR / raw_name
    if not raw_path.exists():
        logger.warning(f"{raw_name} not found, skipping {out_name}.")
        return pd.DataFrame()

    logger.info(f"Processing {level}-digit lines from {raw_name}")
    df = _add_year_flow_value(_read_raw(raw_name))
    code_col, name_col = f"hs{level}_code", f"hs{level}_name"
    df[code_col] = df["product"].astype(str).str.zfill(level)
    df[name_col] = df["product_label"]
    df["hs2_parent"] = df[code_col].str[:2]
    if level == 8:
        df["hs4_parent"] = df[code_col].str[:4]
    df["hs_section"] = df["hs2_parent"].apply(get_hs_section)
    df["value_eur"] = df["value_eur"].fillna(0.0)
    df = df[df["value_eur"] > 0].copy()

    ref = _hs2_totals()
    flow_totals = ref.drop_duplicates(["year", "flow"])[["year", "flow", "flow_total_eur"]]
    chapter_totals = ref[["year", "flow", "hs2_code", "chapter_value_eur"]].rename(columns={"hs2_code": "hs2_parent"})
    df = df.merge(flow_totals, on=["year", "flow"], how="left").merge(chapter_totals, on=["year", "flow", "hs2_parent"], how="left")
    df["total_eur"] = df["flow_total_eur"]
    df["product_share_pct"] = np.where(df["total_eur"] > 0, (df["value_eur"] / df["total_eur"]) * 100, 0.0)
    df["share_in_chapter_pct"] = np.where(df["chapter_value_eur"] > 0, (df["value_eur"] / df["chapter_value_eur"]) * 100, 0.0)

    df = df.sort_values(by=["year", "flow", "value_eur"], ascending=[True, True, False])
    df["overall_rank"] = df.groupby(["year", "flow"]).cumcount() + 1
    df["rank_in_chapter"] = df.groupby(["year", "flow", "hs2_parent"]).cumcount() + 1

    parents = ["hs2_parent", "hs4_parent"] if level == 8 else ["hs2_parent"]
    cols = ["year", "flow", code_col, name_col, *parents, "hs_section", "value_eur", "total_eur",
            "product_share_pct", "share_in_chapter_pct", "overall_rank", "rank_in_chapter"]
    return _write(df[cols].copy(), out_name)


def process_hs4_products() -> pd.DataFrame:
    """Compute 4-digit HS heading rankings and parent chapter contributions."""
    return _process_detailed_tier("hs4_products_annual_raw.csv", "hs4_product_rankings.csv", 4)


def process_hs8_products() -> pd.DataFrame:
    """Compute 8-digit CN tariff line rankings and parent chapter contributions."""
    return _process_detailed_tier("hs8_products_annual_raw.csv", "hs8_product_rankings.csv", 8)


# ── Seasonality ────────────────────────────────────────────────────────────
def process_seasonal_decomposition() -> pd.DataFrame:
    """Decompose monthly time-series into trend, seasonal factor, adjusted series, and residuals."""
    logger.info("Processing seasonal decomposition from monthly_seasonality_raw.csv")
    df = _read_raw("monthly_seasonality_raw.csv")

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
        # Detrended ratio (kept in the output so the dashboard can re-estimate factors per period)
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
    cols = ["date", "year", "month", "product_code", "product_name", "flow", "value_eur", "trend_eur",
            "ratio_to_trend", "seasonal_factor", "seasonally_adjusted_eur", "residual_eur"]
    return _write(res_df[cols].copy(), "seasonal_decomposition.csv")


# ── Peer benchmarks ────────────────────────────────────────────────────────
def process_country_benchmarks() -> pd.DataFrame:
    """Compute comparative trade metrics across Luxembourg and peer countries by product."""
    logger.info("Processing country benchmarks from country_benchmarks_annual_raw.csv")
    df = _read_raw("country_benchmarks_annual_raw.csv")

    df["year"] = pd.to_numeric(df["time"].astype(str).str[:4], errors="coerce").astype("int16")
    df["reporter_code"] = df["reporter"]
    df["reporter_name"] = _clean_partner_name(df["reporter_label"])
    df["product_code"] = df["product"].astype(str)
    df["product_name"] = df["product_label"].astype(str) if "product_label" in df.columns else df["product_code"]
    df["flow"] = df["flow_label"].str.upper()
    df["value_eur"] = pd.to_numeric(df["value"], errors="coerce").fillna(0.0)

    keys = ["year", "reporter_code", "reporter_name", "product_code", "product_name"]
    piv = df.pivot_table(index=keys, columns="flow", values="value_eur", aggfunc="sum").reset_index()
    piv.columns.name = None

    if "EXPORT" not in piv.columns:
        piv["EXPORT"] = 0.0
    if "IMPORT" not in piv.columns:
        piv["IMPORT"] = 0.0

    piv["trade_volume_eur"] = piv["EXPORT"] + piv["IMPORT"]
    piv["trade_balance_eur"] = piv["EXPORT"] - piv["IMPORT"]
    piv["coverage_ratio_pct"] = np.where(piv["IMPORT"] > 0, (piv["EXPORT"] / piv["IMPORT"]) * 100, np.nan)

    piv = piv.sort_values(["reporter_code", "product_code", "year"])
    pair = ["reporter_code", "product_code"]
    base = piv.loc[piv["year"] == START_YEAR, pair + ["EXPORT", "IMPORT", "trade_volume_eur"]].rename(
        columns={"EXPORT": "base_export", "IMPORT": "base_import", "trade_volume_eur": "base_volume"}
    )
    piv = piv.merge(base, on=pair, how="left")
    for col, base_col, out_col in [
        ("EXPORT", "base_export", "export_index_base"),
        ("IMPORT", "base_import", "import_index_base"),
        ("trade_volume_eur", "base_volume", "volume_index_base"),
    ]:
        piv[out_col] = np.where(piv[base_col] > 0, (piv[col] / piv[base_col]) * 100, np.nan)
    piv = piv.drop(columns=["base_export", "base_import", "base_volume"])

    return _write(piv, "country_benchmarks.csv")


# ── Partner x product tables ───────────────────────────────────────────────
def process_product_partners() -> pd.DataFrame:
    """Compute partner rankings and concentration metrics for each HS2 product category (Q3)."""
    raw_path = RAW_DIR / "product_partners_raw.csv"
    if not raw_path.exists():
        logger.warning(f"{raw_path.name} not found, skipping product partner processing.")
        return pd.DataFrame()

    logger.info(f"Processing product partners from {raw_path.name}")
    df = _add_year_flow_value(_read_raw("product_partners_raw.csv"))
    df["hs2_code"] = df["product"].astype(str).str.zfill(2)
    df["hs2_name"] = df["product_label"]
    df["hs_section"] = df["hs2_code"].apply(get_hs_section)
    df["partner_code"] = df["partner"]
    df["partner_name"] = _clean_partner_name(df["partner_label"])
    df["value_eur"] = df["value_eur"].fillna(0.0)

    # Exclude aggregate partner codes
    df = df[~df["partner_code"].isin(AGGREGATE_PARTNER_CODES)].copy()
    df = df[df["value_eur"] > 0].copy()

    keys = ["year", "flow", "hs2_code"]
    df["total_eur"] = df.groupby(keys)["value_eur"].transform("sum")
    df["partner_share_pct"] = np.where(df["total_eur"] > 0, (df["value_eur"] / df["total_eur"]) * 100, 0.0)

    # Sort and rank partners
    df = df.sort_values(by=keys + ["value_eur"], ascending=[True, True, True, False])
    df["rank"] = df.groupby(keys).cumcount() + 1
    df["cumulative_share_pct"] = df.groupby(keys)["partner_share_pct"].cumsum()

    # Herfindahl-Hirschman Index (HHI) for concentration (vectorised)
    df["_sq_share"] = df["partner_share_pct"] ** 2
    df["hhi"] = df.groupby(keys)["_sq_share"].transform("sum")
    df["concentration_level"] = np.where(
        df["hhi"] >= 2500, "High Concentration",
        np.where(df["hhi"] >= 1500, "Moderate Concentration", "Diversified")
    )

    cols = [
        "year", "flow", "hs2_code", "hs2_name", "hs_section",
        "partner_code", "partner_name", "value_eur", "total_eur",
        "partner_share_pct", "rank", "cumulative_share_pct",
        "hhi", "concentration_level"
    ]
    return _write(df[cols].copy(), "product_partners.csv")


def build_hs2_drilldown(pp_df: pd.DataFrame) -> pd.DataFrame:
    """HS2 tier of the partner drill-down, derived from the product-partner table.

    Works for *every* partner and year. ``share_pct`` is the chapter's share of the
    partner's complete flow in that year (sum of all HS2 chapters), so the Value and
    Share views of Figure 2.4 always describe the same year.
    """
    group = ["year", "partner_code", "flow"]
    lvl2 = pp_df.rename(columns={"hs2_code": "product_code", "hs2_name": "product_name"})[
        ["year", "partner_code", "partner_name", "flow", "product_code", "product_name", "hs_section", "value_eur"]
    ].copy()
    lvl2["code_level"] = 2
    lvl2["hs2_parent"] = lvl2["product_code"]
    lvl2["partner_flow_total_eur"] = lvl2.groupby(group)["value_eur"].transform("sum")
    lvl2["share_pct"] = np.where(
        lvl2["partner_flow_total_eur"] > 0, lvl2["value_eur"] / lvl2["partner_flow_total_eur"] * 100, 0.0
    )
    lvl2["chapter_share_pct"] = lvl2["share_pct"]
    lvl2["rank_in_partner"] = _rank_within(lvl2, group)
    lvl2["is_significant"] = lvl2["rank_in_partner"] <= 10
    return lvl2.sort_values(["year", "partner_code", "flow", "value_eur"], ascending=[True, True, True, False])


def process_partner_drilldown(pp_df: pd.DataFrame = None) -> pd.DataFrame:
    """Build the HS4 / CN8 drill-down tables used by Figure 2.4.

    * Levels 4 and 8 come from the key-partner extract (largest lines per year).
    * ``share_pct`` is the line's share of the partner's total flow in that year, taken
      from the complete HS2 sum of the product-partner table.
    * The HS2 tier is not persisted: see :func:`build_hs2_drilldown`.
    """
    if pp_df is None:
        pp_path = PROCESSED_DIR / "product_partners.csv"
        pp_df = pd.read_csv(pp_path, dtype={"hs2_code": str, "partner_code": str}, keep_default_na=False, na_values=[""]) if pp_path.exists() else pd.DataFrame()
    if pp_df.empty:
        logger.warning("No product-partner table available, skipping drilldown processing.")
        return pd.DataFrame()

    raw_path = RAW_DIR / "partner_drilldown_raw.csv"
    if not raw_path.exists():
        logger.warning(f"{raw_path.name} not found, skipping HS4/CN8 drilldown processing.")
        return pd.DataFrame()

    group = ["year", "partner_code", "flow"]
    totals = (
        pp_df.groupby(group)["value_eur"].sum().rename("partner_flow_total_eur").reset_index()
    )

    logger.info(f"Processing partner drilldown from {raw_path.name}")
    df = _add_year_flow_value(_read_raw("partner_drilldown_raw.csv"))
    df["partner_code"] = df["partner"]
    df["partner_name"] = _clean_partner_name(df["partner_label"])
    df["product_code"] = df["product"].astype(str)
    df["product_name"] = df["product_label"]
    df["code_level"] = df["product_code"].str.len().astype("int8")
    df["hs2_parent"] = df["product_code"].str[:2]
    df["hs4_parent"] = np.where(df["code_level"] >= 4, df["product_code"].str[:4], None)
    df["hs_section"] = df["hs2_parent"].apply(get_hs_section)
    df = df[df["value_eur"] > 0].merge(totals, on=group, how="left")
    df["share_pct"] = np.where(
        df["partner_flow_total_eur"] > 0, df["value_eur"] / df["partner_flow_total_eur"] * 100, np.nan
    )

    for level, name in [(4, "partner_drilldown_lvl4.csv"), (8, "partner_drilldown_lvl8.csv")]:
        tier = df[df["code_level"] == level].copy()
        tier["rank_in_partner"] = _rank_within(tier, group)
        tier = tier.sort_values(["year", "partner_code", "flow", "value_eur"], ascending=[True, True, True, False])
        _write(tier, name)

    return df


def run_all_processing():
    """Run full processing pipeline generating processed CSV files."""
    logger.info("=== Starting Processing Pipeline (Raw CSV -> Processed CSV) ===")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    process_overview_kpis()
    process_partner_rankings()
    process_product_rankings()
    process_seasonal_decomposition()
    process_country_benchmarks()
    pp = process_product_partners()      # must run before the drill-down (HS2 tier)
    process_partner_drilldown(pp)
    process_hs4_products()
    process_hs8_products()
    logger.info("=== Tabular CSV Processing Completed Successfully ===")


if __name__ == "__main__":
    run_all_processing()
