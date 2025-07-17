{{ config(materialized = 'table') }}

WITH airport_counts AS (
  SELECT * FROM {{ ref('int_airport_counts') }}
),

ranked AS (
  SELECT
    *,
    RANK() OVER (ORDER BY airport_count DESC) AS rank_desc,
    RANK() OVER (ORDER BY airport_count ASC) AS rank_asc
  FROM airport_counts
)

SELECT
  country_code,
  country_name,
  airport_count,
  CASE
    WHEN rank_desc <= 3 THEN 'top_3'
    WHEN rank_asc <= 10 THEN 'bottom_10'
    ELSE NULL
  END AS rank_category
FROM ranked
WHERE rank_desc <= 3 OR rank_asc <= 10
ORDER BY rank_category, airport_count DESC
