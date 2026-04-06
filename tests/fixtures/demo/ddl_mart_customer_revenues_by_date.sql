-- Create the mart_customer_revenues_by_date table.
-- Aggregation of amounts from core_customer_transactions per customer and date.
--
-- Used in:
--   sales_test.main
--
-- Placeholders:
--   {database}  — e.g. sales_test
--   {schema}    — instance name, e.g. main

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.mart_customer_revenues_by_date (
    customer_id       INTEGER,
    transaction_date  DATE,
    total_amount      FLOAT,
    transaction_count INTEGER
);
