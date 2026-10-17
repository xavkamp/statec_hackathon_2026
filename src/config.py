"""Configuration constants for STATEC Hackathon 2026 - Luxembourg External Trade.
Dataset: Eurostat ds-045409 (EU trade since 1988 by HS2-4-6 and CN8)
Format: Tabular CSV

EVERY tunable setting of the project lives in this file (analysis years, reporter and
partner countries, product coverage, baskets, API tuning, dashboard defaults).
After changing coverage settings re-run:  python run_pipeline.py --ingest --process
(ingestion re-downloads automatically when the cached files don't cover the new settings).
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Eurostat Comext API
COMEXT_API_URL = "https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/ds-045409"

# Time span of the analysis (inclusive). Drives ingestion, processing and every dashboard
# year selector / title.
START_YEAR = 2000
END_YEAR = 2025
YEARS = [str(y) for y in range(START_YEAR, END_YEAR + 1)]

# Reporters: the country the dashboard is about, and the peers it is benchmarked against
# (Tab 4). The primary reporter should be part of PEER_REPORTERS.
PRIMARY_REPORTER = "LU"
PEER_REPORTERS = ["LU", "BE", "DE", "FR", "NL"]

# ── Partner country groups used by the dashboard (ISO-2 codes) ──
EU27_CODES = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR", "HU",
    "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
}
NEIGHBOUR_CODES = {"BE", "DE", "FR"}      # "Direct neighbours" of the primary reporter
TRANSIT_HUB_CODES = {"BE", "NL"}          # Logistics hubs (Antwerp / Rotterdam)

# Fallback partner list for the drill-down dropdown when no ranking data is available
DEFAULT_PARTNER_OPTIONS = ["DE", "BE", "FR", "NL", "US", "CN", "IT", "GB", "PL", "CH", "ES", "JP", "CZ", "TR", "AT"]
DEFAULT_DRILLDOWN_PARTNER = "DE"

# Parallel HTTP workers used by the ingestion step (lower if Eurostat throttles you)
MAX_WORKERS = 4

# Flow mapping
FLOWS = {
    "1": "IMPORT",
    "2": "EXPORT",
}

# Indicators
INDICATOR_VALUE = "VALUE_IN_EUROS"
INDICATOR_QUANTITY = "QUANTITY_IN_100KG"

# Key HS2 chapters (01 to 99)
ALL_HS2_CHAPTERS = [f"{i:02d}" for i in range(1, 100)]

# ── Data coverage settings (shared by ingestion, processing and dashboard) ──
# Products fetched for the monthly seasonality and peer-benchmark tables. Every HS2
# chapter is included so that every critical basket (and the non-critical remainder)
# has a complete list of selectable product sectors.
SEASONAL_PRODUCTS = ["TOTAL"] + ALL_HS2_CHAPTERS
BENCHMARK_PRODUCTS = ["TOTAL"] + ALL_HS2_CHAPTERS

# Curated dropdown labels for the peer-benchmark tab (Tab 4), in display order. Any chapter in
# BENCHMARK_PRODUCTS without an entry here is appended automatically using the name from the data.
BENCHMARK_PRODUCT_LABELS = {
    "TOTAL": "All Merchandise Trade (Total)",
    "87": "87 — Vehicles & Automotive Equipment",
    "84": "84 — Machinery & Mechanical Appliances",
    "85": "85 — Electrical Machinery & Electronics",
    "30": "30 — Pharmaceutical Products",
    "72": "72 — Iron and Steel",
    "73": "73 — Articles of Iron or Steel",
    "27": "27 — Mineral Fuels & Energy",
    "39": "39 — Plastics and Articles Thereof",
    "90": "90 — Optical, Medical & Precision Instruments",
    "04": "04 — Dairy Produce, Honey & Edible Products",
    "22": "22 — Beverages, Spirits and Vinegar",
    "10": "10 — Cereals and Grains",
    "76": "76 — Aluminium and Articles Thereof",
    "40": "40 — Rubber and Articles Thereof",
    "94": "94 — Furniture & Lighting",
    "25": "25 — Salt, Stone, Plaster & Cement",
    "48": "48 — Paper and Paperboard",
    "62": "62 — Apparel & Clothing Accessories",
    "88": "88 — Aircraft, Spacecraft & Parts",
}

# Partners that get a hierarchical HS4 / CN8 drill-down (every partner has HS2 detail
# through the product-partner table).
KEY_PARTNERS = ["DE", "BE", "FR", "NL", "US", "CN", "IT", "GB", "PL", "CH"]

# Number of largest lines retained per (year, flow[, partner]) for the detailed tiers.
# Shares are always computed against the true HS2 flow totals, never the truncated sums.
CN8_TOP_N_PER_YEAR_FLOW = 1000
DRILLDOWN_TOP_N = 100

# Number of years requested in one multi-year Eurostat call (keeps responses below the
# API cell limit that answers HTTP 413).
API_YEAR_WINDOW = 9

# ── Canonical Resilience Radar baskets (HS2 chapters, always zero-padded) ──
CRITICAL_BASKET_CHAPTERS = {
    "ENERGY": ["27"],
    "FOOD": ["01", "02", "03", "04", "10", "16", "19", "22"],
    "HEALTH": ["30", "90"],
    "METALS": ["72", "73", "25", "26", "76"],
    "TECH": ["84", "85"],
    "VEHICLES": ["87", "88"],
}
_CRITICAL_CHAPTER_SET = {ch for chs in CRITICAL_BASKET_CHAPTERS.values() for ch in chs}
NON_CRITICAL_CHAPTERS = [ch for ch in ALL_HS2_CHAPTERS if ch not in _CRITICAL_CHAPTER_SET]

ISO2_NAMES_EN = {
    "DE": "Germany", "FR": "France", "BE": "Belgium", "NL": "Netherlands",
    "US": "United States", "IT": "Italy", "GB": "United Kingdom", "ES": "Spain",
    "CN": "China", "CH": "Switzerland", "PL": "Poland", "AT": "Austria",
    "SE": "Sweden", "JP": "Japan", "CZ": "Czechia", "DK": "Denmark",
    "IE": "Ireland", "PT": "Portugal", "TR": "Turkey", "IN": "India",
    "BR": "Brazil", "KR": "South Korea", "NO": "Norway", "RU": "Russia",
    "CA": "Canada", "MX": "Mexico", "AU": "Australia", "ZA": "South Africa",
    "HU": "Hungary", "RO": "Romania", "SG": "Singapore", "LU": "Luxembourg",
    "FI": "Finland", "SK": "Slovakia", "GR": "Greece", "BG": "Bulgaria",
    "HR": "Croatia", "SI": "Slovenia", "LT": "Lithuania", "LV": "Latvia",
    "EE": "Estonia", "CY": "Cyprus", "MT": "Malta"
}

RESILIENCE_BASKETS = {
    "ALL": {
        "name": "All Product Categories",
        "short_name": "All Products",
        "chapters": [],
        "desc": "Complete merchandise trade scope across all tariff lines",
        "filter_label": "All Product Categories",
    },
    "ENERGY": {
        "name": "Energy & Fuels",
        "short_name": "Energy & Fuels",
        "chapters": CRITICAL_BASKET_CHAPTERS["ENERGY"],
        "desc": "Refined petroleum, natural gas, electrical energy",
        "filter_label": "Energy & Fuels (27)",
    },
    "FOOD": {
        "name": "Food & Nutrition",
        "short_name": "Food & Nutrition",
        "chapters": CRITICAL_BASKET_CHAPTERS["FOOD"],
        "desc": "Dairy, meat, cereals, beverages, essential nutrition",
        "filter_label": "Food & Nutrition (01–04, 10, 16, 19, 22)",
    },
    "HEALTH": {
        "name": "Health & Medicines",
        "short_name": "Health & Medicines",
        "chapters": CRITICAL_BASKET_CHAPTERS["HEALTH"],
        "desc": "Pharmaceutical products, surgical & medical instruments",
        "filter_label": "Health & Medicines (30, 90)",
    },
    "METALS": {
        "name": "Raw Materials & Metals",
        "short_name": "Raw Materials & Metals",
        "chapters": CRITICAL_BASKET_CHAPTERS["METALS"],
        "desc": "Iron, steel, aluminium, construction minerals",
        "filter_label": "Raw Materials & Metals (25–26, 72–73, 76)",
    },
    "TECH": {
        "name": "Tech & Machinery",
        "short_name": "Tech & Machinery",
        "chapters": CRITICAL_BASKET_CHAPTERS["TECH"],
        "desc": "Computers, electrical generators, telecom apparatus",
        "filter_label": "Tech & Machinery (84, 85)",
    },
    "VEHICLES": {
        "name": "Vehicles & Transport",
        "short_name": "Vehicles & Transport",
        "chapters": CRITICAL_BASKET_CHAPTERS["VEHICLES"],
        "desc": "Passenger cars, commercial transport equipment, aerospace",
        "filter_label": "Vehicles & Transport (87, 88)",
    },
    "NON_CRITICAL": {
        "name": "Other Non-Critical Categories",
        "short_name": "Non-Critical Categories",
        "chapters": NON_CRITICAL_CHAPTERS,
        "desc": "All merchandise tariff lines outside the 6 designated critical resilience baskets (Plastics, Rubber, Chemicals, Wood, Textiles, Paper, etc.)",
        "filter_label": "Other Non-Critical Categories",
    },
}

# Standard HS Sections (World Customs Organization 21 sections)
HS_SECTIONS = {
    "Section I (01-05)": ("Live animals & animal products", ["01", "02", "03", "04", "05"]),
    "Section II (06-14)": ("Vegetable products", ["06", "07", "08", "09", "10", "11", "12", "13", "14"]),
    "Section III (15)": ("Animal or vegetable fats & oils", ["15"]),
    "Section IV (16-24)": ("Prepared foodstuffs, beverages, tobacco", ["16", "17", "18", "19", "20", "21", "22", "23", "24"]),
    "Section V (25-27)": ("Mineral products & fuels", ["25", "26", "27"]),
    "Section VI (28-38)": ("Chemicals & allied industries", ["28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38"]),
    "Section VII (39-40)": ("Plastics, rubber & articles thereof", ["39", "40"]),
    "Section VIII (41-43)": ("Raw hides, skins, leather & furs", ["41", "42", "43"]),
    "Section IX (44-46)": ("Wood, cork & straw articles", ["44", "45", "46"]),
    "Section X (47-49)": ("Pulp of wood, paper & books", ["47", "48", "49"]),
    "Section XI (50-63)": ("Textiles & textile articles", [f"{i:02d}" for i in range(50, 64)]),
    "Section XII (64-67)": ("Footwear, headgear, umbrellas", ["64", "65", "66", "67"]),
    "Section XIII (68-70)": ("Articles of stone, plaster, glass", ["68", "69", "70"]),
    "Section XIV (71)": ("Precious stones & metals, jewelry", ["71"]),
    "Section XV (72-83)": ("Base metals & articles (incl. Steel)", [f"{i:02d}" for i in range(72, 84)]),
    "Section XVI (84-85)": ("Machinery, electrical equipment, sound/TV", ["84", "85"]),
    "Section XVII (86-89)": ("Vehicles, aircraft, vessels & transport", ["86", "87", "88", "89"]),
    "Section XVIII (90-92)": ("Optical, medical & precision instruments", ["90", "91", "92"]),
    "Section XIX (93)": ("Arms and ammunition", ["93"]),
    "Section XX (94-96)": ("Miscellaneous manufactured articles", ["94", "95", "96"]),
    "Section XXI (97)": ("Works of art, collectors' pieces & antiques", ["97"]),
}

def get_hs_section(hs_code: str) -> str:
    """Return the high-level HS section name for a given HS code (2-digit or more)."""
    ch = str(hs_code)[:2].zfill(2)
    for section_name, (desc, chapters) in HS_SECTIONS.items():
        if ch in chapters:
            return f"{section_name}: {desc}"
    return "Other / Unclassified"
