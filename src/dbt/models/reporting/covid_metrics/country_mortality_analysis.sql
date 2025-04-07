{{
    config(
        materialized='view',
        schema='reporting',
        tags=['covid', 'reporting', 'analysis']
    )
}}

/*
    Country-Level Mortality Analysis
    
    Analyzes COVID-19 mortality rates by country:
    - Mortality rate calculation
    - Country rankings
    - Case thresholds for significance
    - Latest available data
    
    Note: Only includes countries with >1000 total cases for statistical relevance
*/

WITH 
-- Step 1: Calculate key metrics per country
country_stats AS (
    SELECT 
        country_region,
        MAX(total_confirmed) as total_cases,    -- Latest total cases
        MAX(total_deaths) as total_deaths,      -- Latest total deaths
        -- Calculate mortality rate as percentage
        ROUND(100.0 * MAX(total_deaths) / NULLIF(MAX(total_confirmed), 0), 2) as mortality_rate
    FROM {{ ref('daily_metrics') }}
    GROUP BY country_region
    HAVING MAX(total_confirmed) > 1000  -- Filter out countries with too few cases
),

-- Step 2: Add rankings for both total cases and mortality
ranked_stats AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (ORDER BY total_cases DESC) as cases_rank,      -- Rank by size
        ROW_NUMBER() OVER (ORDER BY mortality_rate DESC) as mortality_rank -- Rank by mortality
    FROM country_stats
),

-- Step 3: Final output with global average comparison
final AS (
    SELECT 
        country_region,
        total_cases,
        total_deaths,
        mortality_rate,
        cases_rank,
        mortality_rank,
        -- Flag countries with above-average mortality
        CASE 
            WHEN mortality_rate > (SELECT AVG(mortality_rate) FROM country_stats)
            THEN true 
            ELSE false 
        END as above_avg_mortality
    FROM ranked_stats
    ORDER BY total_cases DESC  -- Order by country size
)

SELECT * FROM final