# STATEC Hackathon 2026 — Luxembourg External Trade Intelligence

An interactive analytical platform and production-grade Dash dashboard providing multi-dimensional insights into Luxembourg's external trade in goods from **2000 to 2026**.

Powered by Eurostat Comext dataset **`[ds-045409]`** (*"EU trade since 1988 by HS2-4-6 and CN8"*).

---

## Architecture Overview (Pure Tabular CSV Pipeline)

Built using a two-stage **Tabular CSV Architecture** (`data/raw/` $\rightarrow$ `data/processed/`):

```
Eurostat Comext API (ds-045409)
           │
           ▼
┌────────────────────────┐
│     Raw CSV Layer      │  Direct extraction from Eurostat API to CSV in data/raw/
│   (Extracted Tabular)  │  • partners_annual_raw.csv • hs2_products_annual_raw.csv
│                        │  • country_benchmarks_annual_raw.csv • monthly_seasonality_raw.csv
│                        │  • partner_drilldown_raw.csv
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│   Processed CSV Layer  │  Aggregated & model-ready CSV tables in data/processed/
│  (Serving & Analytics) │  • overview_kpis.csv • partner_rankings.csv • product_rankings.csv
│                        │  • seasonal_decomposition.csv • country_benchmarks.csv
│                        │  • partner_drilldown_lvl2.csv, lvl4.csv, lvl8.csv
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│             Interactive Dash Web Application           │
│  http://127.0.0.1:8050 • Reads directly from CSV       │
└────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Requirements & Installation
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
# Or install directly:
pip install pyarrow plotly dash dash-bootstrap-components statsmodels scipy requests
```

### 2. Launch the Application
To run the pre-aggregated dashboard immediately:
```bash
python run_pipeline.py --app
```
Then open your browser to **http://127.0.0.1:8050**.

### 3. CLI Pipeline Options
```bash
python run_pipeline.py --help
# Options:
#   --ingest   Fetch latest data from Eurostat Comext API into data/bronze/
#   --silver   Transform bronze JSON files into silver Parquet tables
#   --gold     Compute gold analytical models and aggregates
#   --csv      Export all tables to human-readable CSV format in data/csv/
#   --app      Start the interactive Dash web application
#   --all      Run end-to-end pipeline (Bronze -> Silver -> Gold -> CSV -> App)
```

---

## Dual-Audience Dashboard Architecture

The dashboard is structured into two distinct operational modes to serve two target audiences:

### 1. 🏛️ National Leadership Briefing (Answers Pressing Questions First)
Designed for national leaders, ministers, policy makers, and directors who require an immediate, high-impact assessment of Luxembourg's sovereign supply chain resilience and economic security:
* **Sovereign Supply Chain & Resilience Radar (Default on Load)**:
  * **Executive Alert Tiles**: Instant visibility into single-point energy vulnerabilities, port corridor transit risks, the macro service buffer, and seasonal supply dips.
  * **Strategic Basket Vulnerability Chart**: Compares 6 vital import baskets (Energy, Food, Health, Tech, Raw Materials, Vehicles) on Supplier Concentration Index (HHI), Top Supplier Dominance (%), and Hub Transit Dependency (%).
  * **Stress-Test Basket Cards**: Individual risk cards with HHI badges (High / Moderate / Diversified), leading 4-digit good vulnerabilities, and single-click links to granular analyst data.
  * **Sovereign Policy Recommendations**: Concrete safeguards regarding petroleum stockpiles, port agreements with Antwerp/Rotterdam, and hospital medicine reserves.
* **Macroeconomic Health & Sovereignty**:
  * 25-year trade volume trajectory (+89% growth).
  * Plain-language explanation of the structural merchandise trade deficit (-€9.2B) and why a ~65% goods coverage ratio is sustainably balanced by Luxembourg's €25B+ services surplus.
  * Intra-EU integration (>80%) single-market cushion.
* **Geopolitical Exposure & Seasonal Shocks**:
  * Direct neighbor import dependency (Belgium 32.9%, Germany 28.2%, France 12.5% = 73.6% of physical imports).
  * Third-country geopolitical exposure (United States, China, United Kingdom).
  * Operational warning regarding the annual **August -14.4% trade contraction** during collective industrial leave ("congé collectif").

### 2. 🔬 Data Analyst Deep-Dive Suite (Explore Details Afterwards)
Designed for economists, trade researchers, and data analysts requiring granular micro-data exploration tools:
* **Tab 1: Trading Partners & Global Map (Q1)**: Interactive choropleth map linked to ISO-3 country codes with regional scope zoom (🇪🇺 Europe, 🌍 World, 🌎 Americas, 🌏 Asia), metric toggle (Trade Value vs Market Share), interactive click-to-spotlight synchronization with Top 10 partner bar charts, and 25-year historical share evolution.
* **Tab 2: Product Categories & Structural Shift (Q2)**: Multi-level treemaps (HS Section $\rightarrow$ HS2 Chapter $\rightarrow$ HS4 Subheading) and 25-year structural transformation charts from steel to advanced machinery and automotive.
* **Tab 3: Hierarchical Micro-Flows HS2 $\rightarrow$ HS4 $\rightarrow$ CN8 (Q3 & Q4)**: Product partner choropleth map and concentration analysis (Q3) with interactive supplier click-spotlight, and partner-specific tariff line drilldowns up to 8-digit CN8 codes with dynamic significance threshold filtering (Q4).
* **Tab 4: Econometric Seasonality & Trend Lab (Q6)**: Decomposition into raw observed series, 12-month centered rolling trend, and seasonally adjusted series with empirical month-of-year seasonal factors.
* **Tab 5: Regional Peer Benchmarking (Q5)**: Comparative volume expansion index (2000 = 100) and merchandise coverage ratio benchmarks against Germany, France, Belgium, and the Netherlands.

---

## Answers to Hackathon Research Questions

### Q1: Trading Partners & Evolution
* **Dominant Partners**: Germany (**25.3%** of exports, **28.2%** of imports), Belgium (**12.7%** exports, **32.9%** imports), and France (**15.4%** exports, **12.5%** imports).
* **Evolution**: Luxembourg's external merchandise trade has remained intensely integrated with its three direct neighbors (>53% of exports and >73% of imports). Non-EU partners (US, China, UK) represent key strategic niches.

### Q2: Main Product Categories & Structural Shift
* **Exports**: Shifted from heavy primary metals to specialized high-value manufactured goods:
  * Machinery & Mechanical Appliances (HS 84): **13.5%**
  * Vehicles & Automotive (HS 87): **10.0%**
  * Plastics & Polymers (HS 39): **9.9%**
  * Iron & Steel (HS 72): **8.2%** (down from historical highs near 30% in earlier decades)
* **Imports**: Dominated by Vehicles (HS 87: **15.1%**), Mineral Fuels & Refined Petroleum (HS 27: **11.0%**), and Machinery (HS 84: **7.8%**).

### Q3 & Q4: Hierarchical Flow Drill-Down (HS2 $\rightarrow$ HS4 $\rightarrow$ CN8)
* The dashboard features interactive hierarchical exploration: select any partner country (e.g. Germany) and toggle between:
  * **2-Digit (HS2 Chapters)**: High-level sector totals
  * **4-Digit (HS4 Subheadings)**: Intermediate product classes
  * **8-Digit (CN8 Detailed)**: Precise tariff lines with dynamic significance filtering to eliminate noise.

### Q5: Comparative Peer Benchmarking
* **Trade Growth**: Luxembourg's trade volume has expanded by **+89%** since 2000 (Index 189), in line with France (+84%), while logistics transit hubs (Netherlands +236%, Belgium +168%) saw stronger physical goods transit expansion.
* **Coverage Ratio Asymmetry**: Germany (116%) and Netherlands (111%) maintain physical merchandise surpluses, whereas Luxembourg operates at a structural goods coverage ratio of **~65%** (offset by huge net service exports in financial and professional sectors).

### Q6: Seasonality & Trend Filtering
* **Seasonal Slump**: Empirical decomposition reveals a marked **August contraction (Seasonal factor = 0.856)**, representing a **14.4% dip** below annual trend due to European factory holidays and Luxembourg's collective summer leave ("congé collectif").
* **Peaks**: Activity rebounds with a spring peak in **March (factor = 1.098)** and an autumn peak in **October (factor = 1.091)**.
* **Trend Filtering**: The dashboard allows toggling raw observed monthly series vs. 12-month centered rolling trend vs. seasonally adjusted series.

---

## Directory Structure

```
statec_hackathon_2026/
├── data/
│   ├── raw/                      # Raw extracted CSV files from Eurostat API
│   │   ├── partners_annual_raw.csv
│   │   ├── hs2_products_annual_raw.csv
│   │   ├── country_benchmarks_annual_raw.csv
│   │   ├── monthly_seasonality_raw.csv
│   │   └── partner_drilldown_raw.csv
│   └── processed/                # Analytical & model-ready serving CSV files
│       ├── overview_kpis.csv
│       ├── partner_rankings.csv
│       ├── product_rankings.csv
│       ├── seasonal_decomposition.csv
│       ├── country_benchmarks.csv
│       ├── partner_drilldown_lvl2.csv
│       ├── partner_drilldown_lvl4.csv
│       └── partner_drilldown_lvl8.csv
├── src/
│   ├── config.py                 # Central parameters (2000-2026, endpoints, HS sections)
│   ├── ingestion/
│   │   ├── fetch_data.py         # Direct Eurostat API extraction to CSV
│   │   └── jsonstat_parser.py    # Vectorized in-memory parser
│   ├── processing/
│   │   └── process_data.py       # Raw CSV to processed CSV transformation
│   └── dashboard/
│       ├── app.py                # Interactive Dash web application
│       ├── data_loader.py        # Cached CSV loader
│       └── design_system.py      # Plotly styling, colors, and layout helpers
├── objectives.txt                # Hackathon problem statement
├── run_pipeline.py               # Master CLI runner
├── requirements.txt              # Project dependencies
└── README.md
```
