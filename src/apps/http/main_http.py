"""Entrypoint for the Data Tester HTTP backend.

Usage:
    uv run python -m src.apps.http.main_http

Set configuration via a .env file in the project root (see .env.example).
If DATATESTER_DATA_PLATFORM=DEMO, demo data is generated and seeded on every run.
"""

import os
from pathlib import Path

import uvicorn
from src.apps.http.app import create_app
from src.config import Config

from tests.fixtures.demo.prepare_demo_artifacts import (
    clean_up_demo_artifacts,
    prepare_demo_artifacts,
)
from tests.fixtures.demo.prepare_demo_data import clean_up_demo_data, prepare_demo_data


def _setup_demo(config: Config) -> None:
    """Generate demo DWH + artifacts and configure storage paths.

    prepare_demo_artifacts writes directly to internal/domain_configs/ and
    internal/testsets/ — the paths LocalDtoStorage reads from — so no seeding
    step is needed.
    """
    # this will resolve to CURRENT working directory, not file path, i.e.
    # if we run this from root, it will write data to root, as expected
    demo_base = Path("data/demo").resolve()

    # Use absolute paths so all storage engines resolve correctly
    config.DATATESTER_INTERNAL_STORAGE_LOCATION = f"local://{demo_base}/internal/"
    config.DATATESTER_DEMO_RAW_PATH = str(demo_base / "raw")
    config.DATATESTER_DEMO_DB_PATH = str(demo_base / "dbs")

    print("Cleaning up demo data...")
    clean_up_demo_artifacts(demo_base)
    clean_up_demo_data(demo_base)

    print("Setting up demo data...")
    prepare_demo_data(demo_base)
    prepare_demo_artifacts(demo_base)


def main() -> None:
    is_local = os.environ.get("DATATESTER_ENV", "LOCAL") == "LOCAL"
    config = Config(_env_file=".env" if is_local else None)  # ty: ignore[unknown-argument]

    if config.DATATESTER_DATA_PLATFORM == "DEMO":
        _setup_demo(config)

    app = create_app(config)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
