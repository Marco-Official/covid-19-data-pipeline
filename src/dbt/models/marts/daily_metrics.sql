{{
    config(
        materialized='table',
        schema='analytics',
        tags=['covid', 'marts']
    )
}}

-- Step 1: Calculate daily stats per country
WITH daily_stats AS (
    SELECT
        date,
        country_region,
        SUM(confirmed_cases) as total_confirmed,
        SUM(death_count) as total_deaths,
        SUM(recovered_count) as total_recovered,
        SUM(active_cases) as total_active
    FROM {{ ref('stg_covid_metrics') }}
    GROUP BY date, country_region
),

-- Step 2: Add previous day metrics for calculations
previous_day AS (
    SELECT
        date,
        country_region,
        total_confirmed,
        total_deaths,
        total_recovered,
        total_active,
        LAG(total_confirmed) OVER (PARTITION BY country_region ORDER BY date) as prev_confirmed,
        LAG(total_deaths) OVER (PARTITION BY country_region ORDER BY date) as prev_deaths,
        LAG(total_recovered) OVER (PARTITION BY country_region ORDER BY date) as prev_recovered
    FROM daily_stats
),

-- Step 3: Calculate final metrics with daily changes
final AS (
    SELECT
        date,
        country_region,
        -- Daily totals
        total_confirmed,
        total_deaths,
        total_recovered,
        total_active,
        -- Daily changes
        total_confirmed - COALESCE(prev_confirmed, 0) as new_cases,
        total_deaths - COALESCE(prev_deaths, 0) as new_deaths,
        total_recovered - COALESCE(prev_recovered, 0) as new_recovered,
        -- Growth rate
        CASE 
            WHEN prev_confirmed > 0 THEN 
                ROUND(((total_confirmed - prev_confirmed)::FLOAT / prev_confirmed) * 100, 2)
            ELSE NULL 
        END as growth_rate_percentage,
        -- Add metadata
        CURRENT_TIMESTAMP as generated_at
    FROM previous_day
    ORDER BY country_region, date
)

-- Step 4: Return final results
SELECT * FROM final 