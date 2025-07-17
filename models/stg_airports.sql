-- This is an example DBT model that transforms raw data into a structured format for analysis.

with raw_data_airport as (
    select *
    from {{ ref('airports') }}
)

select
    id,
    ident,
    type,
    name,
    latitude_deg,
    longitude_deg,
    elevation_ft,
    continent,
    iso_country,
    iso_region,
    municipality,
    scheduled_service,
    gps_code,
    iata_code,
    local_code,
    home_link,
    wikipedia_link,
    keywords
from raw_data_airport
-- where active = true