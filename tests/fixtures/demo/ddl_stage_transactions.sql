-- Create the stage_transactions table.
-- Holds transaction data loaded from CSV files in the raw layer.
-- Each row represents one transaction from one source file.
--
-- Used in:
--   payments_test.alpha  — transactions_2024-01-01 + transactions_2024-01-02
--   payments_test.beta   — transactions_2024-01-01 only
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.stage_transactions (
    date        STRING,
    id          INTEGER,
    customer_id INTEGER,
    amount      FLOAT,
    source_file STRING
);
