-- This test will fail if there are any negative case counts
SELECT *
FROM {{ ref('daily_metrics') }}
WHERE total_confirmed < 0
   OR total_deaths < 0 