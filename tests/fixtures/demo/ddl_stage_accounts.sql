-- Create the stage_accounts table.
-- Holds account master data loaded from CSV files in the raw layer.
-- Each row represents one account record from one source file.
--
-- Used in:
--   payments_test.alpha  — accounts_2024-01-01 + accounts_2024-01-02
--   payments_test.beta   — accounts_2024-01-01 only
--   payments_uat.main    — accounts_2024-01-01 only
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.stage_accounts (
    date                 STRING,
    id                   INTEGER,
    customer_id          INTEGER,
    type                 STRING,
    name                 STRING,
    m__ts                TIMESTAMP,
    m__source_file       STRING,
    m__source_file_path  STRING
);
