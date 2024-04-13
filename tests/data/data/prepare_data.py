"""
This module provides a fixture containing a simple data warehouse which is based
on local file storage (as raw layer) and duckdb databases.

DWH Layout:
    - dwh consists of two business domains 'payments' and 'sales'
    - each domain can have databases in stages 'test' and 'uat'
    - two business objects are loaded: 'customers' and 'transactions'
    - loading takes place into
        raw layer (local filesystem)
        staging layer (duckdb database with tables stage_customers and _transactions)
        core layer (duckdb database with table core_customer_transactions)
Constants:
    RAW_PATH: Path - path in local filesystem where DWH raw layer is stored
    DB_PATH: Path - path in local filesystem where duckdb DWB files are stored
    files: XlsxFiles - list of user-defined excel files which contain business data
    load_config: LoadConfig - configures loading of all stages

Methods:
    prepare_data: full data preparation from reading xlsx files to loading all DWH
        layers - raw, staging, core. Operates based in load_config
    clean_up: removes all DWH layers and artefacts from local filesystem
"""

from typing import List, Tuple, Union
from pathlib import Path
from dataclasses import dataclass

import polars as pl
import duckdb
from fsspec.implementations.local import LocalFileSystem
from fsspec import AbstractFileSystem


PATH = Path(__file__).parent
RAW_PATH = PATH / "raw"  # path in local filesystem where raw layer of DWH is stored
DB_PATH = PATH / "dbs"  # path in local filesystem where duckdb files are stored
FS = LocalFileSystem()  # local filesystem handler


@dataclass
class XlsxFiles:
    customers_1: Path = PATH / "customers_2024-01-01.xlsx"
    customers_2: Path = PATH / "customers_2024-01-02.xlsx"
    transactions_1: Path = PATH / "transactions_2024-01-01.xlsx"
    transactions_2: Path = PATH / "transactions_2024-01-02.xlsx"


files = XlsxFiles()


@dataclass
class RawConfig:
    """Defines loading of raw layer, e.g. file storage layer"""
    domain: str
    stage: str
    instace: str
    folder: str


@dataclass
class StageConfig:
    """Defines loading of data into staging layer, e.g. first table layer in DWH"""
    domain: str
    stage: str
    instace: str
    table: str


@dataclass
class FileConfig:
    """Defines how a file is loaded e2e"""
    xlsx_file: Path  # path to original xlsx file
    raw: List[RawConfig]  # list of configs defining which raw layers to load file to
    stage: List[StageConfig]  # list of configs defining which stage layers to load file to


@dataclass
class CoreConfig:
    """Defines if data is loaded to core layer, e.g. table customer_transactions"""
    domain: str
    stage: str
    instance: str


@dataclass
class LoadConfig:
    file_configs: List[FileConfig]
    core_configs: List[CoreConfig]


"""
# Overall loading plan:
In domain 'payments': 
    uat: only customers_1 will be loaded up to stage in instance main
    test:
        instance alpha will be loaded completely - all customer and transaction files
        instance beta will be loaded with one business date e2e, e.g. customers_1 and transactions_1 
In domain 'sales':
    uat: not loaded
    test: only customers 2 are loaded to stage in instance main

Important when loading customers 2, a loading error is simulating via truncating 
the load to 4/6 rows -- see corresponding SQL
"""

file_configs: List[FileConfig] = [
    # configure loading for customers 1
    FileConfig(
        xlsx_file=files.customers_1,
        raw=[
            RawConfig(domain="payments", stage="uat", instace="main", folder="customers"),
            RawConfig(domain="payments", stage="test", instace="alpha", folder="customers"),
            RawConfig(domain="payments", stage="test", instace="beta", folder="customers"),
        ],
        stage=[
            StageConfig(domain="payments", stage="uat", instace="main", table="customers"),
            StageConfig(domain="payments", stage="test", instace="alpha", table="customers"),
            StageConfig(domain="payments", stage="test", instace="beta", table="customers"),
        ]
    ),
    # configure loading for customers 2
    FileConfig(
        xlsx_file=files.customers_2,
        raw=[
            RawConfig(domain="payments", stage="test", instace="alpha", folder="customers"),
            RawConfig(domain="sales", stage="test", instace="main", folder="customers"),
        ],
        stage=[
            StageConfig(domain="payments", stage="test", instace="alpha", table="customers"),
            StageConfig(domain="sales", stage="test", instace="main", table="customers"),
        ]
    ),
    # configure loading for transactions 1
    FileConfig(
        xlsx_file=files.transactions_1,
        raw=[
            RawConfig(domain="payments", stage="test", instace="alpha", folder="transactions"),
            RawConfig(domain="payments", stage="test", instace="beta", folder="transactions"),
        ],
        stage=[
            StageConfig(domain="payments", stage="test", instace="alpha", table="transactions"),
            StageConfig(domain="payments", stage="test", instace="beta", table="transactions"),
        ]
    ),
    # configure loading for transactions 2
    FileConfig(
        xlsx_file=files.transactions_2,
        raw=[RawConfig(domain="payments", stage="test", instace="alpha", folder="transactions")],
        stage=[StageConfig(domain="payments", stage="test", instace="alpha", table="transactions")]
    ),
]

core_configs: List[CoreConfig] = [
    CoreConfig(domain="payments", stage="test", instance="alpha"),
    CoreConfig(domain="payments", stage="test", instance="beta")
]

load_config: LoadConfig = LoadConfig(file_configs=file_configs, core_configs=core_configs)


def setup_raw_layer(conf: LoadConfig = load_config, path: Path = RAW_PATH,
                    fs: AbstractFileSystem = FS):
    """Set up raw layer in base path: all folders and subfolders will be created"""

    print("\nSETTING UP RAW LAYER:")

    objects: List[Tuple[str, str, str, str]] = []  # list of required combos of domain/prject/folder
    for file_conf in conf.file_configs:
        for raw_conf in file_conf.raw:
            obj = (raw_conf.domain, raw_conf.stage, raw_conf.instace, raw_conf.folder)
            if obj not in objects:
                objects.append(obj)
    print("All folder objects to be created: ", objects)

    # delete existing  data in base path
    if fs.exists(path=str(path)):
        fs.rm(path=str(path), recursive=True)

    # create all folders and subfolders
    created_paths = []
    for obj in objects:
        target_path = str(path/obj[0]/obj[1]/obj[2]/obj[3])
        fs.mkdir(target_path, create_parents=True)
        created_paths.append(target_path)

    print("Created folders: ", created_paths)


def setup_databases(conf: LoadConfig = load_config, path: Path = DB_PATH,
                    fs: AbstractFileSystem = FS):

    print("\nSETTING UP DATABASES:")

    objects: List[Tuple[str, str, str, str, str]] = []
    # create unique list of domain-stage-instance-table-layer required for staging:
    for file_config in conf.file_configs:
        for stage_config in file_config.stage:
            obj = (stage_config.domain, stage_config.stage, stage_config.instace,
                   stage_config.table, "stage")
            if obj not in objects:
                objects.append(obj)

    # create same for core layer; table name is always the same here:
    for core_config in conf.core_configs:
        obj = (core_config.domain, core_config.stage, core_config.instance,
               "customer_transactions", "core")
        objects.append(obj)

    objects = list(set(objects))  # de-duplicate
    print("All database objects to be created: ", objects)

    # delete all existing duckdb database files and recreate folder:
    if fs.exists(path=str(path)):
        fs.rm(str(path), recursive=True)
    fs.mkdir(str(path), create_parents=False)

    # create databases and tables:
    for domain, stage, instance, objectname, layer in objects:
        # database files are <domain>_<stage>.db, e.g. payments_test.db
        database = domain + '_' + stage
        schema = instance  # schema always corresponds to instance
        table = layer + '_' + objectname  # table names are <layer>_<objectname>

        # create database: duckdb database files are created if not exist
        duckdb.execute(f"ATTACH IF NOT EXISTS '{str(path/database)}.db' AS {database}")

        # create tables
        if table == "stage_customers":
            tableschema = (
                "(date STRING, id INTEGER, region STRING, type STRING, name STRING,"
                "source_file STRING)"
            )
        elif table == "stage_transactions":
            tableschema = (
                "(date STRING, id INTEGER, customer_id INTEGER, amount FLOAT,"
                "source_file STRING)"
            )
        elif table == "core_customer_transactions":
            tableschema = (
                "(id INTEGER, transaction_date DATE, amount INTEGER, customer_id INTEGER,"
                "customer_name STRING, customer_type STRING, customer_region STRING)"
            )
        else:
            raise ValueError(f"Unknown tablename {table}")

        duckdb.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{schema};")
        duckdb.execute(
            f"CREATE TABLE IF NOT EXISTS {database}.{schema}.{table} {tableschema};")

    created_tables = duckdb.sql("""
        SELECT * FROM INFORMATION_SCHEMA.TABLES
        ORDER BY table_catalog, table_schema, table_name
    """).pl()
    print("Created tables: ", created_tables)


def get_csv_raw_path(xlsx_path: Path, conf: Union[RawConfig, StageConfig],
                     raw_layer_base_path: Path = RAW_PATH) -> str:
    """Based on path of xlsx file, base path of raw_layer and config,
    get target csv filepath in raw layer"""
    xlsx_filename = xlsx_path.name
    csv_filename = xlsx_filename.replace(".xlsx", ".csv")

    if isinstance(conf, RawConfig):
        obj = conf.folder
    else:
        obj = conf.table

    csv_path = (raw_layer_base_path / conf.domain / conf.stage / conf.instace /
                obj / csv_filename)
    return str(csv_path)


def load_raw_layer(conf: LoadConfig = load_config, path: Path = RAW_PATH):
    """Reads xslx files and loads them into raw layer - e.g. local folders"""
    print("\nLOADING RAW LAYER:")
    loaded_files = []
    for file_config in conf.file_configs:
        xlsx_filepath = file_config.xlsx_file
        df = pl.read_excel(xlsx_filepath)
        for raw_config in file_config.raw:
            csv_filepath = get_csv_raw_path(
                xlsx_path=xlsx_filepath,
                conf=raw_config,
                raw_layer_base_path=path
            )
            df.write_csv(csv_filepath)
            loaded_files.append(csv_filepath)
    print("Raw layer loaded files: ", loaded_files)


def load_staging_layer(conf: LoadConfig = load_config):
    """
    Load CSVs into staging tables. Preconditions:
        - tables and databases must exist in duckdb - see setup_databases
        - CSV files must exist in raw layer - see load_raw_layer
    """
    print("\nLOADING STAGING LAYER:")
    loaded_tables: List[str] = []
    for file_config in conf.file_configs:
        xlsx_filepath = file_config.xlsx_file
        for stage_config in file_config.stage:
            csv_filepath = get_csv_raw_path(
                xlsx_path=xlsx_filepath,
                conf=stage_config,
            )
            database = stage_config.domain + '_' + stage_config.stage
            schema = stage_config.instace
            table = "stage_" + stage_config.table
            filename = csv_filepath.split('/')[-1]

            # truncate loading of customers 2 to 4/6 rows simulate load errors
            limit_clause = "LIMIT 4" if xlsx_filepath == files.customers_2 else ""
            duckdb.execute(f"""
                INSERT INTO {database}.{schema}.{table} 
                SELECT *, '{filename}' AS source_file FROM '{csv_filepath}' 
                {limit_clause};
            """)
            loaded_tables.append(database + '.' + schema + '.' + table)

    loaded_tables = list(sorted(set(loaded_tables)))
    print("Loaded staging tables: ", loaded_tables)

    # check that exactly 8 customers are loaded into paymets alpha
    customers = duckdb.sql("SELECT * FROM payments_test.alpha.stage_customers").pl()
    customer_count = count_values(df=customers, col="name")
    assert customer_count == 8
    print(f"Loaded {customer_count} customers into paymets.alpha.stage_customers")

    # check that all 18 transactions are loaded into payments alpha
    transactions = duckdb.sql("SELECT * FROM payments_test.alpha.stage_transactions").pl()
    transactions_count = count_values(df=transactions, col="id")
    assert transactions_count == 18
    print(f"Loaded {transactions_count} transactions into paymets.alpha.stage_transactions")


def count_values(df: pl.DataFrame, col: str) -> int:
    """Count number of rows in a given column of a polars dataframe"""
    count = (
        df
        .select(pl.col(col))
        .count()
        .to_dicts()[0][col]
    )
    return count


def load_core_layer(conf: LoadConfig = load_config):

    print("\nLOADING CORE LAYER:")
    for core_config in conf.core_configs:
        database = core_config.domain + '_' + core_config.stage
        schema = core_config.instance

        duckdb.execute(f"""
            INSERT INTO {database}.{schema}.core_customer_transactions
                SELECT
                    transactions.id,
                    transactions.date AS transaction_date,
                    transactions.amount,
                    transactions.customer_id,
                    customers.name AS customer_name,
                    customers.type AS customer_type,
                    customers.region AS customer_region,

                FROM {database}.{schema}.stage_transactions AS transactions
                LEFT JOIN {database}.{schema}.stage_customers AS customers
                    ON transactions.customer_id = customers.id
                    AND transactions.date = customers.date
            
                WHERE customer_region != 'africa' 
        """)

    # check that all 18 transactions are loaded into payments alpha
    customer_transactions = duckdb.sql(
        "SELECT * FROM payments_test.alpha.core_customer_transactions").pl()
    count = count_values(df=customer_transactions, col="id")
    assert count == 12
    print(f"Loaded {count} transactions into paymets.alpha.core_customer_transactions")


def prepare_data():
    setup_raw_layer()
    setup_databases()
    load_raw_layer()
    load_staging_layer()
    load_core_layer()


def clean_up(db_path: Path = DB_PATH, raw_path: Path = RAW_PATH,
             fs: AbstractFileSystem = FS):

    print("\nDELETING RAW LAYER")
    if fs.exists(str(raw_path)):
        fs.rm(str(raw_path), recursive=True)

    print("DELETING DWH LAYER")
    if fs.exists(str(db_path)):
        duck_db_files = []
        files_in_db_path: List[str] = fs.ls(str(db_path))
        for file in files_in_db_path:
            if file.endswith(".db"):
                duck_db_files.append(file)

        for duck_db_file in duck_db_files:
            db_name = duck_db_file.split('/')[-1].removesuffix('.db')
            duckdb.execute(f"DETACH {db_name};")

    if fs.exists(str(db_path)):
        fs.rm(str(db_path), recursive=True)
