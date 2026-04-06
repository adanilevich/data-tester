-- Create the core_account_payments table.
-- Denormalized table joining accounts and transactions from staging layer.
-- Populated for instances that have both stage_accounts and stage_transactions.
--
-- Used in:
--   payments_test.alpha  — fully loaded
--   payments_test.beta   — loaded from one business date
--   payments_uat.main    — loaded from one business date
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

CREATE SCHEMA IF NOT EXISTS {database}.{schema};
CREATE TABLE IF NOT EXISTS {database}.{schema}.core_account_payments (
    id               INTEGER,
    transaction_date DATE,
    amount           FLOAT,
    account_id       INTEGER,
    account_type     STRING,
    account_name     STRING,
    customer_id      INTEGER
);
