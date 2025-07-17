-- This is an example DBT model that transforms raw data into a structured format for analysis.

with raw_data_countries as (
    select *
    from {{ ref('countries') }}
)

select
  id,
  code,
  name,
  continent,
  wikipedia_link,
  keywords
from raw_data_countries
-- where active = true