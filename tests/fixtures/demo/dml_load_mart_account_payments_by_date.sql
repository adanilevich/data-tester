-- Populate mart_account_payments_by_date by aggregating core_account_payments.
-- Groups by account_id and transaction_date, sums amounts and counts transactions.
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

INSERT INTO {database}.{schema}.mart_account_payments_by_date
    SELECT
        account_id,
        transaction_date,
        SUM(amount) AS total_amount,
        COUNT(*) AS transaction_count

    FROM {database}.{schema}.core_account_payments
    GROUP BY account_id, transaction_date;
