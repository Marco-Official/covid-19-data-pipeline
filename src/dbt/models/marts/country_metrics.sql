{{
    config(
        materialized='table',
        schema='analytics',
        tags=['covid', 'marts']
    )
}}

-- Step 1: Calculate latest metrics per country
WITH latest_metrics AS (
    SELECT 
        country_region,
        MAX(date) as latest_date,
        MAX(confirmed_cases) as total_confirmed,
        MAX(death_count) as total_deaths,
        MAX(recovered_count) as total_recovered,
        AVG(mortality_rate) as avg_mortality_rate,
        AVG(recovery_rate) as avg_recovery_rate
    FROM {{ ref('stg_covid_metrics') }}
    GROUP BY country_region
),

-- Step 2: Add rankings for different metrics
country_rankings AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (ORDER BY total_confirmed DESC) as confirmed_rank,
        ROW_NUMBER() OVER (ORDER BY total_deaths DESC) as death_rank,
        ROW_NUMBER() OVER (ORDER BY avg_mortality_rate DESC) as mortality_rate_rank
    FROM latest_metrics
),

-- Step 3: Calculate global percentages and prepare final output
final AS (
    SELECT 
        cr.*,
        -- Calculate percentages of global totals
        ROUND(100.0 * cr.total_confirmed / SUM(cr.total_confirmed) OVER (), 2) as pct_of_global_confirmed,
        ROUND(100.0 * cr.total_deaths / SUM(cr.total_deaths) OVER (), 2) as pct_of_global_deaths,
        -- Add metadata
        CURRENT_TIMESTAMP as generated_at
    FROM country_rankings cr
    ORDER BY total_confirmed DESC
)

-- Step 4: Return final results
SELECT * FROM final
