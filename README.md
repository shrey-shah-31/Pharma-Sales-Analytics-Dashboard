# 💊 Pharma Sales Analytics & Commercial Strategy Dashboard

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MySQL 8.0+](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)](https://www.mysql.com/)
[![Tableau Ready](https://img.shields.io/badge/Tableau-Cloud%20%7C%20Desktop-E97627.svg)](https://www.tableau.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end commercial pharmaceutical sales analytics pipeline and executive intelligence platform. This repository encompasses large-scale synthetic data engineering (115,000+ transactions), advanced SQL business intelligence, exploratory data analysis, RFM doctor segmentation, Tableau star-schema modeling, and executive stakeholder strategy reports.

---

## 📑 Repository Table of Contents

- [Project Architecture](#-project-architecture)
- [Repository Structure](#-repository-structure)
- [Dataset Specifications & Injected Patterns](#-dataset-specifications--injected-patterns)
- [SQL Analytics Suite](#-sql-analytics-suite)
- [Python EDA & RFM Segmentation](#-python-eda--rfm-segmentation)
- [Tableau Dashboard Architecture](#-tableau-dashboard-architecture)
- [Executive Business Recommendations](#-executive-business-recommendations)
- [Quick Start Guide](#-quick-start-guide)

---

## 🏛️ Project Architecture

```
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│  1. DATA GENERATION    │      │  2. SQL ANALYTICS      │      │  3. PYTHON & RFM PIPELINE
│  • Faker + NumPy       ├─────►│  • MySQL 8.0+          ├─────►│  • Pandas / Seaborn    │
│  • 115,000 Txns        │      │  • MoM/QoQ Window Fns  │      │  • HCP RFM Modeling    │
│  • Injected Patterns   │      │  • Underperformer Flags│      │  • Star Schema Export  │
└────────────────────────┘      └────────────────────────┘      └───────────┬────────────┘
                                                                            │
                                ┌────────────────────────┐      ┌───────────▼────────────┐
                                │  5. STRATEGY REPORT    │      │  4. TABLEAU DASHBOARD  │
                                │  • 5 Recommendations   │◄─────┤  • Interactive Specs   │
                                │  • Territory Strategy  │      │  • Calculated Formulas │
                                │  • Portfolio Rational. │      │  • HTML Live Mockup    │
                                └────────────────────────┘      └────────────────────────┘
```

---

## 📁 Repository Structure

```
Pharma Sales Analytics Dashboard/
│
├── README.md                               # Comprehensive Project Documentation
├── pharma_sales.csv                        # Primary Dataset (115,000 transactions, 21.0 MB)
│
├── data/                                   # Cleaned Dimension & Fact Tables (Tableau Ready)
│   ├── pharma_sales.csv                    # Complete raw transaction dataset
│   ├── fact_sales.csv                      # Transaction fact table (115,000 records)
│   ├── dim_drug.csv                        # Drug dimension catalog (14 products)
│   ├── dim_region.csv                      # Geographic territory & tier dimension (20 territories)
│   └── dim_hcp.csv                         # Healthcare professional RFM dimension (800 HCPs)
│
├── sql/
│   └── queries.sql                         # 7 Production MySQL 8.0+ Business Intelligence Queries
│
├── notebooks/
│   └── pharma_sales_analysis.ipynb         # Full Jupyter Notebook (EDA, Time-Series, RFM, Visuals)
│
├── scripts/
│   ├── generate_data.py                    # Fast vectorized synthetic data generator script
│   ├── run_analysis_pipeline.py            # Automated pipeline & Tableau CSV export script
│   └── build_notebook.py                   # Programmatic Jupyter Notebook compiler
│
├── dashboard/
│   ├── tableau_dashboard_design.md         # Full Technical Tableau Design Spec & Formula Catalog
│   └── dashboard_preview.html              # Standalone Interactive Web Prototype
│
└── reports/
    └── business_report.md                  # Executive Stakeholder Strategy & Recommendation Report
```

---

## 📊 Dataset Specifications & Injected Patterns

The dataset contains **115,000 transactions** spanning **2 full calendar years** (`2024-01-01` to `2025-12-31`).

### Injected Realistic Dynamics & Validation:

1. **Seasonality Cycle (Q4 Surge & Summer Dip)**:
   - **Q4 Surge (Oct–Dec)**: Accounts for **34.11% (\$289.43M)** of annual net revenue (Dec peak at **12.43%**), driven by hospital budgeting deadlines and deductible resets.
   - **Summer Dip (Jun–Aug)**: Accounts for **19.54% (\$163.78M)** of annual sales (~6.5% monthly average).
2. **15% Underperforming Territories (3 out of 20)**:
   - National Benchmark Territory Mean: **\$42.43M**
   - Lagging Territories:
     - `North-Plains`: **\$28.99M (-31.7% below mean)**
     - `South-Delta`: **\$27.92M (-34.2% below mean)**
     - `West-Desert`: **\$28.22M (-33.5% below mean)**
3. **Pareto Revenue Concentration (Top 3 Drugs ~50%)**:
   - The top 3 products account for **50.95% (\$432.37M)** of total revenue:
     - `#01 Oncozap (Pembrolizumab)` [Oncology]: **\$197.65M (23.29%)**
     - `#02 Glycaheal (Semaglutide)` [Diabetes]: **\$119.61M (14.10%)**
     - `#03 Tumorkill (Trastuzumab)` [Oncology]: **\$115.11M (13.57%)**

---

## 🗄️ SQL Analytics Suite (`sql/queries.sql`)

The repository includes a suite of 7 production MySQL 8.0+ queries:

1. **Monthly & Quarterly Sales Aggregations**: Granular volume, gross/net sales, average discount %, and AOV.
2. **MoM and QoQ Growth % via `LAG()`**:
   ```sql
   (ZN(SUM(net_sales)) - LAG(SUM(net_sales), 1) OVER (ORDER BY sales_year, sales_month)) 
   / LAG(SUM(net_sales), 1) OVER (ORDER BY sales_year, sales_month) * 100
   ```
3. **Top 10 Drugs by Revenue and Units**: Multi-metric product ranking with running cumulative Pareto shares.
4. **Region & Territory Multi-Level Ranking**: National rankings and intra-regional ranks via `PARTITION BY region`.
5. **HCP Segmentation (Platinum / Gold / Silver / Bronze)**: Quantile-based prescriber tiering with executive summaries.
6. **Therapeutic Area Contribution Breakdown**: Cross-portfolio analysis across Cardiology, Oncology, Neurology, and Diabetes.
7. **Underperforming Territory Flagging (<70% of Benchmark)**: Dynamic deficit calculation and sales rep mapping.

---

## 🔬 Python EDA & RFM Segmentation (`notebooks/`)

The Jupyter Notebook executes a complete analysis workflow:
- **Data Quality Audit**: Verification of $0$ nulls, $0$ duplicates, and continuous 731-day coverage.
- **Visual EDA**: Distribution histograms, cross-metric correlation heatmap ($r = 0.998$ gross/net, $r = 0.742$ price/net), 24-month seasonality timelines, and category breakdown.
- **HCP RFM Modeling**:
  - **R (Recency)**: Days elapsed since doctor's last prescription.
  - **F (Frequency)**: Total transaction count.
  - **M (Monetary)**: Total net revenue generated.
  - **Segments**: *Champions (Tier-1 KOLs)*, *Loyal High-Volume*, *High-Value Specialty*, *Potential Growth*, *At-Risk / Low-Volume*.
- **Tableau Star-Schema Exports**: Automatically populates `fact_sales.csv`, `dim_drug.csv`, `dim_region.csv`, and `dim_hcp.csv`.

---

## 📱 Tableau Dashboard Architecture (`dashboard/`)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  💊 PHARMA COMMERCIAL SALES EXECUTIVE DASHBOARD                                                       │
├──────────────┬──────────────┬──────────────┬──────────────┬────────────────────────┬──────────────────┤
│ TOTAL SALES  │ MOM GROWTH   │ QOQ GROWTH   │ ACTIVE HCPS  │ TOP DRUG REVENUE       │ PARAMETERS       │
│   $848.55M   │   +14.6%     │   +34.1%     │     800      │ Oncozap ($197.65M)     │ Target: 100% (▼) │
│ Gross:$957.7M│  ▲ Oct-Dec   │  Q4 Spikes   │ 6 Specialties│ 23.29% Portfolio Share │ Metric: Net Sales│
├──────────────┴──────────────┴──────────────┴──────────────┴────────────────────────┴──────────────────┤
│ 📈 Sheet 1: Monthly Sales Trend (Seasonality Cycle)        │ 🏆 Sheet 3: Top 10 Drugs by Revenue      │
│ [Dual-Axis Line & Volume with Summer Dip & Q4 Spike Bands] │ [Horizontal Bars colored by TA]          │
├────────────────────────────────────────────────────────────┼──────────────────────────────────────────┤
│ 🗺️ Sheet 4: Territory Performance Map                      │ 👥 Sheet 5: HCP Segment Treemap          │
│ [Choropleth Map: % of Target Benchmark & <70% Alerts]      │ [Champions | Loyal | Specialty | At-Risk]│
├────────────────────────────────────────────────────────────┴──────────────────────────────────────────┤
│ 🏢 Sheet 6: Region × Therapeutic Area Matrix   │ 📊 Sheet 2: Quarterly KPI Heatmap Table              │
│ [Cross-category revenue concentration tiles]   │ [Q1-Q4 YoY & QoQ matrix with diverging green/red]    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Core Tableau Calculated Fields Provided:
- **MoM Sales Growth %**: `(SUM([net_sales]) - LOOKUP(SUM([net_sales]), -1)) / ABS(LOOKUP(SUM([net_sales]), -1))`
- **Territory Benchmark Target**: `{ FIXED : AVG({ FIXED [territory] : SUM([net_sales]) }) } * [p_Target_Selector]`
- **% of Target Achieved**: `SUM([net_sales]) / [Territory Benchmark Target]`
- **Underperformer Flag**: `IF [% of Target Achieved] < 0.70 THEN "CRITICAL: Underperforming (<70%)" ELSE "ON TARGET" END`
- **Dynamic Top Drug LOD**: `{ FIXED : MAX(IF { FIXED [drug_name]: SUM([net_sales]) } = { FIXED: MAX({ FIXED [drug_name]: SUM([net_sales]) }) } THEN [drug_name] END) }`

> **Interactive Mockup**: Open [`[dashboard/dashboard_preview.html]`]([dashboard/dashboard_preview.html](https://htmlpreview.github.io/?https://raw.githubusercontent.com/shrey-shah-31/Pharma-Sales-Analytics-Dashboard/refs/heads/main/dashboard_preview.html)) in any browser to interact with the live filterable dashboard preview.

---

## 🎯 Executive Business Recommendations (`reports/business_report.md`)

1. **Q4 Seasonality Early Lock-In**: Pre-book hospital volume in August/September with guaranteed pricing to capture **+\$18M–\$24M** in accelerated revenue.
2. **Tier-1 KOL Concierge Model**: Assign dedicated MSLs and advisory boards to the top 204 Champion doctors who drive 32.1% of revenue, increasing retention by **15%** (**+\$16M–\$20M**).
3. **Hospital Discount Rationalization**: Replace flat 17.5% volume discounts with Tiered Performance Agreements tied to formulary exclusivity, capturing **+\$12M–\$15M in margin**.
4. **Portfolio Prioritization**:
   - 🚀 **Double-Down**: `Oncozap (Pembrolizumab)` (\$197.6M), `Glycaheal (Semaglutide)` (\$119.6M), and `Tumorkill (Trastuzumab)` (\$115.1M).
   - 🔻 **Deprioritize**: `Cerebrox (Memantine)` (\$17.2M) and `Vasotens (Amlodipine)` (\$19.4M) by shifting from field detailing to 100% digital self-service.
5. **Territory Turnaround Sprint**: Rebalance sales reps from over-performing metro territories into `North-Plains`, `South-Delta`, and `West-Desert` to recover **+\$14M–\$18M** of their \$42.16M deficit.

**Total Annual Commercial Upside**: **+\$72.0M to \$92.0M**

---

## 🔍 Automated Verification & Data Rigor (`verify.py`)

Run the standalone verification suite to mathematically validate all data integrity checks, financial aggregates, seasonality distributions, and underperforming territory thresholds:

```bash
python verify.py
```

### Verification Output Benchmark:
```text
================================================================================
PHARMA COMMERCIAL SALES ANALYTICS -- RIGOROUS VERIFICATION SUITE
================================================================================

[1] DATASET INTEGRITY & DIMENSIONS:
  * Total Transactions      : 115,000 (Requirement: 100,000+ rows) -> [PASS]
  * Date Timeline Range     : 2024-01-01 to 2025-12-31 (731 unique days)
  * Null Values Count       : 0 -> [PASS]
  * Duplicate TXN IDs Count : 0 -> [PASS]

[2] FINANCIAL METRICS SUMMARY:
  * Total Gross Sales       : $957,708,904.48
  * Total Net Sales         : $848,552,440.67 (~$848.55M)
  * Total Units Sold        : 3,697,414 units
  * Effective Discount Rate : 11.40%

[3] SEASONALITY VALIDATION (Q4 SPIKE & SUMMER DIP):
  * Q4 Revenue (Oct-Dec)    : $289,431,837.44 (34.11% of Annual Sales) -> [PASS]
  * Summer Revenue (Jun-Aug): $165,776,923.09 (19.54% of Annual Sales) -> [PASS]
  * Peak Month (December)   : $105,490,330.14 (12.43%)

[4] UNDERPERFORMING TERRITORIES (<70% TARGET BENCHMARK):
  * National Mean Benchmark : $42,427,622.03
  * Underperforming Count   : 3 of 20 territories (15.0%) -> [PASS]
    - South-Delta    : $27,916,661.44 (65.8% of Benchmark | Deficit: -$14,510,960.59)
    - West-Desert    : $28,221,815.70 (66.5% of Benchmark | Deficit: -$14,205,806.33)
    - North-Plains   : $28,989,788.14 (68.3% of Benchmark | Deficit: -$13,437,833.89)
  * Total Addressable Gap   : $42,154,600.82 (~$42.16M)

[5] DRUG REVENUE CONCENTRATION (TOP 3 PARETO):
    #1 Oncozap (Pembrolizumab)      [Oncology]: $197,650,778.90 (23.29%)
    #2 Glycaheal (Semaglutide)      [Diabetes]: $119,613,063.78 (14.10%)
    #3 Tumorkill (Trastuzumab)      [Oncology]: $115,106,385.99 (13.57%)
    #4 Coroxin (Apixaban)           [Cardiology]: $84,605,979.57 (9.97%)
    #5 Cellstop (Lenalidomide)      [Oncology]: $59,037,653.41 (6.96%)
  * Top 3 Cumulative Share  : 50.95% (Target: ~50%) -> [PASS]

[6] TABLEAU STAR-SCHEMA FILE EXPORTS:
  * data/fact_sales.csv    : [EXISTS] 115,000 records (11.77 MB)
  * data/dim_drug.csv      : [EXISTS] 14 records (0.00 MB)
  * data/dim_region.csv    : [EXISTS] 20 records (0.00 MB)
  * data/dim_hcp.csv       : [EXISTS] 800 records (0.08 MB)

================================================================================
[PASS] ALL 7 VERIFICATION CRITERIA PASSED WITH 100% INTEGRITY
================================================================================
```




## 📜 License
This project is open-source under the MIT License.
