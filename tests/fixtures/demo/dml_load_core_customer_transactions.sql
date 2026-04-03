-- Populate core_customer_transactions by joining staging tables.
-- Joins stage_transactions with stage_customers on customer_id and date,
-- then filters out rows where customer_region = 'africa'.
--
-- The africa filter is a deliberate business rule that reduces the result
-- set (e.g. payments_test.alpha goes from 18 transactions to 12 core rows).
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

INSERT INTO {database}.{schema}.core_customer_transactions
    SELECT
        transactions.id,
        transactions.date AS transaction_date,
        transactions.amount,
        transactions.customer_id,
        customers.name AS customer_name,
        customers.type AS customer_type,
        customers.region AS customer_region

    FROM {database}.{schema}.stage_transactions AS transactions
    LEFT JOIN {database}.{schema}.stage_customers AS customers
        ON transactions.customer_id = customers.id
        AND transactions.date = customers.date

    -- Business rule: exclude african region from core layer
    WHERE customer_region != 'africa';
