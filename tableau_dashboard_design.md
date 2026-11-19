# 📊 Pharma Sales Analytics - Interactive Tableau Dashboard Specification

A comprehensive production-ready design guide, data modeling blueprint, calculated field formula catalog, and visual hierarchy for building the **Pharma Commercial Performance Executive Dashboard** in Tableau Desktop / Tableau Cloud / Tableau Server.

---

## 🏗️ 1. Data Model & Relationships (Star Schema)

In Tableau's Data Source layer, connect to the 4 extracted CSV files with physical/logical relationships:

```
                  ┌────────────────────────┐
                  │       dim_drug         │
                  │ ────────────────────── │
                  │ PK: drug_id            │
                  └───────────┬────────────┘
                              │ 1:N (on drug_id)
                              │
┌────────────────────────┐    ▼    ┌────────────────────────┐
│       dim_region       │       │       fact_sales       │       ┌────────────────────────┐
│ ────────────────────── │◄──────┤ ────────────────────── │──────►│        dim_hcp         │
│ PK: territory          │  N:1  │ PK: transaction_id     │  N:1  │ ────────────────────── │
└────────────────────────┘  (on  │ FK: drug_id, territory │  (on  │ PK: hcp_id             │
                        territory)│ FK: hcp_id, sales_rep  │hcp_id)│                        │
                                 └────────────────────────┘       └────────────────────────┘
```

### Table Relationships Configuration:
- **`fact_sales` (Center Fact)**: Grain = Individual sale transaction.
- **`dim_drug`**: Linked via `[fact_sales].[drug_id] = [dim_drug].[drug_id]`
- **`dim_region`**: Linked via `[fact_sales].[territory] = [dim_region].[territory]`
- **`dim_hcp`**: Linked via `[fact_sales].[hcp_id] = [dim_hcp].[hcp_id]`

---

## 🎛️ 2. Parameters Configuration

Create the following parameters in Tableau to enable interactive scenarios:

### Parameter 1: `[p_Target_Selector]`
*Allows executives to test baseline target models vs. aggressive stretch targets.*
- **Data type**: Float
- **Display format**: Percentage (`0.0%`)
- **Allowable values**: List
  - `1.00` &rarr; "Baseline Target (National Benchmark)"
  - `1.05` &rarr; "+5% Growth Target"
  - `1.10` &rarr; "+10% Stretch Target"
  - `1.15` &rarr; "+15% Aggressive Expansion"
- **Current Value**: `1.00`

### Parameter 2: `[p_Growth_Threshold]`
*Controls alerting threshold on MoM/QoQ KPI indicators.*
- **Data type**: Float
- **Display format**: Percentage (`0.0%`)
- **Allowable values**: Range (`-0.20` to `0.20`, Step = `0.02`)
- **Current Value**: `0.00` (0.0%)

### Parameter 3: `[p_Metric_Toggle]`
*Toggles views between Net Sales Revenue and Units Sold.*
- **Data type**: String
- **Allowable values**: List
  - `"Net Sales ($)"`
  - `"Units Sold"`
  - `"Gross Sales ($)"`
- **Current Value**: `"Net Sales ($)"`

---

## 📐 3. Comprehensive Tableau Calculated Fields Catalog

Copy and paste the exact formulas below into Tableau's Calculated Field editor:

### A. Core Metrics & Parameter-Driven Metrics

#### 1. `[Selected Metric Value]`
```tableau
CASE [p_Metric_Toggle]
    WHEN "Net Sales ($)" THEN SUM([net_sales])
    WHEN "Units Sold" THEN SUM([units_sold])
    WHEN "Gross Sales ($)" THEN SUM([total_sales])
    ELSE SUM([net_sales])
END
```

#### 2. `[Average Discount Rate %]`
```tableau
SUM([total_sales] - [net_sales]) / SUM([total_sales])
```

#### 3. `[Realized Price Per Unit]`
```tableau
SUM([net_sales]) / SUM([units_sold])
```

---

### B. Time Intelligence & Growth Window Functions

#### 4. `[MoM Sales Growth %]`
*Compute using: Table (Across) or Specific Dimensions -> `[Date (Month)]`*
```tableau
(ZN(SUM([net_sales])) - LOOKUP(ZN(SUM([net_sales])), -1)) 
/ 
ABS(LOOKUP(ZN(SUM([net_sales])), -1))
```

#### 5. `[QoQ Sales Growth %]`
*Compute using: Table (Across) or Specific Dimensions -> `[Date (Quarter)]`*
```tableau
(ZN(SUM([net_sales])) - LOOKUP(ZN(SUM([net_sales])), -1)) 
/ 
ABS(LOOKUP(ZN(SUM([net_sales])), -1))
```

#### 6. `[YoY Sales Growth %]`
*Compute using: Table (Across) or Specific Dimensions -> `[Date (Year)]` (offset -12 months or -4 quarters)*
```tableau
(ZN(SUM([net_sales])) - LOOKUP(ZN(SUM([net_sales])), -12)) 
/ 
ABS(LOOKUP(ZN(SUM([net_sales])), -12))
```

#### 7. `[Growth Status Alert]`
```tableau
IF [MoM Sales Growth %] >= [p_Growth_Threshold] THEN "▲ Above Threshold"
ELSE "▼ Lagging Threshold"
END
```

---

### C. Benchmark, Target & Underperformance Logic

#### 8. `[Territory Target Revenue]`
*Calculates baseline national territory benchmark multiplied by the selected scenario parameter:*
```tableau
{ FIXED : AVG({ FIXED [territory] : SUM([net_sales]) }) } * [p_Target_Selector]
```

#### 9. `[% of Target Achieved]`
```tableau
SUM([net_sales]) / [Territory Target Revenue]
```

#### 10. `[Territory Performance Tier]`
```tableau
IF [% of Target Achieved] < 0.70 THEN "Critical Lagging (<70%)"
ELSEIF [% of Target Achieved] < 1.00 THEN "Moderate Below Target (70-99%)"
ELSE "Target Achieved (>=100%)"
END
```

---

### D. Level of Detail (LOD) Expressions & Rankings

#### 11. `[Top Drug Name (LOD)]`
*Finds the highest-revenue drug dynamically across the filtered universe:*
```tableau
{ FIXED : MAX(
    IF { FIXED [drug_name] : SUM([net_sales]) } = 
       { FIXED : MAX({ FIXED [drug_name] : SUM([net_sales]) }) }
    THEN [drug_name]
    END
) }
```

#### 12. `[Active HCP Prescribers Count]`
```tableau
COUNTD([hcp_id])
```

#### 13. `[Drug Revenue Rank]`
```tableau
RANK_DENSE(SUM([net_sales]), 'desc')
```

#### 14. `[% of Total Portfolio Revenue]`
```tableau
SUM([net_sales]) / TOTAL(SUM([net_sales]))
```

---

## 🖥️ 4. Sheet Construction Blueprint

### Top Row: KPI Summary Cards (5 Dedicated BAN Sheets)

| Card | Primary Value | Sub-Text / Comparison | Color Indicator |
| :--- | :--- | :--- | :--- |
| **KPI 1: Total Net Revenue** | `SUM([net_sales])` (Format: `$#,##0.0,, "M"`) | `$957.7M Gross Sales • 11.6% Avg Disc` | `#0f172a` (Slate Dark) |
| **KPI 2: MoM Growth %** | `[MoM Sales Growth %]` (Format: `+0.0%;-0.0%`) | `vs Previous Month` | `IF >=0 THEN #10b981 ELSE #ef4444` |
| **KPI 3: QoQ Growth %** | `[QoQ Sales Growth %]` (Format: `+0.0%;-0.0%`) | `vs Previous Quarter` | `IF >=0 THEN #10b981 ELSE #ef4444` |
| **KPI 4: Active HCPs** | `COUNTD([hcp_id])` (Format: `#,##0`) | `Across 6 Specialties` | `#2563eb` (Royal Blue) |
| **KPI 5: Top Contributor** | `[Top Drug Name (LOD)]` | `23.3% of Total Revenue` | `#8b5cf6` (Purple) |

---

### Sheet 1: Monthly Sales Trend (Seasonality Dynamics)
- **Chart Type**: Dual-Axis Line & Band Chart
- **Columns**: `MONTH([date])` (Continuous Date-Value)
- **Rows**: `SUM([net_sales])` & `SUM([units_sold])` (Dual Axis)
- **Marks**:
  - Axis 1 (Sales): Line (`#1d4ed8`, size = 3), Circles on vertices.
  - Axis 2 (Units): Bar chart (opacity = 20%, `#94a3b8`).
- **Reference Bands**:
  - Band 1: `2024-06-01` to `2024-08-31` & `2025-06-01` to `2025-08-31` (Label: "Summer Dip")
  - Band 2: `2024-10-01` to `2024-12-31` & `2025-10-01` to `2025-12-31` (Label: "Q4 Surge")
- **Tooltip**: Include Month, Net Revenue, YoY Growth %, Units Sold, and Top Therapeutic Area.

---

### Sheet 2: Quarterly KPI Matrix (Heatmap Table)
- **Chart Type**: Highlight Table (Heatmap)
- **Columns**: `YEAR([date])`, `QUARTER([date])`
- **Rows**: `[therapeutic_area]`, `[channel]`
- **Marks**: Square
  - **Color**: `[QoQ Sales Growth %]` (Diverging Palette: Red `#dc2626` &harr; White &harr; Green `#16a34a`)
  - **Label**: Text with `SUM([net_sales])` (Format: `$#,##0.0,, "M"`) and `[QoQ Sales Growth %]` below.

---

### Sheet 3: Top 10 Drugs Performance (Horizontal Bar Chart)
- **Chart Type**: Horizontal Ranked Bar Chart
- **Columns**: `SUM([net_sales])`
- **Rows**: `[drug_name]` (Sorted by `SUM([net_sales])` Descending)
- **Filter**: `[Drug Revenue Rank] <= 10`
- **Marks**: Bar
  - **Color**: `[therapeutic_area]` (Cardiology = `#3b82f6`, Oncology = `#ec4899`, Neurology = `#8b5cf6`, Diabetes = `#10b981`)
  - **Label**: `SUM([net_sales])` + `[% of Total Portfolio Revenue]`
- **Tooltip**: Drug Name, Therapeutic Area, Standard Price, Prescribing HCP Count, Net Sales.

---

### Sheet 4: Territory Performance Map (Geographic / Choropleth View)
- **Chart Type**: Filled Map / Symbol Map
- **Detail**: `[territory]`, `[region]`
- **Marks**: Map Shapes / Polygonal Filled Areas
  - **Color**: `[% of Target Achieved]` (Stepped Color Palette: Red for `<70%`, Yellow for `70-99%`, Blue/Green for `100%+`)
  - **Size** (if symbol): `SUM([net_sales])`
  - **Label**: `[territory]` + `[% of Target Achieved]`
- **Alert Annotations**: Automatically call out `North-Plains`, `South-Delta`, and `West-Desert` with callout boxes.

---

### Sheet 5: HCP RFM Segment Treemap
- **Chart Type**: Treemap
- **Detail**: `[rfm_segment]`, `[hcp_specialty]`
- **Marks**: Box
  - **Size**: `SUM([net_sales])`
  - **Color**: `[rfm_segment]` (Champions = `#1e3a8a`, Loyal = `#3b82f6`, High-Value Specialty = `#8b5cf6`, Potential = `#f59e0b`, At-Risk = `#ef4444`)
  - **Label**: `[rfm_segment]`, `COUNTD([hcp_id])` ("# Doctors"), `SUM([net_sales])` ("$ Revenue")

---

### Sheet 6: Region × Therapeutic Area Breakdown Matrix
- **Chart Type**: 2x2 Heatmap Tile / Stacked Bar Comparison
- **Columns**: `[region]`
- **Rows**: `[therapeutic_area]`
- **Marks**: Circle or Heatmap Square
  - **Size**: `SUM([units_sold])`
  - **Color**: `SUM([net_sales])`
  - **Tooltip**: Detail share of region's revenue originating from each specialty.

---

## 🎚️ 5. Global Filter Configuration

Place these filters in a dedicated collapsible left sidebar or top filter ribbon:
1. **Date Range**: Range of Dates slider (`2024-01-01` to `2025-12-31`)
2. **Region**: Multi-select dropdown (`All`, `North`, `South`, `East`, `West`)
3. **Therapeutic Area**: Multi-select dropdown (`Cardiology`, `Oncology`, `Neurology`, `Diabetes`)
4. **Drug**: Searchable multi-select dropdown (14 drugs)
5. **Channel**: Multi-select dropdown (`Retail`, `Hospital`, `Online`)
*Set all filters to "Apply to Selected Worksheets &rarr; All Using Related Data Sources".*

---

## ⚡ 6. Interactive Dashboard Actions

1. **Territory Filter Action**:
   - *Source*: Sheet 4 (Territory Map)
   - *Action*: Select &rarr; Filters Sheets 1, 3, 5, and 6 to only show data for the clicked territory.
2. **Drug Highlight Action**:
   - *Source*: Sheet 3 (Top 10 Drugs)
   - *Action*: Hover &rarr; Highlights drug sales across Sheet 1 (Trend) and Sheet 6 (Matrix).
3. **HCP Segment Filter Action**:
   - *Source*: Sheet 5 (HCP Treemap)
   - *Action*: Select &rarr; Filters Sheet 3 & 4 to show drug preferences and geographic dispersion of that specific doctor cohort.

---

## 🎨 7. Dashboard Visual Layout (1920 × 1080 Full HD)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  💊 PHARMA COMMERCIAL SALES ANALYTICS DASHBOARD               [Date Range: 2024-01-01 - 2025-12-31]   │
├──────────────┬──────────────┬──────────────┬──────────────┬────────────────────────┬──────────────────┤
│ TOTAL SALES  │ MOM GROWTH   │ QOQ GROWTH   │ ACTIVE HCPS  │ TOP DRUG REVENUE       │ PARAMETERS       │
│   $848.55M   │   +14.6%     │   +34.1%     │     800      │ Oncozap ($197.6M)      │ Target: 100% (▼) │
│ Gross:$957.7M│  ▲ Oct-Dec   │  Q4 Spikes   │ 6 Specialties│ 23.3% Portfolio Share  │ Metric: Net Sales│
├──────────────┴──────────────┴──────────────┴──────────────┴────────────────────────┴──────────────────┤
│ 📈 MONTHLY SALES TREND & SEASONALITY (Sheet 1)             │ 🏆 TOP 10 DRUGS BY REVENUE (Sheet 3)     │
│ [Line Chart: 24 Months showing Summer Dip & Q4 Spike]     │ [Horizontal Bars colored by TA]          │
│                                                            │  1. Oncozap (Oncology)   ██████████ $198M│
│                                                            │  2. Glycaheal (Diabetes) ██████ $120M    │
│                                                            │  3. Tumorkill (Oncology) █████ $115M     │
├────────────────────────────────────────────────────────────┼──────────────────────────────────────────┤
│ 🗺️ TERRITORY PERFORMANCE MAP (Sheet 4)                     │ 👥 HCP RFM SEGMENT TREEMAP (Sheet 5)     │
│ [Geo Map: Color = % to Target Benchmark]                   │ [Champions | Loyal | Specialty | At-Risk]│
│ • Flagging: North-Plains, South-Delta, West-Desert (<70%)  │                                          │
├────────────────────────────────────────────────────────────┴──────────────────────────────────────────┤
│ 🏢 REGION × THERAPEUTIC AREA MATRIX (Sheet 6)   │ 📊 QUARTERLY KPI GROWTH HEATMAP (Sheet 2)            │
│ [North, South, East, West vs 4 TA Categories]   │ [Q1-Q4 YoY/QoQ Growth Matrix with Diverging Colors]  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
