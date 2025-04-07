{{
    config(
        materialized='table',
        schema='staging',
        tags=['covid', 'staging']
    )
}}

-- Step 1: Import source data and clean column names
WITH source_confirmed AS (
    SELECT 
        date,
        "Province/State" as province_state,
        "Country/Region" as country_region,
        Lat as latitude,
        Long as longitude,
        confirmed as confirmed_cases
    FROM {{ source('covid', 'raw_confirmed') }}
),

source_deaths AS (
    SELECT 
        date,
        "Province/State" as province_state,
        "Country/Region" as country_region,
        deaths as death_count
    FROM {{ source('covid', 'raw_deaths') }}
),

source_recovered AS (
    SELECT 
        date,
        "Province/State" as province_state,
        "Country/Region" as country_region,
        recovered as recovered_count
    FROM {{ source('covid', 'raw_recovered') }}
),

-- Step 2: Join all metrics together
joined_metrics AS (
    SELECT 
        c.date,
        c.province_state,
        c.country_region,
        c.latitude,
        c.longitude,
        c.confirmed_cases,
        d.death_count,
        r.recovered_count
    FROM source_confirmed c
    LEFT JOIN source_deaths d 
        ON c.date = d.date 
        AND COALESCE(c.province_state, '') = COALESCE(d.province_state, '')
        AND c.country_region = d.country_region
    LEFT JOIN source_recovered r
        ON c.date = r.date 
        AND COALESCE(c.province_state, '') = COALESCE(r.province_state, '')
        AND c.country_region = r.country_region 
),

-- Step 3: Final output with calculated 
final AS (
    SELECT 
        date,
        province_state,
        country_region,
        latitude,
        longitude,
        confirmed_cases,
        death_count,
        recovered_count,
        confirmed_cases - COALESCE(recovered_count, 0) - COALESCE(death_count, 0) as active_cases,
        -- Add mortality and recovery rates
        CASE 
            WHEN confirmed_cases > 0 THEN 
                ROUND((death_count::FLOAT / confirmed_cases) * 100, 2)
            ELSE NULL 
        END as mortality_rate,
        CASE 
            WHEN confirmed_cases > 0 THEN 
                ROUND((recovered_count::FLOAT / confirmed_cases) * 100, 2)
            ELSE NULL 
        END as recovery_rate
    FROM joined_metrics
)

-- Step 4: Add final output to the model
SELECT * FROM final