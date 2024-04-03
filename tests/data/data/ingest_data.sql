DROP TABLE IF EXISTS my_domain.alpha.stage_customers;
DROP TABLE IF EXISTS my_domain.beta.stage_customers;
DROP TABLE IF EXISTS my_domain.alpha.stage_transactions;
DROP TABLE IF EXISTS my_domain.beta.stage_transactions;
DROP TABLE IF EXISTS my_domain.alpha.core_revenues;

CREATE TABLE my_domain.alpha.stage_customers AS (
    SELECT * FROM read_csv('$customers_file_1')
    UNION ALL
    (SELECT * FROM read_csv('$customers_file_2') LIMIT 4)-- we trucate 2 customers
);

CREATE TABLE my_domain.alpha.stage_transactions AS (
    SELECT * FROM read_csv('$transactions_file_1')
    UNION ALL
    SELECT * FROM read_csv('$transactions_file_2')
);

CREATE TABLE my_domain.alpha.core_revenues AS (
    SELECT
        transactions.id,
        transactions.date AS transaction_date,
        transactions.amount,
        transactions.customer_id,
        customers.name AS customer_name,
        customers.type AS customer_type,
        customers.region AS customer_region,
        customers.date AS customer_date

    FROM my_domain.alpha.stage_transactions AS transactions
    LEFT JOIN my_domain.alpha.stage_customers AS customers
        ON transactions.customer_id = customers.id
        AND transactions.date = customers.date

    WHERE customer_region != 'africa'
);