-- ==============================================================================
-- PHARMA SALES ANALYTICS - SQL QUERY SUITE (MySQL 8.0+ Syntax)
-- Dataset: Synthetic Pharma Sales (115,000+ Transactions, 2024-2025)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- DDL & Data Loading Reference (Optional Setup)
-- ------------------------------------------------------------------------------
/*
CREATE TABLE IF NOT EXISTS pharma_sales (
    transaction_id VARCHAR(30) PRIMARY KEY,
    date DATE NOT NULL,
    drug_id VARCHAR(30) NOT NULL,
    drug_name VARCHAR(100) NOT NULL,
    therapeutic_area VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    territory VARCHAR(50) NOT NULL,
    hcp_id VARCHAR(30) NOT NULL,
    hcp_name VARCHAR(100) NOT NULL,
    hcp_specialty VARCHAR(50) NOT NULL,
    sales_rep_id VARCHAR(30) NOT NULL,
    sales_rep_name VARCHAR(100) NOT NULL,
    units_sold INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_sales DECIMAL(14, 2) NOT NULL,
    discount_pct DECIMAL(6, 4) NOT NULL,
    net_sales DECIMAL(14, 2) NOT NULL,
    channel VARCHAR(30) NOT NULL
);

LOAD DATA LOCAL INFILE 'pharma_sales.csv'
INTO TABLE pharma_sales
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
*/


-- ==============================================================================
-- 1. MONTHLY & QUARTERLY SALES AGGREGATION
-- ==============================================================================
-- Description:
-- Aggregates sales performance across time buckets (Monthly and Quarterly).
-- Tracks transaction volume, units sold, gross sales, average discount %,
-- net sales, and average order value (AOV).

-- 1A. Monthly Aggregation
SELECT 
    YEAR(date) AS sales_year,
    MONTH(date) AS sales_month,
    DATE_FORMAT(date, '%Y-%m') AS year_month,
    DATE_FORMAT(date, '%M %Y') AS formatted_month,
    COUNT(transaction_id) AS total_transactions,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(total_sales), 2) AS gross_sales,
    ROUND(AVG(discount_pct) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(net_sales), 2) AS net_sales,
    ROUND(AVG(net_sales), 2) AS avg_net_per_txn
FROM pharma_sales
GROUP BY 
    YEAR(date), 
    MONTH(date), 
    DATE_FORMAT(date, '%Y-%m'), 
    DATE_FORMAT(date, '%M %Y')
ORDER BY sales_year ASC, sales_month ASC;

-- 1B. Quarterly Aggregation
SELECT 
    YEAR(date) AS sales_year,
    QUARTER(date) AS sales_quarter,
    CONCAT(YEAR(date), '-Q', QUARTER(date)) AS year_quarter,
    COUNT(transaction_id) AS total_transactions,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(total_sales), 2) AS gross_sales,
    ROUND(AVG(discount_pct) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(net_sales), 2) AS net_sales,
    ROUND(SUM(net_sales) / SUM(units_sold), 2) AS avg_realized_price_per_unit
FROM pharma_sales
GROUP BY 
    YEAR(date), 
    QUARTER(date), 
    CONCAT(YEAR(date), '-Q', QUARTER(date))
ORDER BY sales_year ASC, sales_quarter ASC;


-- ==============================================================================
-- 2. MoM AND QoQ GROWTH % USING WINDOW FUNCTIONS (LAG)
-- ==============================================================================
-- Description:
-- Utilizes CTEs (Common Table Expressions) and the LAG() window function to 
-- compare current period performance against the previous period (Month-over-Month
-- and Quarter-over-Quarter) and computes percentage growth rates.

-- 2A. Month-over-Month (MoM) Growth Analysis
WITH monthly_metrics AS (
    SELECT 
        YEAR(date) AS sales_year,
        MONTH(date) AS sales_month,
        DATE_FORMAT(date, '%Y-%m') AS period_label,
        COUNT(transaction_id) AS txn_count,
        SUM(units_sold) AS units_sold,
        SUM(net_sales) AS current_net_sales
    FROM pharma_sales
    GROUP BY YEAR(date), MONTH(date), DATE_FORMAT(date, '%Y-%m')
),
mom_lagged AS (
    SELECT 
        sales_year,
        sales_month,
        period_label,
        units_sold,
        current_net_sales,
        LAG(current_net_sales, 1) OVER (
            ORDER BY sales_year ASC, sales_month ASC
        ) AS prev_month_net_sales,
        LAG(units_sold, 1) OVER (
            ORDER BY sales_year ASC, sales_month ASC
        ) AS prev_month_units_sold
    FROM monthly_metrics
)
SELECT 
    period_label,
    ROUND(current_net_sales, 2) AS net_sales,
    ROUND(prev_month_net_sales, 2) AS prev_month_net_sales,
    ROUND(current_net_sales - prev_month_net_sales, 2) AS mom_net_change,
    ROUND(
        CASE 
            WHEN prev_month_net_sales IS NULL THEN NULL
            ELSE ((current_net_sales - prev_month_net_sales) / prev_month_net_sales) * 100 
        END, 
        2
    ) AS mom_sales_growth_pct,
    units_sold,
    prev_month_units_sold,
    ROUND(
        CASE 
            WHEN prev_month_units_sold IS NULL THEN NULL
            ELSE ((units_sold - prev_month_units_sold) / prev_month_units_sold) * 100 
        END, 
        2
    ) AS mom_units_growth_pct
FROM mom_lagged
ORDER BY sales_year ASC, sales_month ASC;

-- 2B. Quarter-over-Quarter (QoQ) Growth Analysis
WITH quarterly_metrics AS (
    SELECT 
        YEAR(date) AS sales_year,
        QUARTER(date) AS sales_quarter,
        CONCAT(YEAR(date), '-Q', QUARTER(date)) AS period_label,
        SUM(units_sold) AS units_sold,
        SUM(net_sales) AS current_net_sales
    FROM pharma_sales
    GROUP BY YEAR(date), QUARTER(date), CONCAT(YEAR(date), '-Q', QUARTER(date))
),
qoq_lagged AS (
    SELECT 
        sales_year,
        sales_quarter,
        period_label,
        units_sold,
        current_net_sales,
        LAG(current_net_sales, 1) OVER (
            ORDER BY sales_year ASC, sales_quarter ASC
        ) AS prev_quarter_net_sales,
        LAG(units_sold, 1) OVER (
            ORDER BY sales_year ASC, sales_quarter ASC
        ) AS prev_quarter_units_sold
    FROM quarterly_metrics
)
SELECT 
    period_label,
    ROUND(current_net_sales, 2) AS net_sales,
    ROUND(prev_quarter_net_sales, 2) AS prev_quarter_net_sales,
    ROUND(current_net_sales - prev_quarter_net_sales, 2) AS qoq_net_change,
    ROUND(
        CASE 
            WHEN prev_quarter_net_sales IS NULL THEN NULL
            ELSE ((current_net_sales - prev_quarter_net_sales) / prev_quarter_net_sales) * 100 
        END, 
        2
    ) AS qoq_sales_growth_pct,
    units_sold,
    ROUND(
        CASE 
            WHEN prev_quarter_units_sold IS NULL THEN NULL
            ELSE ((units_sold - prev_quarter_units_sold) / prev_quarter_units_sold) * 100 
        END, 
        2
    ) AS qoq_units_growth_pct
FROM qoq_lagged
ORDER BY sales_year ASC, sales_quarter ASC;


-- ==============================================================================
-- 3. TOP 10 DRUGS BY REVENUE AND BY UNITS
-- ==============================================================================
-- Description:
-- Ranks pharmaceutical products by Net Revenue and Unit Sales volume.
-- Employs DENSE_RANK() and window sums to compute revenue share & cumulative share.

-- 3A. Top 10 Drugs by Net Revenue (with % Contribution & Cumulative Share)
WITH drug_revenue_summary AS (
    SELECT 
        drug_id,
        drug_name,
        therapeutic_area,
        COUNT(transaction_id) AS total_prescriptions,
        SUM(units_sold) AS total_units_sold,
        ROUND(AVG(unit_price), 2) AS avg_unit_price,
        SUM(net_sales) AS total_net_sales
    FROM pharma_sales
    GROUP BY drug_id, drug_name, therapeutic_area
),
ranked_revenue AS (
    SELECT 
        drug_id,
        drug_name,
        therapeutic_area,
        total_prescriptions,
        total_units_sold,
        avg_unit_price,
        ROUND(total_net_sales, 2) AS net_revenue,
        ROUND(total_net_sales * 100.0 / SUM(total_net_sales) OVER (), 2) AS pct_of_total_revenue,
        ROUND(SUM(total_net_sales) OVER (ORDER BY total_net_sales DESC) * 100.0 / SUM(total_net_sales) OVER (), 2) AS cumulative_revenue_pct,
        DENSE_RANK() OVER (ORDER BY total_net_sales DESC) AS revenue_rank
    FROM drug_revenue_summary
)
SELECT * 
FROM ranked_revenue
WHERE revenue_rank <= 10
ORDER BY revenue_rank ASC;

-- 3B. Top 10 Drugs by Units Sold
WITH drug_units_summary AS (
    SELECT 
        drug_id,
        drug_name,
        therapeutic_area,
        COUNT(transaction_id) AS total_prescriptions,
        SUM(units_sold) AS total_units_sold,
        ROUND(SUM(net_sales), 2) AS total_net_sales,
        DENSE_RANK() OVER (ORDER BY SUM(units_sold) DESC) AS unit_rank,
        ROUND(SUM(units_sold) * 100.0 / SUM(SUM(units_sold)) OVER (), 2) AS pct_of_total_units
    FROM pharma_sales
    GROUP BY drug_id, drug_name, therapeutic_area
)
SELECT * 
FROM drug_units_summary
WHERE unit_rank <= 10
ORDER BY unit_rank ASC;


-- ==============================================================================
-- 4. REGION-WISE AND TERRITORY-WISE PERFORMANCE RANKING
-- ==============================================================================
-- Description:
-- Multi-level geographic ranking displaying:
-- - Overall region rankings by net sales
-- - Territory rankings overall (national rank) and within each respective region (regional rank).

-- 4A. Region-Wise Performance Summary
SELECT 
    region,
    COUNT(DISTINCT territory) AS num_territories,
    COUNT(DISTINCT sales_rep_id) AS num_sales_reps,
    COUNT(transaction_id) AS total_transactions,
    SUM(units_sold) AS total_units,
    ROUND(SUM(net_sales), 2) AS total_net_sales,
    ROUND(SUM(net_sales) * 100.0 / SUM(SUM(net_sales)) OVER (), 2) AS pct_national_sales,
    ROUND(AVG(net_sales), 2) AS avg_txn_value,
    DENSE_RANK() OVER (ORDER BY SUM(net_sales) DESC) AS national_region_rank
FROM pharma_sales
GROUP BY region
ORDER BY national_region_rank ASC;

-- 4B. Territory-Wise Performance & Hierarchical Ranking
WITH territory_performance AS (
    SELECT 
        region,
        territory,
        COUNT(DISTINCT hcp_id) AS active_hcps,
        COUNT(DISTINCT sales_rep_id) AS assigned_reps,
        COUNT(transaction_id) AS total_transactions,
        SUM(units_sold) AS total_units,
        SUM(net_sales) AS total_net_sales
    FROM pharma_sales
    GROUP BY region, territory
)
SELECT 
    region,
    territory,
    active_hcps,
    assigned_reps,
    total_transactions,
    total_units,
    ROUND(total_net_sales, 2) AS territory_net_sales,
    ROUND(total_net_sales * 100.0 / SUM(total_net_sales) OVER (PARTITION BY region), 2) AS pct_of_regional_sales,
    ROUND(total_net_sales * 100.0 / SUM(total_net_sales) OVER (), 2) AS pct_of_national_sales,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY total_net_sales DESC) AS rank_within_region,
    DENSE_RANK() OVER (ORDER BY total_net_sales DESC) AS national_territory_rank
FROM territory_performance
ORDER BY region ASC, rank_within_region ASC;


-- ==============================================================================
-- 5. HCP-LEVEL SEGMENTATION (Platinum/Gold/Silver/Bronze by Sales)
-- ==============================================================================
-- Description:
-- Classifies Healthcare Professionals (Doctors) into tiers (Platinum, Gold, Silver, Bronze)
-- based on their cumulative net prescription sales.
-- Includes summary distribution breakdown across tiers.

-- 5A. Granular HCP Tier Assignment
WITH hcp_sales_summary AS (
    SELECT 
        hcp_id,
        hcp_name,
        hcp_specialty,
        territory,
        region,
        COUNT(transaction_id) AS total_prescriptions,
        SUM(units_sold) AS total_units_prescribed,
        SUM(net_sales) AS total_generated_net_sales,
        PERCENT_RANK() OVER (ORDER BY SUM(net_sales) ASC) AS sales_percentile
    FROM pharma_sales
    GROUP BY hcp_id, hcp_name, hcp_specialty, territory, region
),
hcp_segmented AS (
    SELECT 
        hcp_id,
        hcp_name,
        hcp_specialty,
        region,
        territory,
        total_prescriptions,
        total_units_prescribed,
        ROUND(total_generated_net_sales, 2) AS total_net_sales,
        ROUND(sales_percentile * 100, 2) AS percentile_score,
        CASE 
            WHEN sales_percentile >= 0.85 THEN 'Platinum'   -- Top 15% HCPs
            WHEN sales_percentile >= 0.60 THEN 'Gold'       -- Next 25% (60th - 85th percentile)
            WHEN sales_percentile >= 0.30 THEN 'Silver'     -- Next 30% (30th - 60th percentile)
            ELSE 'Bronze'                                   -- Bottom 30% (0 - 30th percentile)
        END AS hcp_tier
    FROM hcp_sales_summary
)
SELECT 
    hcp_id,
    hcp_name,
    hcp_specialty,
    region,
    territory,
    total_prescriptions,
    total_units_prescribed,
    total_net_sales,
    percentile_score,
    hcp_tier,
    DENSE_RANK() OVER (ORDER BY total_net_sales DESC) AS hcp_national_rank
FROM hcp_segmented
ORDER BY total_net_sales DESC;

-- 5B. Tier Aggregation Summary (Executive Overview of Tiers)
WITH hcp_metrics AS (
    SELECT 
        hcp_id,
        SUM(net_sales) AS total_net_sales,
        PERCENT_RANK() OVER (ORDER BY SUM(net_sales) ASC) AS sales_percentile
    FROM pharma_sales
    GROUP BY hcp_id
),
tiered_hcps AS (
    SELECT 
        hcp_id,
        total_net_sales,
        CASE 
            WHEN sales_percentile >= 0.85 THEN 'Platinum'
            WHEN sales_percentile >= 0.60 THEN 'Gold'
            WHEN sales_percentile >= 0.30 THEN 'Silver'
            ELSE 'Bronze'
        END AS hcp_tier
    FROM hcp_metrics
)
SELECT 
    hcp_tier,
    COUNT(hcp_id) AS total_hcps,
    ROUND(COUNT(hcp_id) * 100.0 / SUM(COUNT(hcp_id)) OVER (), 2) AS pct_of_doctors,
    ROUND(SUM(total_net_sales), 2) AS tier_total_net_sales,
    ROUND(SUM(total_net_sales) * 100.0 / SUM(SUM(total_net_sales)) OVER (), 2) AS pct_of_total_revenue,
    ROUND(AVG(total_net_sales), 2) AS avg_sales_per_hcp,
    ROUND(MIN(total_net_sales), 2) AS min_sales_threshold,
    ROUND(MAX(total_net_sales), 2) AS max_sales_in_tier
FROM tiered_hcps
GROUP BY hcp_tier
ORDER BY 
    CASE hcp_tier 
        WHEN 'Platinum' THEN 1 
        WHEN 'Gold' THEN 2 
        WHEN 'Silver' THEN 3 
        WHEN 'Bronze' THEN 4 
    END ASC;


-- ==============================================================================
-- 6. THERAPEUTIC AREA CONTRIBUTION BREAKDOWN
-- ==============================================================================
-- Description:
-- Evaluates portfolio distribution across the 4 primary therapeutic categories:
-- Cardiology, Oncology, Neurology, and Diabetes.
-- Analyzes unit volume, product breadth, discount depth, and revenue share.

SELECT 
    therapeutic_area,
    COUNT(DISTINCT drug_id) AS portfolio_drug_count,
    COUNT(DISTINCT hcp_id) AS unique_prescribing_hcps,
    COUNT(transaction_id) AS total_transactions,
    SUM(units_sold) AS total_units_sold,
    ROUND(SUM(total_sales), 2) AS gross_sales,
    ROUND(AVG(discount_pct) * 100, 2) AS avg_discount_rate_pct,
    ROUND(SUM(net_sales), 2) AS total_net_sales,
    ROUND(SUM(net_sales) * 100.0 / SUM(SUM(net_sales)) OVER (), 2) AS revenue_contribution_pct,
    ROUND(SUM(units_sold) * 100.0 / SUM(SUM(units_sold)) OVER (), 2) AS unit_volume_contribution_pct,
    ROUND(SUM(net_sales) / SUM(units_sold), 2) AS effective_price_per_unit
FROM pharma_sales
GROUP BY therapeutic_area
ORDER BY total_net_sales DESC;


-- ==============================================================================
-- 7. IDENTIFY UNDERPERFORMING TERRITORIES (<70% OF TARGET / MEAN)
-- ==============================================================================
-- Description:
-- Identifies territories lagging behind expectations (<70% of target/benchmark mean).
-- Dynamically calculates territory target based on the benchmark average territory revenue,
-- flags the performance index %, revenue shortfall deficit, and displays the assigned sales team.

WITH territory_revenue_stats AS (
    SELECT 
        region,
        territory,
        COUNT(DISTINCT sales_rep_id) AS rep_count,
        GROUP_CONCAT(DISTINCT sales_rep_name ORDER BY sales_rep_name SEPARATOR ', ') AS assigned_sales_reps,
        COUNT(transaction_id) AS transaction_count,
        SUM(units_sold) AS total_units_sold,
        SUM(net_sales) AS territory_net_sales
    FROM pharma_sales
    GROUP BY region, territory
),
benchmark_calc AS (
    SELECT 
        region,
        territory,
        rep_count,
        assigned_sales_reps,
        transaction_count,
        total_units_sold,
        territory_net_sales,
        -- Benchmark target set to national average territory revenue across all 20 territories
        AVG(territory_net_sales) OVER () AS target_revenue_benchmark,
        -- 70% threshold definition
        AVG(territory_net_sales) OVER () * 0.70 AS threshold_70_pct
    FROM territory_revenue_stats
)
SELECT 
    region,
    territory,
    rep_count,
    assigned_sales_reps,
    transaction_count,
    total_units_sold,
    ROUND(territory_net_sales, 2) AS territory_net_sales,
    ROUND(target_revenue_benchmark, 2) AS target_revenue_benchmark,
    ROUND(territory_net_sales - target_revenue_benchmark, 2) AS deficit_to_target,
    ROUND((territory_net_sales / target_revenue_benchmark) * 100, 2) AS pct_of_target_achieved,
    CASE 
        WHEN territory_net_sales < (target_revenue_benchmark * 0.70) 
        THEN 'CRITICAL: Underperforming (<70% of Target)'
        WHEN territory_net_sales < target_revenue_benchmark 
        THEN 'WATCHLIST: Below Target (70-100%)'
        ELSE 'ON TARGET: >= 100%'
    END AS performance_status
FROM benchmark_calc
WHERE territory_net_sales < threshold_70_pct
ORDER BY pct_of_target_achieved ASC;
