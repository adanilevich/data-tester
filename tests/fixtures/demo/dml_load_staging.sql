-- Load a CSV file from the raw layer into a staging table.
-- Appends metadata columns for traceability:
--   m__ts              — load timestamp
--   m__source_file     — just the filename
--   m__source_file_path — full path with local:// prefix
--
-- An optional {limit_clause} (e.g. "LIMIT 500") can truncate the load to
-- simulate incomplete data ingestion — used for transactions_2024-01-02
-- in payments domain to create a deliberate stagecount mismatch for testing.
--
-- Placeholders:
--   {database}           — e.g. payments_test
--   {schema}             — instance name, e.g. alpha
--   {table}              — full table name, e.g. stage_customers
--   {csv_filepath}       — absolute path to the CSV source file
--   {filename}           — just the filename, e.g. customers_2024-01-01.csv
--   {source_file_path}   — full path with local:// prefix
--   {load_ts}            — load timestamp string
--   {limit_clause}       — "" for full load, or "LIMIT n" for truncated load

INSERT INTO {database}.{schema}.{table}
SELECT *,
    '{load_ts}'::TIMESTAMP AS m__ts,
    '{filename}' AS m__source_file,
    '{source_file_path}' AS m__source_file_path
FROM '{csv_filepath}'
{limit_clause};
