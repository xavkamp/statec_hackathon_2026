# STATEC Hackathon 2026 — Luxembourg External Trade Intelligence

An interactive analytical platform and production-grade Dash dashboard providing multi-dimensional insights into Luxembourg's external trade in goods from **2000 to 2026**.

Powered by Eurostat Comext dataset **`[ds-045409]`** (*"EU trade since 1988 by HS2-4-6 and CN8"*).

---

## Architecture Overview

Built following the **Medallion Data Architecture** (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) and modern dashboard principles:

```
Eurostat Comext API (ds-045409)
           │
           ▼
┌───────────────────────┐
│     Bronze Layer      │  Raw JSON responses cached in data/bronze/
│ (Landing & Ingestion) │  • Partners (2000-2026) • HS2 Chapters • Benchmarks • Seasonality • Drilldowns
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│     Silver Layer      │  Cleaned, typed, validated Parquet tables in data/silver/
│  (Cleansing & Typing) │  • Standardized country codes, flows, date dimensions, HS sections
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│      Gold Layer       │  Serving tables & analytical models in data/gold/
│ (Aggregates & Models) │  • Overview KPIs • Rankings • Seasonal decomposition • Peer benchmarks
└──────────┬────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│             Interactive Dash Web Application           │
│  http://127.0.0.1:8050 • Multi-Tab Exploratory UI      │
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
#   --app      Start the interactive Dash web application
#   --all      Run end-to-end pipeline (Bronze -> Silver -> Gold -> App)
```

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
│   ├── bronze/          # Raw cached Eurostat Comext responses (.json)
│   ├── silver/          # Clean typed Parquet tables (.parquet)
│   └── gold/            # Analytical serving Parquet tables (.parquet)
├── src/
│   ├── config.py        # Central parameters (2000-2026, endpoints, HS sections)
│   ├── ingestion/       # Eurostat Comext API fetcher & JSON-stat parser
│   ├── processing/      # Silver & Gold transformation pipelines
│   └── dashboard/       # Dash interactive application & design system
├── objectives.txt       # Hackathon problem statement
├── run_pipeline.py      # Master CLI runner
└── README.md
```
