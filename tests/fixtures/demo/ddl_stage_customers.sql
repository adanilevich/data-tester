-- Create the stage_customers table.
-- Holds customer master data loaded from CSV files in the raw layer.
-- Each row represents one customer record from one source file.
--
-- Used in:
--   sales_test.main — customers_2024-01-01 + customers_2024-01-02
--
-- Placeholders:
--   {database}  — e.g. sales_test
--   {schema}    — instance name, e.g. main

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.stage_customers (
    date                 STRING,
    id                   INTEGER,
    region               STRING,
    type                 STRING,
    name                 STRING,
    m__ts                TIMESTAMP,
    m__source_file       STRING,
    m__source_file_path  STRING
);
