{{
    config(
        materialized='table',
        tags=['covid', 'marts']
    )
}}

-- Step 1: Calculate daily global totals
WITH daily_totals AS (
    SELECT 
        date,
        SUM(confirmed_cases) as global_confirmed,
        SUM(death_count) as global_deaths,
        SUM(recovered_count) as global_recovered,
        SUM(active_cases) as global_active,
        AVG(mortality_rate) as avg_mortality_rate,
        AVG(recovery_rate) as avg_recovery_rate
    FROM {{ ref('stg_covid_metrics') }}
    GROUP BY date
),

-- Step 2: Calculate daily changes and moving averages
daily_changes AS (
    SELECT 
        *,
        -- Daily changes
        global_confirmed - LAG(global_confirmed, 1) OVER (ORDER BY date) as new_confirmed,
        global_deaths - LAG(global_deaths, 1) OVER (ORDER BY date) as new_deaths,
        global_recovered - LAG(global_recovered, 1) OVER (ORDER BY date) as new_recovered,
        -- 7-day moving averages
        AVG(global_confirmed) OVER (
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as confirmed_7day_avg,
        AVG(global_deaths) OVER (
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as deaths_7day_avg
    FROM daily_totals
),

-- Step 3: Prepare final output with all metrics
final AS (
    SELECT 
        date,
        -- Daily totals
        global_confirmed,
        global_deaths,
        global_recovered,
        global_active,
        -- New cases
        new_confirmed,
        new_deaths,
        new_recovered,
        -- Moving averages
        ROUND(confirmed_7day_avg) as confirmed_7day_avg,
        ROUND(deaths_7day_avg) as deaths_7day_avg,
        -- Rates
        avg_mortality_rate,
        avg_recovery_rate,
        -- Growth rates
        CASE 
            WHEN LAG(global_confirmed, 1) OVER (ORDER BY date) > 0 
            THEN ROUND(100.0 * (global_confirmed - LAG(global_confirmed, 1) OVER (ORDER BY date)) / 
                      LAG(global_confirmed, 1) OVER (ORDER BY date), 2)
            ELSE NULL 
        END as confirmed_growth_rate,
        -- Add metadata
        CURRENT_TIMESTAMP as generated_at
    FROM daily_changes
    ORDER BY date
)

-- Step 4: Return final results
SELECT * FROM final 