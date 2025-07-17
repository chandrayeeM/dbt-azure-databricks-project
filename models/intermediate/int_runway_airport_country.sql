{{ config(materialized = 'view') }}

WITH base AS (
    SELECT
        r.id AS runway_id,
        r.airport_ident,
        r.length_ft,
        r.width_ft,
        a.ident AS airport_code,
        a.name AS airport_name,
        a.iso_country,
        c.code AS country_code,
        c.name AS country_name
    FROM {{ ref('stg_runways') }} r
    JOIN {{ ref('stg_airports') }} a
        ON r.airport_ident = a.ident
    JOIN {{ ref('stg_countries') }} c
        ON a.iso_country = c.code
    WHERE r.length_ft IS NOT NULL --AND r.width_ft IS NOT NULL
),

with_ranks AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY iso_country ORDER BY length_ft DESC) AS longest_rank,
        ROW_NUMBER() OVER (PARTITION BY iso_country ORDER BY length_ft ASC) AS shortest_rank
    FROM base
)

SELECT
    runway_id,
    airport_ident,
    airport_code,
    airport_name,
    length_ft,
    width_ft,
    iso_country,
    country_code,
    country_name,
    longest_rank,
    shortest_rank
FROM with_ranks
