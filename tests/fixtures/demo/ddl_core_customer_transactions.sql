-- Create the core_customer_transactions table.
-- Denormalized table joining customers and transactions from staging layer.
-- Only populated for instances that have both stage_customers and stage_transactions.
--
-- Used in:
--   sales_test.main — loaded with africa filter (deliberate error)
--
-- NOT used in:
--   payments domain — has no customers in staging, uses core_account_payments instead
--
-- Placeholders:
--   {database}  — e.g. sales_test
--   {schema}    — instance name, e.g. main

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.core_customer_transactions (
    id              INTEGER,
    transaction_date DATE,
    amount          FLOAT,
    customer_id     INTEGER,
    customer_name   STRING,
    customer_type   STRING,
    customer_region STRING
);
