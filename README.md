# STATEC Hackathon 2026 — Luxembourg's External Trade Radar (Team SCRAPPED)

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
#   --ingest   Extract trade data from Eurostat directly to data/raw/*.csv
#   --process  Transform raw CSVs into aggregated data/processed/*.csv tables
#   --app      Start the interactive Dash web application
#   --test     Execute the automated test suite (all active tabs, filters, models)
#   --all      Run end-to-end pipeline (Ingest CSV -> Process CSV -> Launch App)
#   --port     Port for Dash server (default: 8050)
```

### 4. Automated Testing & Verification
Execute the test suite to verify all tab renderers, basket filters, and econometric models:
```bash
python run_pipeline.py --test
# Or run directly:
python tests/run_all_tests.py
```

---

## Dashboard Architecture & Numbering System

The dashboard is structured into **5 numbered analytical tabs**, **8 sections**, and **18 numbered figures** with synchronized interactive filters and methodology infoboxes:

### 1. 🛡️ Tab 1: Resilience Radar
Designed for policymakers, strategic analysts, and directors assessing sovereign supply chain security, critical dependencies, and national resilience:
* **Section 1.1: Macro Trajectory & Geopolitical Origins**
  * **Figure 1.1:** Overall Merchandise Trade Balance Trajectory (2000–2026).
  * **Figure 1.2:** Top Trading Partners Ranking (Dynamic Value €M vs. Share % toggle).
  * **Figure 1.3:** Single Market Integration (EU vs. Extra-EU physical import distribution).
  * **Figure 1.4:** Geopolitical Trade Balance Matrix (Scatter mapping net surplus vs. volume).
  * **Figure 1.5:** Origin Concentration Trend (Herfindahl-Hirschman Index evolution over 26 years).
* **Section 1.2: Critical Import Baskets & Supplier Concentration**
  * **Figure 1.6:** Critical Import Baskets Matrix (HHI vs. Top Supplier Share across *Energy, Food, Health, Metals, Tech, Vehicles*, and *Non-Critical Categories*).
  * **Figure 1.7:** Supplier Concentration Breakdown with dynamic risk badges (Low `<1500`, Moderate `1500–2500`, High `>2500`).

### 2. 🌍 Tab 2: Trading Partners
Bilateral trade dynamics, geographic flow distribution, and hierarchical tariff line drill-down:
* **Section 2.1: Main Trading Partners & Bilateral Flows**
  * **Figure 2.1:** Top 10 Bilateral Partners by Trade Value / Market Share.
  * **Figure 2.2:** Global Geographic Flow Map (Choropleth centered on Luxembourg with Europe / World scopes).
  * **Figure 2.3:** Multi-Year Bilateral Trajectory for selected partner country.
* **Section 2.2: Bilateral Product Breakdown per Partner**
  * **Figure 2.4:** Hierarchical Tariff Drill-Down for selected partner across **2-digit (HS2)**, **4-digit (HS4)**, and **8-digit (CN8)** tariff lines, with dynamic threshold filtering and **Critical Basket Filters**.

### 3. 📦 Tab 3: Product Categories
Structural transformation of Luxembourg's trade basket, diversification, and principal supplier origins:
* **Section 3.1: Product Categories & Structural Shift**
  * **Figure 3.1:** Top Traded Product Categories (HS2 Chapters, HS4 Headings, CN8 Subheadings).
  * **Figure 3.2:** 26-Year Structural Transformation (Multi-decade transition from steel to automotive, plastics, and advanced machinery; Volume €M vs. Market Share % toggle).
  * **Figure 3.3:** CN / Chapter Level Breakdown Table.
* **Section 3.2: Principal Partners by Product Category**
  * **Figure 3.4:** Top Sourcing Partners for Selected Commodity.
  * **Figure 3.5:** Supplier Geographic Distribution Map.

### 4. 📊 Tab 4: Peer Benchmarks
Regional economic benchmarking against core European peer economies (Germany, France, Belgium, Netherlands):
* **Section 4.1: Regional Peer Benchmarking**
  * **Figure 4.1:** Multi-Country Trade Volume Expansion Trajectory (Indexed to **Base 100 = 2000**, with dynamic Compound Annual Growth Rate [CAGR] badges).
  * **Figure 4.2:** Structural Export-to-Import Coverage Ratio Benchmarks (with explicit 100% parity threshold markers).

### 5. 📅 Tab 5: Seasonality Analysis
Econometric time-series decomposition, intra-year cyclicality, and seasonal factor extraction:
* **Section 5.1: Econometric Seasonality & Trend Analysis**
  * **Methodology Infobox:** Built-in guidance detailing 12-month centered moving averages, multiplicative detrending ratios, and robust multi-year median normalization.
  * **Figure 5.1:** Monthly Trade Flow Timeseries & 12M Trend (Toggles for Raw Observed, 12M Rolling Trend, and Seasonally Adjusted series).
  * **Figure 5.2:** Monthly Seasonal Factors & Percentage Deviation (Clean, uncluttered bar chart isolating recurring calendar deviations, spotlighting the annual August industrial slump vs. spring/autumn peaks).

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
  * **4-Digit (HS4 Headings)**: Intermediate product classes
  * **8-Digit (CN8 Detailed)**: Precise tariff lines with dynamic significance filtering and **Critical Basket Filters**.

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
├── tests/                        # Automated regression and verification test suite
│   ├── test_dashboard.py         # Active tab renderers, HHI & seasonality tests
│   ├── test_basket_filters.py    # Critical basket filtering across all tabs
│   ├── test_year_range.py        # Dynamic temporal adaptation audit
│   ├── test_partner_drilldown.py # Partner hierarchical tariff breakdown tests
│   └── run_all_tests.py          # Master test runner
├── objectives.txt                # Hackathon problem statement
├── run_pipeline.py               # Master CLI runner
├── requirements.txt              # Project dependencies
└── README.md
```
