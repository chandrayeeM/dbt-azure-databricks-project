-- This macro takes a table name as input and returns the count of rows in that table
{% macro count_rows(table_name) %}
    select count(*) from {{ table_name }}
{% endmacro %}