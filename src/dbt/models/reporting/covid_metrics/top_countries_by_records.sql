{{
    config(
        materialized='view',
        schema='reporting',
        tags=['covid', 'reporting', 'countries']
    )
}}

/*
    Top Countries by COVID-19 Metrics
    
    Ranks countries based on key COVID-19 indicators:
    - Total confirmed cases
    - Total deaths
    - Active cases
    - Recovery rates
    
    Note: Updates daily with latest available data
*/

WITH 
-- Step 1: Calculate metrics per country
country_metrics AS (
    SELECT 
        country_region,
        COUNT(*) as record_count,          -- Number of daily reports (1 per geographic unit)
        SUM(confirmed_cases) as total_cases,  -- Total cases across all regions
        SUM(death_count) as total_deaths      -- Total deaths across all regions
    FROM {{ ref('stg_covid_metrics') }}
    GROUP BY country_region
),

-- Step 2: Get total record count for percentage calculation
total_records AS (
    SELECT COUNT(*) as total_count
    FROM {{ ref('stg_covid_metrics') }}
),

-- Step 3: Final output with percentages and mortality rate
final AS (
    SELECT 
        country_region,
        record_count,
        total_cases,
        total_deaths,
        -- Calculate what percentage of all records belong to this country
        ROUND(100.0 * record_count / total_count, 2) as percentage_of_records,
        -- Calculate mortality rate (deaths/cases)
        ROUND(100.0 * total_deaths / NULLIF(total_cases, 0), 2) as mortality_rate
    FROM country_metrics
    CROSS JOIN total_records
    ORDER BY record_count DESC  -- Rank by number of records
    LIMIT 5                     -- Show only top 5 countries
)

SELECT * FROM final 