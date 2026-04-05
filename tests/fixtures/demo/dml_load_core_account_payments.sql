-- Populate core_account_payments by joining staging tables.
-- Joins stage_transactions with stage_accounts on account_id and date.
--
-- Placeholders:
--   {database}  — e.g. payments_test
--   {schema}    — instance name, e.g. alpha

INSERT INTO {database}.{schema}.core_account_payments
    SELECT
        transactions.id,
        transactions.date AS transaction_date,
        transactions.amount,
        transactions.account_id,
        accounts.type AS account_type,
        accounts.name AS account_name,
        accounts.customer_id

    FROM {database}.{schema}.stage_transactions AS transactions
    LEFT JOIN {database}.{schema}.stage_accounts AS accounts
        ON transactions.account_id = accounts.id
        AND transactions.date = accounts.date;
