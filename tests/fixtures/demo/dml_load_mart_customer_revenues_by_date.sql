-- Populate mart_customer_revenues_by_date by aggregating core_customer_transactions.
-- Groups by customer_id and transaction_date, sums amounts and counts transactions.
--
-- Placeholders:
--   {database}  — e.g. sales_test
--   {schema}    — instance name, e.g. main

INSERT INTO {database}.{schema}.mart_customer_revenues_by_date
    SELECT
        customer_id,
        transaction_date,
        SUM(amount) AS total_amount,
        COUNT(*) AS transaction_count

    FROM {database}.{schema}.core_customer_transactions
    GROUP BY customer_id, transaction_date;
