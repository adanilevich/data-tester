-- Load a CSV file from the raw layer into a staging table.
-- Appends the source filename as an extra column for traceability.
--
-- An optional {limit_clause} (e.g. "LIMIT 4") can truncate the load to
-- simulate incomplete data ingestion — used for customers_2024-01-02.xlsx
-- to create a deliberate rowcount mismatch for testing.
--
-- Placeholders:
--   {database}      — e.g. payments_test
--   {schema}        — instance name, e.g. alpha
--   {table}         — full table name, e.g. stage_customers
--   {csv_filepath}  — absolute path to the CSV source file
--   {filename}      — just the filename, e.g. customers_2024-01-01.csv
--   {limit_clause}  — "" for full load, or "LIMIT 4" for truncated load

INSERT INTO {database}.{schema}.{table}
SELECT *, '{filename}' AS source_file
FROM '{csv_filepath}'
{limit_clause};
