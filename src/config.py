"""Configuration constants for STATEC Hackathon 2026 - Luxembourg External Trade.
Dataset: Eurostat ds-045409 (EU trade since 1988 by HS2-4-6 and CN8)
Time span: 2000 - 2026
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

# Eurostat Comext API
COMEXT_API_URL = "https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/ds-045409"

# Time span constraint: 2000 - 2026
START_YEAR = 2000
END_YEAR = 2026
YEARS = [str(y) for y in range(START_YEAR, END_YEAR + 1)]

# Reporters
PRIMARY_REPORTER = "LU"
PEER_REPORTERS = ["LU", "BE", "DE", "FR", "NL"]

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
