"""
Integration tests for the FastAPI HTTP backend.

Tests the full pipeline against the demo backend, following the same
setup pattern as test_cli_app.py.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.apps.http_app import create_app
from src.apps.http_di import HttpDependencyInjector
from src.config import Config
from src.domain_ports import SaveTestSetCommand
from src.dtos import DomainConfigDTO, TestSetDTO
from tests.fixtures.demo.prepare_demo_artifacts import (
    clean_up_demo_artifacts,
    prepare_demo_artifacts,
)
from tests.fixtures.demo.prepare_demo_data import prepare_demo_data

_DEMO_DIR = Path(__file__).parent / "_demo_data_http"


def _make_config() -> Config:
    return Config(
        DATATESTER_DATA_PLATFORM="DEMO",
        DATATESTER_USER_STORAGE_ENGINE="LOCAL",
        DATATESTER_INTERNAL_STORAGE_LOCATION=f"local://{_DEMO_DIR}/internal/",
        DATATESTER_DEMO_RAW_PATH=str(_DEMO_DIR / "raw"),
        DATATESTER_DEMO_DB_PATH=str(_DEMO_DIR / "dbs"),
    )


@pytest.fixture(scope="module")
def demo_client():
    clean_up_demo_artifacts(_DEMO_DIR)
    prepare_demo_data(_DEMO_DIR)
    prepare_demo_artifacts(_DEMO_DIR)

    config = _make_config()
    di = HttpDependencyInjector(config)

    dc_driver = di.domain_config_driver()
    configs_dir = _DEMO_DIR / "configs"
    for cfg_file in sorted(configs_dir.glob("*.json")):
        dto = DomainConfigDTO.from_json(cfg_file.read_text())
        dc_driver.save_domain_config(config=dto)

    ts_driver = di.testset_driver()
    testsets_dir = _DEMO_DIR / "testsets"
    for ts_file in sorted(testsets_dir.rglob("*.json")):
        dto = TestSetDTO.from_json(ts_file.read_text())
        ts_driver.adapter.save_testset(SaveTestSetCommand(testset=dto))

    app = create_app(config)
    with TestClient(app) as client:
        yield client

    clean_up_demo_artifacts(_DEMO_DIR)


class TestDomainConfigEndpoints:
    def test_list_domain_configs_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/domain-config")
        assert response.status_code == 200
        data = response.json()
        assert "payments" in data
        assert "sales" in data

    def test_load_domain_config_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/domain-config/payments")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "payments"

    def test_put_domain_config_returns_204(self, demo_client: TestClient):
        get_resp = demo_client.get("/domain-config/payments")
        assert get_resp.status_code == 200
        dto = get_resp.json()
        put_resp = demo_client.put("/domain-config/payments", json=dto)
        assert put_resp.status_code == 204


class TestTestSetEndpoints:
    def test_list_testsets_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/payments/testset")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_load_testset_returns_200(self, demo_client: TestClient):
        list_resp = demo_client.get("/payments/testset")
        testsets = list_resp.json()
        testset_id = testsets[0]["testset_id"]
        response = demo_client.get(f"/payments/testset/{testset_id}")
        assert response.status_code == 200
        assert response.json()["testset_id"] == testset_id


class TestTestRunEndpoints:
    def test_list_testruns_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/payments/testrun/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_post_testrun_returns_202_with_testrun_id(self, demo_client: TestClient):
        # Get domain config
        dc_resp = demo_client.get("/domain-config/payments")
        domain_config = dc_resp.json()

        # Get testset
        ts_resp = demo_client.get("/payments/testset")
        testsets = ts_resp.json()
        testset = next(t for t in testsets if t["name"] == "payments_full")

        # Find specifications
        specs_locations = domain_config["specifications_locations"]
        if isinstance(specs_locations, dict):
            locations = list(specs_locations.values())
            if locations and isinstance(locations[0], list):
                locations = locations[0]
        elif isinstance(specs_locations, list):
            locations = specs_locations
        else:
            locations = [specs_locations]
        find_body = {"testset": testset, "locations": locations}
        specs_resp = demo_client.post("/payments/specification/find", json=find_body)
        assert specs_resp.status_code == 200
        spec_list = specs_resp.json()

        # Execute testrun
        body = {
            "testset": testset,
            "domain_config": domain_config,
            "spec_list": spec_list,
        }
        response = demo_client.post("/payments/testrun/", json=body)
        assert response.status_code == 202
        data = response.json()
        assert "testrun_id" in data
        return data["testrun_id"]

    def test_load_testrun_returns_200_after_execution(self, demo_client: TestClient):
        # Get domain config
        dc_resp = demo_client.get("/domain-config/payments")
        domain_config = dc_resp.json()

        # Get testset
        ts_resp = demo_client.get("/payments/testset")
        testsets = ts_resp.json()
        testset = next(t for t in testsets if t["name"] == "payments_full")

        # Find specifications
        specs_locations = domain_config["specifications_locations"]
        if isinstance(specs_locations, dict):
            locations = list(specs_locations.values())
            if locations and isinstance(locations[0], list):
                locations = locations[0]
        elif isinstance(specs_locations, list):
            locations = specs_locations
        else:
            locations = [specs_locations]
        find_body = {"testset": testset, "locations": locations}
        specs_resp = demo_client.post("/payments/specification/find", json=find_body)
        spec_list = specs_resp.json()

        # Execute testrun
        body = {
            "testset": testset,
            "domain_config": domain_config,
            "spec_list": spec_list,
        }
        response = demo_client.post("/payments/testrun/", json=body)
        assert response.status_code == 202
        testrun_id = response.json()["testrun_id"]

        # TestClient runs background tasks synchronously, so load immediately
        get_resp = demo_client.get(f"/payments/testrun/{testrun_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["testrun_id"] == testrun_id
