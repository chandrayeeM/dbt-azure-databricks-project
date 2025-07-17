{{ config(materialized = 'table') }}

WITH source AS (
    SELECT * FROM {{ ref('int_runway_airport_country') }}
),
valid_country_counts AS (
    SELECT
        iso_country,
        COUNT(*) AS valid_runway_count
    FROM source
    GROUP BY iso_country
    HAVING COUNT(*) >= 2
),
filtered_source AS (
    SELECT s.*
    FROM source s
    JOIN valid_country_counts c ON s.iso_country = c.iso_country
),
longest AS (
    SELECT
        country_name,
        airport_name,
        length_ft,
        width_ft,
        'longest' AS runway_type
    FROM filtered_source
    WHERE longest_rank = 1
),

shortest AS (
    SELECT
        country_name,
        airport_name,
        length_ft,
        width_ft,
        'shortest' AS runway_type
    FROM filtered_source
    WHERE shortest_rank = 1
)

SELECT 
    country_name,
    airport_name,
    length_ft,
    width_ft,
    runway_type
FROM longest
UNION ALL
SELECT 
    country_name,
    airport_name,
    length_ft,
    width_ft,
    runway_type 
FROM shortest
ORDER BY country_name, runway_type