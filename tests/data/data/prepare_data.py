from typing import List, Tuple
from pathlib import Path

import polars as pl
import duckdb

PATH = Path(__file__).parent

filenames = (
    PATH / "customers_2024-01-01.xlsx",
    PATH / "customers_2024-01-02.xlsx",
    PATH / "transactions_2024-01-01.xlsx",
    PATH / "transactions_2024-01-02.xlsx",
)


def read_excels(files: List[Path] = filenames) -> List[Tuple[str, pl.DataFrame]]:
    result = []
    for file in files:
        result.append((str(file), pl.read_excel(file)))
    return result


def save_to_csv(data: List[Tuple[str, pl.DataFrame]]) -> List[str]:
    csv_filenames = []
    for filename, df in data:
        new_filename = filename.replace(".xlsx", ".csv")
        df.write_csv(new_filename)
        csv_filenames.append(new_filename)

    return csv_filenames


def create_database():
    with open(PATH / "create_dbs.sql", "r") as f:
        create_statement = f.read()

    _ = duckdb.execute(create_statement).fetchall()


def ingest_data(files: List[str]):
    customer_files = [file for file in files if "customer" in file]
    customer_files_sorted = list(sorted(customer_files))
    customers_file_1, customers_file_2 = customer_files_sorted

    transactions_files = [file for file in files if "transaction" in file]
    transactions_files_sorted = list(sorted(transactions_files))
    transactions_file_1, transactions_file_2 = transactions_files_sorted

    with open(PATH / "ingest_data.sql", "r") as f:
        ingest_statement = f.read()

    ingest_statement = ingest_statement.replace("$customers_file_1", customers_file_1)
    ingest_statement = ingest_statement.replace("$customers_file_2", customers_file_2)

    ingest_statement = ingest_statement.replace(
        "$transactions_file_1",
        transactions_file_1
    )
    ingest_statement = ingest_statement.replace(
        "$transactions_file_2",
        transactions_file_2
    )

    _ = duckdb.execute(ingest_statement)


def count_values(df: pl.DataFrame, col: str) -> int:
    count = (
        df
        .select(pl.col(col))
        .count()
        .to_dicts()[0][col]
    )
    return count


def check_results():

    # check that exactly 3 tables exist
    tables = duckdb.sql(
        "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema='alpha'"
    ).pl()
    assert count_values(tables, "table_name") == 3

    # check num rows in stage tables
    customers = duckdb.sql("SELECT * FROM my_domain.alpha.stage_customers;").pl()
    assert count_values(customers, "name") == 8

    transactions = duckdb.sql("SELECT * FROM my_domain.alpha.stage_transactions;").pl()
    assert count_values(transactions, "id") == 18

    revenues = duckdb.sql("SELECT * FROM my_domain.alpha.core_revenues;").pl()
    assert count_values(revenues, "id") == 12


def prepare_data():
    create_database()
    dfs = read_excels()
    csvs = save_to_csv(dfs)
    ingest_data(csvs)
    check_results()
