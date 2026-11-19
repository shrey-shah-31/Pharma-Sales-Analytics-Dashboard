"""
Synthetic Pharma Sales Data Generator
Generates a realistic pharmaceutical sales dataset with 100,000+ rows.
Includes:
- 2-year daily timeline with Q4 spike and summer dip seasonality
- 20 territories across 4 regions with 15% underperforming territories (~30-40% below mean)
- 14 drugs across 4 therapeutic areas where Top 3 drugs contribute ~50% revenue
- Realistic HCPs, Sales Reps, pricing, discounts, and channel dynamics
- Export as pharma_sales.csv
"""

import os
import csv
import datetime
from collections import defaultdict
import numpy as np
from faker import Faker

def generate_pharma_dataset(num_rows=115000, seed=42, output_path="pharma_sales.csv"):
    np.random.seed(seed)
    fake = Faker()
    Faker.seed(seed)

    print(f"Generating synthetic pharma sales dataset ({num_rows:,} rows)...")

    # 1. Therapeutic Areas & Drugs (14 drugs)
    # Calibrated base prices and selection weights so top 3 drugs contribute ~50% total revenue
    drugs = [
        # Cardiology (4 drugs)
        {"drug_id": "DRG-CARD-001", "drug_name": "Cardioguard (Metoprolol)", "therapeutic_area": "Cardiology", "unit_price": 75.0, "weight": 0.085, "unit_base": 32},
        {"drug_id": "DRG-CARD-002", "drug_name": "Lipidex (Atorvastatin)", "therapeutic_area": "Cardiology", "unit_price": 55.0, "weight": 0.090, "unit_base": 38},
        {"drug_id": "DRG-CARD-003", "drug_name": "Vasotens (Amlodipine)", "therapeutic_area": "Cardiology", "unit_price": 60.0, "weight": 0.080, "unit_base": 32},
        {"drug_id": "DRG-CARD-004", "drug_name": "Coroxin (Apixaban)", "therapeutic_area": "Cardiology", "unit_price": 360.0, "weight": 0.085, "unit_base": 22}, # Top Contributor #3
        
        # Oncology (3 drugs)
        {"drug_id": "DRG-ONC-001", "drug_name": "Oncozap (Pembrolizumab)", "therapeutic_area": "Oncology", "unit_price": 1620.0, "weight": 0.070, "unit_base": 14}, # Top Contributor #1
        {"drug_id": "DRG-ONC-002", "drug_name": "Tumorkill (Trastuzumab)", "therapeutic_area": "Oncology", "unit_price": 1280.0, "weight": 0.060, "unit_base": 12}, # Top Contributor #2
        {"drug_id": "DRG-ONC-003", "drug_name": "Cellstop (Lenalidomide)", "therapeutic_area": "Oncology", "unit_price": 860.0, "weight": 0.050, "unit_base": 11},
        
        # Neurology (4 drugs)
        {"drug_id": "DRG-NEUR-001", "drug_name": "Neuroflux (Donepezil)", "therapeutic_area": "Neurology", "unit_price": 95.0, "weight": 0.075, "unit_base": 28},
        {"drug_id": "DRG-NEUR-002", "drug_name": "Synapsis (Levetiracetam)", "therapeutic_area": "Neurology", "unit_price": 125.0, "weight": 0.070, "unit_base": 25},
        {"drug_id": "DRG-NEUR-003", "drug_name": "Migrarelief (Erenumab)", "therapeutic_area": "Neurology", "unit_price": 520.0, "weight": 0.060, "unit_base": 14},
        {"drug_id": "DRG-NEUR-004", "drug_name": "Cerebrox (Memantine)", "therapeutic_area": "Neurology", "unit_price": 105.0, "weight": 0.060, "unit_base": 22},
        
        # Diabetes (3 drugs)
        {"drug_id": "DRG-DIAB-001", "drug_name": "Glucoprime (Metformin)", "therapeutic_area": "Diabetes", "unit_price": 38.0, "weight": 0.095, "unit_base": 48},
        {"drug_id": "DRG-DIAB-002", "drug_name": "Insuluxe (Insulin Glargine)", "therapeutic_area": "Diabetes", "unit_price": 295.0, "weight": 0.080, "unit_base": 20},
        {"drug_id": "DRG-DIAB-003", "drug_name": "Glycaheal (Semaglutide)", "therapeutic_area": "Diabetes", "unit_price": 750.0, "weight": 0.085, "unit_base": 15},
    ]
    drug_probs = np.array([d["weight"] for d in drugs])
    drug_probs /= drug_probs.sum()

    # 2. Geographic Hierarchy (4 Regions, 20 Territories)
    regions = {
        "North": ["North-Metro", "North-Central", "North-Lakes", "North-Valley", "North-Plains"],
        "South": ["South-Gulf", "South-Coast", "South-Delta", "South-Piedmont", "South-Highlands"],
        "East": ["East-Atlantic", "East-Metro", "East-NewEngland", "East-TriState", "East-Appalachia"],
        "West": ["West-Pacific", "West-Desert", "West-BayArea", "West-Northwest", "West-Rockies"]
    }
    
    territory_to_region = {}
    all_territories = []
    for reg, terrs in regions.items():
        for terr in terrs:
            territory_to_region[terr] = reg
            all_territories.append(terr)
            
    # 15% underperforming territories (3 out of 20 territories: ~30-40% below mean)
    underperforming_territories = set(["North-Plains", "South-Delta", "West-Desert"])
    territory_weights = []
    for terr in all_territories:
        if terr in underperforming_territories:
            territory_weights.append(0.78) # Lower transaction frequency
        else:
            territory_weights.append(1.04)
    territory_weights = np.array(territory_weights) / np.sum(territory_weights)

    # 3. Sales Reps Pool (2 reps per territory = 40 reps)
    sales_reps_by_terr = defaultdict(list)
    rep_counter = 101
    for terr in all_territories:
        for _ in range(2):
            rep_id = f"REP-{rep_counter:03d}"
            rep_name = fake.name()
            sales_reps_by_terr[terr].append((rep_id, rep_name))
            rep_counter += 1

    # 4. HCP Pool (800 Doctors across specialties)
    specialties = [
        "Cardiology", "Oncology", "Neurology", "Endocrinology", 
        "Internal Medicine", "Family Medicine"
    ]
    specialty_probs = [0.20, 0.15, 0.15, 0.20, 0.15, 0.15]
    
    hcps_by_terr = defaultdict(list)
    all_hcps = []
    for i in range(1, 801):
        hcp_id = f"HCP-{i:04d}"
        hcp_name = f"Dr. {fake.first_name()} {fake.last_name()}"
        hcp_spec = np.random.choice(specialties, p=specialty_probs)
        hcp_terr = np.random.choice(all_territories, p=territory_weights)
        hcp_obj = (hcp_id, hcp_name, hcp_spec, hcp_terr)
        hcps_by_terr[hcp_terr].append(hcp_obj)
        all_hcps.append(hcp_obj)

    # 5. Date Generation with Seasonality (2 Years: 2024-01-01 to 2025-12-31)
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    total_days = (end_date - start_date).days + 1
    date_range = [start_date + datetime.timedelta(days=x) for x in range(total_days)]
    
    date_weights = []
    for d in date_range:
        month = d.month
        weekday = d.weekday() # 0 = Monday, 6 = Sunday
        
        weight = 1.0
        # Q4 spike (Oct, Nov, Dec): high deductible clearance, hospital budget fulfillment
        if month == 10:
            weight *= 1.30
        elif month == 11:
            weight *= 1.42
        elif month == 12:
            weight *= 1.55
        # Summer dip (Jun, Jul, Aug): seasonal slowdown
        elif month == 6:
            weight *= 0.85
        elif month == 7:
            weight *= 0.78
        elif month == 8:
            weight *= 0.82
        elif month in (1, 2):
            weight *= 0.92
            
        # Day of week pattern: lower weekend sales (pharmacies/hospitals order less on weekends)
        if weekday in (5, 6):
            weight *= 0.50
        else:
            weight *= 1.20
            
        date_weights.append(weight)
        
    date_weights = np.array(date_weights) / np.sum(date_weights)

    # 6. Sampling
    print("Vectorized sampling of rows...")
    sampled_date_indices = np.random.choice(len(date_range), size=num_rows, p=date_weights)
    sampled_territory_indices = np.random.choice(len(all_territories), size=num_rows, p=territory_weights)
    sampled_drug_indices = np.random.choice(len(drugs), size=num_rows, p=drug_probs)
    
    channels = ["Retail", "Hospital", "Online"]
    channel_probs = [0.50, 0.35, 0.15]
    sampled_channels = np.random.choice(channels, size=num_rows, p=channel_probs)

    # Sort sampled transactions chronologically
    sort_order = np.argsort(sampled_date_indices)
    sampled_date_indices = sampled_date_indices[sort_order]
    sampled_territory_indices = sampled_territory_indices[sort_order]
    sampled_drug_indices = sampled_drug_indices[sort_order]
    sampled_channels = sampled_channels[sort_order]

    # Pre-generate noise for prices and quantities
    price_noise = 1.0 + np.random.uniform(-0.02, 0.02, size=num_rows)
    quantity_noise = np.random.gamma(shape=3.5, scale=0.3, size=num_rows) # positive right-skewed multiplier

    fieldnames = [
        "transaction_id", "date", "drug_id", "drug_name", "therapeutic_area",
        "region", "territory", "hcp_id", "hcp_name", "hcp_specialty",
        "sales_rep_id", "sales_rep_name", "units_sold", "unit_price",
        "total_sales", "discount_pct", "net_sales", "channel"
    ]

    print(f"Writing dataset to {output_path}...")
    
    # Validation accumulators
    total_gross_sales = 0.0
    total_net_sales = 0.0
    monthly_sales = defaultdict(float)
    territory_sales = defaultdict(lambda: {"count": 0, "net_sales": 0.0})
    drug_sales = defaultdict(lambda: {"count": 0, "net_sales": 0.0, "name": "", "ta": ""})

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_rows):
            txn_id = f"TXN-{(i + 1):07d}"
            date_obj = date_range[sampled_date_indices[i]]
            date_str = date_obj.strftime("%Y-%m-%d")
            
            terr = all_territories[sampled_territory_indices[i]]
            region = territory_to_region[terr]
            
            drug = drugs[sampled_drug_indices[i]]
            channel = sampled_channels[i]

            # Sales Rep
            reps = sales_reps_by_terr[terr]
            rep_idx = np.random.randint(len(reps))
            rep_id, rep_name = reps[rep_idx]

            # HCP
            hcp_pool = hcps_by_terr[terr] if (terr in hcps_by_terr and len(hcps_by_terr[terr]) > 0 and np.random.rand() < 0.80) else all_hcps
            hcp_idx = np.random.randint(len(hcp_pool))
            hcp_id, hcp_name, hcp_spec, _ = hcp_pool[hcp_idx]

            # Pricing
            unit_price = round(drug["unit_price"] * price_noise[i], 2)

            # Units Sold
            channel_mult = 1.8 if channel == "Hospital" else (0.75 if channel == "Online" else 1.0)
            underperf_mult = 0.84 if terr in underperforming_territories else 1.0
            
            raw_units = drug["unit_base"] * channel_mult * underperf_mult * quantity_noise[i]
            units_sold = max(1, int(round(raw_units)))

            # Total Sales
            total_sale = round(units_sold * unit_price, 2)

            # Discounts
            if channel == "Hospital":
                disc = np.random.uniform(0.10, 0.25)
            elif channel == "Online":
                disc = np.random.uniform(0.05, 0.15)
            else: # Retail
                disc = np.random.uniform(0.00, 0.08)
            discount_pct = round(disc, 4)

            net_sale = round(total_sale * (1.0 - discount_pct), 2)

            row = {
                "transaction_id": txn_id,
                "date": date_str,
                "drug_id": drug["drug_id"],
                "drug_name": drug["drug_name"],
                "therapeutic_area": drug["therapeutic_area"],
                "region": region,
                "territory": terr,
                "hcp_id": hcp_id,
                "hcp_name": hcp_name,
                "hcp_specialty": hcp_spec,
                "sales_rep_id": rep_id,
                "sales_rep_name": rep_name,
                "units_sold": units_sold,
                "unit_price": unit_price,
                "total_sales": total_sale,
                "discount_pct": discount_pct,
                "net_sales": net_sale,
                "channel": channel
            }
            writer.writerow(row)

            # Accumulate statistics
            total_gross_sales += total_sale
            total_net_sales += net_sale
            monthly_sales[date_obj.month] += net_sale
            
            t_stat = territory_sales[terr]
            t_stat["count"] += 1
            t_stat["net_sales"] += net_sale

            d_stat = drug_sales[drug["drug_id"]]
            d_stat["count"] += 1
            d_stat["net_sales"] += net_sale
            d_stat["name"] = drug["drug_name"]
            d_stat["ta"] = drug["therapeutic_area"]

    print("File export complete!")
    print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

    # Print Summary & Pattern Validation
    print("\n" + "="*60)
    print("DATASET VALIDATION REPORT")
    print("="*60)
    print(f"Total Transactions : {num_rows:,}")
    print(f"Date Timeline      : {date_range[0]} to {date_range[-1]} (2 Full Years)")
    print(f"Total Gross Sales  : ${total_gross_sales:,.2f}")
    print(f"Total Net Sales    : ${total_net_sales:,.2f}")

    # 1. Seasonality
    print("\n[1] SEASONALITY (Q4 SPIKE & SUMMER DIP)")
    print("-" * 50)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m in range(1, 13):
        m_rev = monthly_sales[m]
        pct = (m_rev / total_net_sales) * 100
        bar = "#" * int(pct * 2.5)
        print(f"  {month_names[m-1]:<4}: ${m_rev:,.2f} ({pct:5.2f}%) {bar}")

    q4_rev = monthly_sales[10] + monthly_sales[11] + monthly_sales[12]
    summer_rev = monthly_sales[6] + monthly_sales[7] + monthly_sales[8]
    print(f"\n  >> Q4 (Oct-Dec) Share     : {(q4_rev / total_net_sales)*100:.2f}% (Expected ~32-35%)")
    print(f"  >> Summer (Jun-Aug) Share : {(summer_rev / total_net_sales)*100:.2f}% (Expected ~19-21%)")

    # 2. Territory Performance
    print("\n[2] TERRITORY PERFORMANCE (15% UNDERPERFORMING)")
    print("-" * 50)
    mean_terr_rev = total_net_sales / len(all_territories)
    print(f"  Territory Revenue Benchmark Mean: ${mean_terr_rev:,.2f}\n")
    for terr in all_territories:
        t_rev = territory_sales[terr]["net_sales"]
        t_cnt = territory_sales[terr]["count"]
        diff = (t_rev - mean_terr_rev) / mean_terr_rev * 100
        status = "[UNDERPERFORMING ~30-40% BELOW]" if terr in underperforming_territories else "[Normal]"
        print(f"  {terr:<18} | Txns: {t_cnt:6,} | Rev: ${t_rev:,.2f} ({diff:+6.1f}%) {status}")

    # 3. Drug Revenue Share (Top 3 Drugs ~50%)
    print("\n[3] DRUG REVENUE DISTRIBUTION (TOP 3 DRUGS SHARE)")
    print("-" * 50)
    sorted_drugs = sorted(drug_sales.items(), key=lambda x: x[1]["net_sales"], reverse=True)
    cum_share = 0.0
    for rank, (d_id, d_data) in enumerate(sorted_drugs, 1):
        share = (d_data["net_sales"] / total_net_sales) * 100
        cum_share += share
        star = " *** [TOP 3]" if rank <= 3 else ""
        print(f"  #{rank:02d} {d_data['name']:<28} [{d_data['ta']:<11}]: ${d_data['net_sales']:,.2f} ({share:5.2f}% | Cum: {cum_share:5.2f}%){star}")

    top3_total_share = sum(d[1]["net_sales"] for d in sorted_drugs[:3]) / total_net_sales * 100
    print(f"\n  >> TOP 3 DRUGS REVENUE SHARE: {top3_total_share:.2f}% (Target: ~50%)")
    print("="*60)

if __name__ == "__main__":
    generate_pharma_dataset(num_rows=115000, output_path="pharma_sales.csv")
