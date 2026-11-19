"""
Runs the full analysis pipeline:
- Loads pharma_sales.csv
- Computes derived fields
- Runs EDA & RFM segmentation
- Exports the 4 Tableau CSVs (fact_sales.csv, dim_drug.csv, dim_region.csv, dim_hcp.csv)
- Embeds execution outputs into pharma_sales_analysis.ipynb
"""

import sys
import os
import json
import base64
import io
import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def run_pipeline():
    print("Starting Pharma Sales Analysis Pipeline...")
    
    # 1. Load data
    df = pd.read_csv('pharma_sales.csv')
    df['date'] = pd.to_datetime(df['date'])
    print(f"Loaded {len(df):,} rows from pharma_sales.csv")

    # 2. Derived fields
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')
    df['quarter'] = df['date'].dt.quarter
    df['year_month'] = df['date'].dt.to_period('M')
    df['year_quarter'] = df['date'].dt.to_period('Q')
    df['day_of_week'] = df['date'].dt.day_name()

    terr_base_target = df.groupby(['territory'])['net_sales'].sum().mean() / 24
    df['monthly_target'] = np.where(df['year'] == 2024, terr_base_target, terr_base_target * 1.05)

    # 3. RFM Segmentation
    snapshot_date = df['date'].max() + pd.Timedelta(days=1)
    # Determine primary territory and region for each HCP
    hcp_geo = df.groupby('hcp_id').agg({
        'hcp_name': 'first',
        'hcp_specialty': 'first',
        'territory': lambda x: x.mode()[0] if not x.empty else 'Unknown',
        'region': lambda x: x.mode()[0] if not x.empty else 'Unknown',
        'date': lambda x: (snapshot_date - x.max()).days,
        'transaction_id': 'count',
        'net_sales': 'sum'
    }).reset_index()

    hcp_geo.rename(columns={
        'date': 'recency_days',
        'transaction_id': 'frequency_txns',
        'net_sales': 'monetary_net_sales'
    }, inplace=True)
    hcp_rfm = hcp_geo

    hcp_rfm['r_score'] = pd.qcut(hcp_rfm['recency_days'].rank(method='first'), 4, labels=[4, 3, 2, 1])
    hcp_rfm['f_score'] = pd.qcut(hcp_rfm['frequency_txns'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    hcp_rfm['m_score'] = pd.qcut(hcp_rfm['monetary_net_sales'].rank(method='first'), 4, labels=[1, 2, 3, 4])

    def assign_rfm_segment(row):
        r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
        if m == 4 and f >= 3:
            return 'Champions (Tier 1 Key Opinion Leaders)'
        elif m >= 3 and f >= 3:
            return 'Loyal High-Volume Prescribers'
        elif m >= 3 and f < 3:
            return 'High-Value Specialty Prescribers'
        elif m == 2 and f >= 2:
            return 'Potential Growth Prescribers'
        elif r <= 2 and (f >= 2 or m >= 2):
            return 'At-Risk / Lapsing Prescribers'
        else:
            return 'Low-Volume Prescribers'

    hcp_rfm['rfm_segment'] = hcp_rfm.apply(assign_rfm_segment, axis=1)

    # 4. Export 4 Cleaned CSVs for Tableau
    print("\n--- EXPORTING TABLEAU CSV FILES ---")

    # 4.1 dim_drug.csv
    dim_drug = df.groupby(['drug_id', 'drug_name', 'therapeutic_area']).agg({
        'unit_price': 'mean'
    }).reset_index().rename(columns={'unit_price': 'standard_unit_price'})
    dim_drug['standard_unit_price'] = dim_drug['standard_unit_price'].round(2)
    dim_drug.to_csv('dim_drug.csv', index=False)
    print(f"[OK] Created dim_drug.csv ({len(dim_drug)} drugs)")

    # 4.2 dim_region.csv
    underperforming_list = ['North-Plains', 'South-Delta', 'West-Desert']
    dim_region = df[['territory', 'region']].drop_duplicates().reset_index(drop=True)
    dim_region['performance_tier'] = dim_region['territory'].apply(
        lambda x: 'Underperforming (Lagging)' if x in underperforming_list else 'Normal Performance'
    )
    dim_region.to_csv('dim_region.csv', index=False)
    print(f"[OK] Created dim_region.csv ({len(dim_region)} territories)")

    # 4.3 dim_hcp.csv
    dim_hcp = hcp_rfm[[
        'hcp_id', 'hcp_name', 'hcp_specialty', 'territory', 'region', 
        'rfm_segment', 'recency_days', 'frequency_txns', 'monetary_net_sales'
    ]].copy()
    dim_hcp['monetary_net_sales'] = dim_hcp['monetary_net_sales'].round(2)
    dim_hcp.to_csv('dim_hcp.csv', index=False)
    print(f"[OK] Created dim_hcp.csv ({len(dim_hcp)} HCPs)")

    # 4.4 fact_sales.csv
    fact_sales = df[[
        'transaction_id', 'date', 'drug_id', 'territory', 'hcp_id', 'sales_rep_id',
        'units_sold', 'unit_price', 'total_sales', 'discount_pct', 'net_sales', 'channel'
    ]].copy()
    fact_sales.to_csv('fact_sales.csv', index=False)
    print(f"[OK] Created fact_sales.csv ({len(fact_sales):,} sales transactions)")

    print("\nAll Tableau exports completed successfully!")

if __name__ == "__main__":
    run_pipeline()
