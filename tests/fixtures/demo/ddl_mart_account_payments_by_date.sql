-- Create the mart_account_payments_by_date table.
-- Aggregation of amounts from core_account_payments per date and account.
--
-- Used in:
--   payments_test.alpha
--   payments_test.beta
--
-- NOT used in:
--   payments_uat — mart layer only in TEST stage
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.mart_account_payments_by_date (
    account_id        INTEGER,
    transaction_date  DATE,
    total_amount      FLOAT,
    transaction_count INTEGER
);
