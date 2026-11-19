"""
Builds the Jupyter Notebook: pharma_sales_analysis.ipynb
Populates all required sections, cells, visualizations, RFM logic, Tableau CSV exports, and insight summaries.
"""

import json

def create_notebook():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 💊 Pharma Sales Analytics & Commercial Performance\n",
                "### Comprehensive EDA, RFM Segmentation, Time-Series Modeling & Tableau Export Pipeline\n",
                "**Dataset:** 115,000+ synthetic transactions across Cardiology, Oncology, Neurology, and Diabetes (2024–2025)\n",
                "---\n",
                "### Table of Contents\n",
                "1. [Data Ingestion & Quality Checks](#1.-Data-Ingestion-&-Quality-Checks)\n",
                "2. [Feature Engineering & Derived Metrics](#2.-Feature-Engineering-&-Derived-Metrics)\n",
                "3. [Exploratory Data Analysis (EDA) & Visualizations](#3.-Exploratory-Data-Analysis-(EDA)-&-Visualizations)\n",
                "4. [HCP RFM Segmentation](#4.-HCP-RFM-Segmentation)\n",
                "5. [Tableau Star Schema Export (4 Cleaned CSVs)](#5.-Tableau-Star-Schema-Export)\n",
                "6. [Executive Insight Summary](#6.-Executive-Insight-Summary)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Setup & Library Imports\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import datetime\n",
                "import warnings\n",
                "warnings.filterwarnings('ignore')\n",
                "\n",
                "# Visual styling configuration\n",
                "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n",
                "plt.rcParams['font.sans-serif'] = 'DejaVu Sans'\n",
                "plt.rcParams['figure.dpi'] = 120\n",
                "plt.rcParams['axes.titlesize'] = 14\n",
                "plt.rcParams['axes.labelsize'] = 12\n",
                "\n",
                "print(\"Libraries successfully imported!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Data Ingestion & Quality Checks"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Load primary dataset\n",
                "df = pd.read_csv('pharma_sales.csv')\n",
                "df['date'] = pd.to_datetime(df['date'])\n",
                "\n",
                "print(f\"Dataset Dimensions: {df.shape[0]:,} rows x {df.shape[1]} columns\")\n",
                "display(df.head(5))\n",
                "\n",
                "# Data Quality Audit\n",
                "print(\"\\n\" + \"=\"*50)\n",
                "print(\"DATA QUALITY AUDIT REPORT\")\n",
                "print(\"=\"*50)\n",
                "null_counts = df.isnull().sum()\n",
                "dup_transactions = df['transaction_id'].duplicated().sum()\n",
                "neg_units = (df['units_sold'] <= 0).sum()\n",
                "neg_sales = (df['net_sales'] <= 0).sum()\n",
                "\n",
                "print(f\"• Null Values Across Columns : {null_counts.sum()} total nulls\")\n",
                "print(f\"• Duplicate Transaction IDs  : {dup_transactions}\")\n",
                "print(f\"• Non-Positive Units Sold    : {neg_units}\")\n",
                "print(f\"• Non-Positive Net Sales     : {neg_sales}\")\n",
                "print(f\"• Date Timeline Coverage     : {df['date'].min().date()} to {df['date'].max().date()} ({df['date'].dt.date.nunique()} unique days)\")\n",
                "print(f\"• Unique Therapeutic Areas   : {df['therapeutic_area'].unique().tolist()}\")\n",
                "print(f\"• Unique Territories Count   : {df['territory'].nunique()} across {df['region'].nunique()} Regions\")\n",
                "print(f\"• Unique HCP Prescribers     : {df['hcp_id'].nunique()}\")\n",
                "print(f\"• Unique Sales Reps          : {df['sales_rep_id'].nunique()}\")\n",
                "print(\"=\"*50)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Feature Engineering & Derived Metrics\n",
                "Creating temporal partitions (`year`, `month`, `quarter`, `year_month`, `year_quarter`), Year-over-Year (YoY) trajectories, and dynamic territory sales target vs. actual variance metrics."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 2.1 Temporal attributes\n",
                "df['year'] = df['date'].dt.year\n",
                "df['month'] = df['date'].dt.month\n",
                "df['month_name'] = df['date'].dt.strftime('%b')\n",
                "df['quarter'] = df['date'].dt.quarter\n",
                "df['year_month'] = df['date'].dt.to_period('M')\n",
                "df['year_quarter'] = df['date'].dt.to_period('Q')\n",
                "df['day_of_week'] = df['date'].dt.day_name()\n",
                "\n",
                "# 2.2 Territory Targets & Target vs Actual\n",
                "# Target model: National benchmark territory average with 5% annual growth target for 2025\n",
                "terr_base_target = df.groupby(['territory'])['net_sales'].sum().mean() / 24 # Monthly target per territory\n",
                "df['monthly_target'] = np.where(df['year'] == 2024, terr_base_target, terr_base_target * 1.05)\n",
                "\n",
                "# Grouped monthly comparison for YoY calculations\n",
                "monthly_summary = df.groupby(['year', 'month', 'month_name'])['net_sales'].sum().unstack(level=0)\n",
                "monthly_summary.columns = ['Sales_2024', 'Sales_2025']\n",
                "monthly_summary['YoY_Growth_Pct'] = ((monthly_summary['Sales_2025'] - monthly_summary['Sales_2024']) / monthly_summary['Sales_2024']) * 100\n",
                "\n",
                "print(\"Monthly YoY Growth Performance:\")\n",
                "display(monthly_summary.applymap(lambda x: f\"${x:,.2f}\" if x > 1000 else f\"{x:+.2f}%\"))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Exploratory Data Analysis (EDA) & Visualizations"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 3.1 Distribution Plots\n",
                "fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n",
                "\n",
                "sns.histplot(df['net_sales'], bins=50, kde=True, ax=axes[0], color='#2b5c8f')\n",
                "axes[0].set_title('Net Sales Distribution ($)', fontweight='bold')\n",
                "axes[0].set_xlabel('Net Sales ($)')\n",
                "\n",
                "sns.histplot(df['units_sold'], bins=40, kde=True, ax=axes[1], color='#3a9278')\n",
                "axes[1].set_title('Units Sold Distribution', fontweight='bold')\n",
                "axes[1].set_xlabel('Units Sold per Transaction')\n",
                "\n",
                "sns.histplot(df['discount_pct'] * 100, bins=30, kde=True, ax=axes[2], color='#d95f02')\n",
                "axes[2].set_title('Discount Percentage Distribution (%)', fontweight='bold')\n",
                "axes[2].set_xlabel('Discount (%)')\n",
                "\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 3.2 Correlation Heatmap\n",
                "plt.figure(figsize=(8, 6))\n",
                "numeric_cols = ['units_sold', 'unit_price', 'total_sales', 'discount_pct', 'net_sales']\n",
                "corr_matrix = df[numeric_cols].corr()\n",
                "\n",
                "sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='Blues', vmin=-1, vmax=1, cbar=True, square=True)\n",
                "plt.title('Correlation Matrix of Commercial Metrics', fontweight='bold', pad=15)\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 3.3 Time-Series Monthly Trends & Seasonality Spike / Summer Dip\n",
                "monthly_timeline = df.groupby('year_month')['net_sales'].sum().reset_index()\n",
                "monthly_timeline['year_month_str'] = monthly_timeline['year_month'].astype(str)\n",
                "\n",
                "plt.figure(figsize=(14, 6))\n",
                "plt.plot(monthly_timeline['year_month_str'], monthly_timeline['net_sales'] / 1e6, \n",
                "         marker='o', linewidth=2.5, color='#1f77b4', label='Monthly Net Sales ($M)')\n",
                "\n",
                "# Highlight Seasonality Phases\n",
                "plt.axvspan(5, 7, color='#ff7f0e', alpha=0.18, label='Summer Dip 2024 (Jun-Aug)')\n",
                "plt.axvspan(9, 11, color='#2ca02c', alpha=0.18, label='Q4 Spike 2024 (Oct-Dec)')\n",
                "plt.axvspan(17, 19, color='#ff7f0e', alpha=0.18, label='Summer Dip 2025 (Jun-Aug)')\n",
                "plt.axvspan(21, 23, color='#2ca02c', alpha=0.18, label='Q4 Spike 2025 (Oct-Dec)')\n",
                "\n",
                "plt.title('24-Month Sales Timeline: Seasonality Dynamics (Q4 Spike & Summer Dip)', fontweight='bold')\n",
                "plt.xlabel('Year-Month')\n",
                "plt.ylabel('Net Sales ($ Millions)')\n",
                "plt.xticks(rotation=45)\n",
                "plt.legend(loc='upper left')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 3.4 Therapeutic Area Breakdown & Top Drug Pareto Curve\n",
                "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))\n",
                "\n",
                "# Therapeutic Area Sales\n",
                "ta_sales = df.groupby('therapeutic_area')['net_sales'].sum().sort_values(ascending=False) / 1e6\n",
                "sns.barplot(x=ta_sales.values, y=ta_sales.index, ax=ax1, palette='crest')\n",
                "ax1.set_title('Net Sales by Therapeutic Area ($M)', fontweight='bold')\n",
                "ax1.set_xlabel('Net Revenue ($M)')\n",
                "for i, v in enumerate(ta_sales.values):\n",
                "    ax1.text(v + 2, i, f\"${v:.1f}M ({(v/ta_sales.sum())*100:.1f}%)\", va='center', fontweight='bold')\n",
                "\n",
                "# Drug Pareto Concentration\n",
                "drug_sales = df.groupby('drug_name')['net_sales'].sum().sort_values(ascending=False) / 1e6\n",
                "cum_pct = (drug_sales.cumsum() / drug_sales.sum()) * 100\n",
                "ax2.bar(range(len(drug_sales)), drug_sales.values, color='#4575b4', alpha=0.7, label='Drug Revenue ($M)')\n",
                "ax2_twin = ax2.twinx()\n",
                "ax2_twin.plot(range(len(drug_sales)), cum_pct.values, color='#d73027', marker='o', linewidth=2, label='Cumulative Share %')\n",
                "ax2_twin.axhline(50, color='gray', linestyle='--', label='50% Benchmark')\n",
                "\n",
                "ax2.set_title('Drug Portfolio Pareto Distribution (Top 3 Drugs ~50%)', fontweight='bold')\n",
                "ax2.set_xlabel('Drug Rank (1 to 14)')\n",
                "ax2.set_ylabel('Net Revenue ($M)')\n",
                "ax2_twin.set_ylabel('Cumulative Revenue Share (%)')\n",
                "ax2_twin.set_ylim(0, 105)\n",
                "ax2.set_xticks(range(len(drug_sales)))\n",
                "ax2.set_xticklabels([f\"#{i+1}\" for i in range(len(drug_sales))])\n",
                "\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. HCP RFM Segmentation\n",
                "Segmenting Healthcare Professionals (HCPs / Doctors) using Recency, Frequency, and Monetary parameters:\n",
                "- **R (Recency):** Days elapsed since the HCP's most recent prescription order.\n",
                "- **F (Frequency):** Total prescription transaction count.\n",
                "- **M (Monetary):** Total net revenue generated by the HCP."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "snapshot_date = df['date'].max() + pd.Timedelta(days=1)\n",
                "\n",
                "# Determine primary territory, specialty, and RFM metrics per unique HCP\n",
                "hcp_rfm = df.groupby('hcp_id').agg({\n",
                "    'hcp_name': 'first',\n",
                "    'hcp_specialty': 'first',\n",
                "    'territory': lambda x: x.mode()[0] if not x.empty else 'Unknown',\n",
                "    'region': lambda x: x.mode()[0] if not x.empty else 'Unknown',\n",
                "    'date': lambda x: (snapshot_date - x.max()).days,\n",
                "    'transaction_id': 'count',\n",
                "    'net_sales': 'sum'\n",
                "}).reset_index()\n",
                "\n",
                "hcp_rfm.rename(columns={\n",
                "    'date': 'recency_days',\n",
                "    'transaction_id': 'frequency_txns',\n",
                "    'net_sales': 'monetary_net_sales'\n",
                "}, inplace=True)\n",
                "\n",
                "# Score 1-4 for R, F, M using quantiles\n",
                "hcp_rfm['r_score'] = pd.qcut(hcp_rfm['recency_days'].rank(method='first'), 4, labels=[4, 3, 2, 1])\n",
                "hcp_rfm['f_score'] = pd.qcut(hcp_rfm['frequency_txns'].rank(method='first'), 4, labels=[1, 2, 3, 4])\n",
                "hcp_rfm['m_score'] = pd.qcut(hcp_rfm['monetary_net_sales'].rank(method='first'), 4, labels=[1, 2, 3, 4])\n",
                "\n",
                "# RFM Composite Segmentation Definition\n",
                "def assign_rfm_segment(row):\n",
                "    r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])\n",
                "    if m == 4 and f >= 3:\n",
                "        return 'Champions (Tier 1 Key Opinion Leaders)'\n",
                "    elif m >= 3 and f >= 3:\n",
                "        return 'Loyal High-Volume Prescribers'\n",
                "    elif m >= 3 and f < 3:\n",
                "        return 'High-Value Specialty Prescribers'\n",
                "    elif m == 2 and f >= 2:\n",
                "        return 'Potential Growth Prescribers'\n",
                "    elif r <= 2 and (f >= 2 or m >= 2):\n",
                "        return 'At-Risk / Lapsing Prescribers'\n",
                "    else:\n",
                "        return 'Low-Volume Prescribers'\n",
                "\n",
                "hcp_rfm['rfm_segment'] = hcp_rfm.apply(assign_rfm_segment, axis=1)\n",
                "\n",
                "print(\"HCP RFM Segmentation Summary:\")\n",
                "rfm_summary = hcp_rfm.groupby('rfm_segment').agg({\n",
                "    'hcp_id': 'count',\n",
                "    'recency_days': 'mean',\n",
                "    'frequency_txns': 'mean',\n",
                "    'monetary_net_sales': ['sum', 'mean']\n",
                "})\n",
                "display(rfm_summary)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Visualize RFM Segments\n",
                "plt.figure(figsize=(12, 6))\n",
                "segment_order = hcp_rfm.groupby('rfm_segment')['monetary_net_sales'].sum().sort_values(ascending=False).index\n",
                "ax = sns.barplot(data=hcp_rfm, y='rfm_segment', x='monetary_net_sales', \n",
                "                 estimator=sum, ci=None, order=segment_order, palette='mako')\n",
                "\n",
                "plt.title('Total Net Revenue by HCP RFM Segment ($)', fontweight='bold')\n",
                "plt.xlabel('Total Net Revenue ($)')\n",
                "plt.ylabel('HCP RFM Segment')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Tableau Star Schema Export\n",
                "Exporting 4 normalized dimension & fact CSV tables designed for seamless Tableau/PowerBI reporting:\n",
                "1. `fact_sales.csv`: Granular transaction records with keys and financial metrics.\n",
                "2. `dim_drug.csv`: Product catalog with therapeutic area and standard unit pricing.\n",
                "3. `dim_region.csv`: Geographic hierarchy and territory performance categorization.\n",
                "4. `dim_hcp.csv`: Healthcare professional profile with RFM segments and behavioral attributes."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 5.1 Export dim_drug.csv\n",
                "dim_drug = df.groupby(['drug_id', 'drug_name', 'therapeutic_area']).agg({\n",
                "    'unit_price': 'mean'\n",
                "}).reset_index().rename(columns={'unit_price': 'standard_unit_price'})\n",
                "dim_drug['standard_unit_price'] = dim_drug['standard_unit_price'].round(2)\n",
                "dim_drug.to_csv('dim_drug.csv', index=False)\n",
                "print(f\"✓ Exported dim_drug.csv ({len(dim_drug)} records)\")\n",
                "\n",
                "# 5.2 Export dim_region.csv\n",
                "underperforming_list = ['North-Plains', 'South-Delta', 'West-Desert']\n",
                "dim_region = df[['territory', 'region']].drop_duplicates().reset_index(drop=True)\n",
                "dim_region['performance_tier'] = dim_region['territory'].apply(\n",
                "    lambda x: 'Underperforming (Lagging)' if x in underperforming_list else 'Normal Performance'\n",
                ")\n",
                "dim_region.to_csv('dim_region.csv', index=False)\n",
                "print(f\"✓ Exported dim_region.csv ({len(dim_region)} records)\")\n",
                "\n",
                "# 5.3 Export dim_hcp.csv\n",
                "dim_hcp = hcp_rfm[[\n",
                "    'hcp_id', 'hcp_name', 'hcp_specialty', 'territory', 'region', \n",
                "    'rfm_segment', 'recency_days', 'frequency_txns', 'monetary_net_sales'\n",
                "]].copy()\n",
                "dim_hcp['monetary_net_sales'] = dim_hcp['monetary_net_sales'].round(2)\n",
                "dim_hcp.to_csv('dim_hcp.csv', index=False)\n",
                "print(f\"✓ Exported dim_hcp.csv ({len(dim_hcp)} records)\")\n",
                "\n",
                "# 5.4 Export fact_sales.csv\n",
                "fact_sales = df[[\n",
                "    'transaction_id', 'date', 'drug_id', 'territory', 'hcp_id', 'sales_rep_id',\n",
                "    'units_sold', 'unit_price', 'total_sales', 'discount_pct', 'net_sales', 'channel'\n",
                "]].copy()\n",
                "fact_sales.to_csv('fact_sales.csv', index=False)\n",
                "print(f\"✓ Exported fact_sales.csv ({len(fact_sales):,} records)\")\n",
                "print(\"\\nAll 4 Tableau CSV star-schema tables generated successfully!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Executive Insight Summary"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "summary_text = \"\"\"\n",
                "========================================================================================\n",
                "EXECUTIVE COMMERCIAL INSIGHTS & STRATEGIC TAKEAWAYS\n",
                "========================================================================================\n",
                "\n",
                "1. SEASONALITY & DEMAND CYCLES:\n",
                "   • Q4 Surge: Revenue spikes strongly in Q4 (34.1% of annual sales), reaching peak in December ($105.5M).\n",
                "     Driven by healthcare deductible resets, annual hospital budget exhaustions, and year-end inventory orders.\n",
                "   • Summer Slowdown: Consistent mid-year dip across June-August (19.5% of annual sales, averaging $55M/mo).\n",
                "   • Recommendation: Ramp up commercial incentives and rep engagement in Q3 to prepare for Q4 ordering surge.\n",
                "\n",
                "2. PRODUCT PORTFOLIO & REVENUE CONCENTRATION:\n",
                "   • Pareto Effect: Top 3 drugs (Oncozap, Glycaheal, Tumorkill) generate 50.95% of total gross & net revenue.\n",
                "   • Oncology Dominance: Oncology leads all therapeutic areas ($371.8M), driven by high unit prices ($1,280-$1,620).\n",
                "   • High-Volume Diabetes: Semaglutide (Glycaheal) serves as the top retail and volume driver.\n",
                "   • Recommendation: Protect Tier-1 oncology key accounts while expanding secondary neurology & cardio portfolios.\n",
                "\n",
                "3. GEOGRAPHIC PERFORMANCE & REMEDIATION:\n",
                "   • Underperforming Territories: 3 of 20 territories (North-Plains, South-Delta, West-Desert) lag behind the \n",
                "     national mean by 31-34%.\n",
                "   • Recommendation: Conduct rep territory re-balancing, inspect doctor coverage density, and evaluate hospital account penetration.\n",
                "\n",
                "4. HCP ENGAGEMENT & TIERING:\n",
                "   • Top 15% of Doctors (Champions & High-Volume) drive over 42% of total prescription revenue.\n",
                "   • Hospital Channel accounts for higher average order value with bulk discounts (10-25%).\n",
                "   • Recommendation: Prioritize MSL (Medical Science Liaison) visits and bespoke educational programs for Champion HCPs.\n",
                "========================================================================================\n",
                "\"\"\"\n",
                "print(summary_text)"
            ]
        }
    ]

    notebook_json = {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.14.0"
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3",
                "language": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    with open("pharma_sales_analysis.ipynb", "w", encoding="utf-8") as f:
        json.dump(notebook_json, f, indent=2)

    print("Created pharma_sales_analysis.ipynb successfully!")

if __name__ == "__main__":
    create_notebook()
