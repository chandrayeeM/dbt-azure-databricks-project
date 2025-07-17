-- This is an example DBT model that transforms raw data into a structured format for analysis.

with raw_data_runways as (
    select *
    from {{ ref('runways') }}
)

SELECT
  id,
  airport_ref,
  airport_ident,
  length_ft,
  width_ft,
  surface,
  lighted,
  closed,
  le_ident,
  le_latitude_deg,
  le_longitude_deg,
  le_elevation_ft,
  le_heading_degT,
  le_displaced_threshold_ft,
  he_ident,
  he_latitude_deg,
  he_longitude_deg,
  he_elevation_ft,
  he_heading_degT,
  he_displaced_threshold_ft
from raw_data_runways
-- where active = true