-- This file contains tests for the DBT models. It verifies that the data transformations produce the expected results.

-- Example test to check if the model produces non-null values
SELECT *
FROM {{ ref('example_model') }}
WHERE column_name IS NULL

-- Add more tests as needed to validate the model's output