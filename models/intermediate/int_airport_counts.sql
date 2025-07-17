{{ config(materialized = 'view') }}

SELECT
  c.code AS country_code,
  c.name AS country_name,
  COUNT(a.ident) AS airport_count
FROM {{ ref('stg_airports') }} a
JOIN {{ ref('stg_countries') }} c
  ON a.iso_country = c.code
GROUP BY c.code, c.name