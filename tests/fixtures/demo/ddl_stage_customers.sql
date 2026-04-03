-- Create the stage_customers table.
-- Holds customer master data loaded from CSV files in the raw layer.
-- Each row represents one customer record from one source file.
--
-- Used in:
--   payments_uat.main          — customers_2024-01-01 only
--   payments_test.alpha        — customers_2024-01-01 + customers_2024-01-02 (truncated to 4 rows)
--   payments_test.beta         — customers_2024-01-01 only
--   sales_test.main            — customers_2024-01-02 (truncated to 4 rows)
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.stage_customers (
    date        STRING,
    id          INTEGER,
    region      STRING,
    type        STRING,
    name        STRING,
    source_file STRING
);
