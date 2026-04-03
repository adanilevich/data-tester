-- Attach a DuckDB database file.
-- Database files follow the naming convention: <domain>_<stage>.db
-- e.g. payments_test.db, payments_uat.db, sales_test.db
--
-- Databases used in this fixture:
--   payments_test.db  — payments domain, test stage (instances: alpha, beta)
--   payments_uat.db   — payments domain, uat stage  (instance: main)
--   sales_test.db     — sales domain, test stage    (instance: main)
--
-- Placeholders:
--   {db_filepath}  — full path to the .db file on disk
--   {database}     — logical database name, e.g. payments_test

ATTACH IF NOT EXISTS '{db_filepath}' AS {database};
