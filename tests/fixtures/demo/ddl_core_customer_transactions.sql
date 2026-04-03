-- Create the core_customer_transactions table.
-- Denormalized table joining customers and transactions from staging layer.
-- Only populated for instances that have both stage_customers and stage_transactions.
--
-- Used in:
--   payments_test.alpha  — fully loaded (12 rows after africa filter)
--   payments_test.beta   — loaded from one business date
--
-- NOT used in:
--   sales domain         — has no transactions, so core layer is skipped
--   payments_uat         — has no transactions, so core layer is skipped
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.core_customer_transactions (
    id              INTEGER,
    transaction_date DATE,
    amount          INTEGER,
    customer_id     INTEGER,
    customer_name   STRING,
    customer_type   STRING,
    customer_region STRING
);
