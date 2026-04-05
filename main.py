"""Entrypoint for the Data Tester HTTP backend.

Usage:
    uv run python main.py

Set configuration via a .env file in the project root (see .env.example).
If DATATESTER_DATA_PLATFORM=DEMO, demo data is generated and seeded on every run.
"""

import os
from pathlib import Path

import uvicorn

from src.apps.http_app import create_app
from src.apps.http_di import HttpDependencyInjector
from src.config import Config
from src.dtos import DomainConfigDTO, TestSetDTO


def _setup_demo(config: Config) -> HttpDependencyInjector:
    """Generate demo DWH + artifacts, seed dto storage, return ready DI injector."""
    from tests.fixtures.demo.prepare_demo_artifacts import prepare_demo_artifacts
    from tests.fixtures.demo.prepare_demo_data import prepare_demo_data

    demo_base = Path("data/demo").resolve()

    # Use absolute paths so all storage engines resolve correctly
    config.DATATESTER_INTERNAL_STORAGE_LOCATION = f"local://{demo_base}/"
    config.DATATESTER_DEMO_RAW_PATH = str(demo_base / "raw")
    config.DATATESTER_DEMO_DB_PATH = str(demo_base / "dbs")

    print("Setting up demo data...")
    prepare_demo_data(demo_base)
    prepare_demo_artifacts(demo_base)

    # Seed dto storage: prepare_demo_artifacts writes to {demo_base}/configs/ and
    # {demo_base}/testsets/, but LocalDtoStorage expects domain_configs/ and testsets/.
    di = HttpDependencyInjector(config)

    dc_driver = di.domain_config_driver()
    for cfg_file in sorted((demo_base / "configs").glob("*.json")):
        dc_driver.save_domain_config(config=DomainConfigDTO.from_json(cfg_file.read_text()))

    ts_driver = di.testset_driver()
    for ts_file in sorted((demo_base / "testsets").rglob("*.json")):
        ts_driver.save_testset(testset=TestSetDTO.from_json(ts_file.read_text()))

    return di


def main() -> None:
    is_local = os.environ.get("DATATESTER_ENV", "LOCAL") == "LOCAL"
    config = Config(_env_file=".env" if is_local else None)
    di: HttpDependencyInjector | None = None

    if config.DATATESTER_DATA_PLATFORM == "DEMO":
        di = _setup_demo(config)

    app = create_app(config, di=di)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
