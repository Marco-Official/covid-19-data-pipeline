{{
    config(
        materialized='view',
        schema='reporting',
        tags=['covid', 'reporting', 'trends']
    )
}}

/*
    Global Daily COVID-19 Trends
    
    Aggregates daily COVID-19 metrics globally to track:
    - Total and new cases
    - Total deaths
    - Growth rates
    - 7-day moving averages
    
    Note: Uses 7-day averages to smooth out weekend reporting dips
*/

WITH 
-- Step 1: Aggregate metrics globally for each day
global_daily_cases AS (
    SELECT 
        date,
        SUM(total_confirmed) as total_cases,     -- Global cumulative cases
        SUM(new_cases) as new_cases,             -- New cases reported that day
        SUM(total_deaths) as total_deaths,       -- Global cumulative deaths
        ROUND(AVG(growth_rate_percentage), 2) as avg_growth_rate  -- Average daily growth rate
    FROM {{ ref('daily_metrics') }}
    GROUP BY date
),

-- Step 2: Add moving averages and format final output
final AS (
    SELECT 
        date,
        total_cases,
        new_cases,
        total_deaths,
        avg_growth_rate,
        -- Calculate 7-day moving average to smooth out weekly reporting patterns
        ROUND(AVG(new_cases) OVER (
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 0) as cases_7day_avg
    FROM global_daily_cases
    ORDER BY date  -- Ensure chronological order
)

SELECT * FROM final 