"""Unit tests for Controller using InMemoryState (no NiceGUI required)."""

from __future__ import annotations

import time
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.dtos import (
    DomainConfigDTO,
    Result,
    SpecEntryDTO,
    TestCaseEntryDTO,
    TestRunDTO,
    TestSetDTO,
    TestType,
)
from src.dtos import Status as RunStatus
from src.dtos.storage_dtos import LocationDTO
from src.ui.client import DataTesterClient
from src.ui.config import UIConfig
from src.ui.controller import Controller

from tests.unit.ui.in_memory_state import InMemoryState


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

_DEFAULT_SECRET = "a" * 32  # satisfies 32-char minimum


def _make_config(**kwargs: object) -> UIConfig:
    defaults: dict[str, object] = {
        "DATATESTER_UI_STORAGE_SECRET": _DEFAULT_SECRET,
        "DATATESTER_UI_TTL_TESTSETS": 60,
        "DATATESTER_UI_TTL_TESTOBJECTS": 60,
        "DATATESTER_UI_TTL_TESTRUNS": 60,
        "DATATESTER_UI_TTL_SPECS": 10,
        "DATATESTER_UI_TTL_DOMAIN_CONFIGS": 60,
    }
    defaults.update(kwargs)
    return UIConfig(**defaults)  # type: ignore


def _make_domain_config(domain: str = "sales") -> DomainConfigDTO:
    return DomainConfigDTO(
        domain=domain,
        instances={"test": ["alpha"]},
        compare_datatypes=["string", "integer"],
        sample_size_default=100,
        spec_locations={"test": ["local:///specs/"]},
        reports_location=LocationDTO("local:///reports/"),
    )


def _make_testset(domain: str = "sales", stage: str = "test") -> TestSetDTO:
    tc = TestCaseEntryDTO(domain=domain, testobject="orders", testtype=TestType.SCHEMA)
    return TestSetDTO(
        name="orders_ts",
        domain=domain,
        default_stage=stage,
        default_instance="alpha",
        testcases={tc.identifier: tc},
    )


def _make_testrun(domain: str = "sales") -> TestRunDTO:
    cfg = _make_domain_config(domain)
    return TestRunDTO(
        id=uuid4(),
        testset_id=uuid4(),
        domain=domain,
        stage="test",
        instance="alpha",
        result=Result.OK,
        status=RunStatus.FINISHED,
        start_ts=datetime.now(),
        testset_name="orders_ts",
        domain_config=cfg,
    )


def _make_controller(
    state: InMemoryState | None = None,
    client: DataTesterClient | None = None,
    config: UIConfig | None = None,
) -> Controller:
    state = state or InMemoryState()
    client = client or AsyncMock(spec=DataTesterClient)
    config = config or _make_config()
    return Controller(client=client, state=state, config=config)


# ---------------------------------------------------------------------------
# build_testrun_def
# ---------------------------------------------------------------------------


def test_build_testrun_def_specs_not_loaded_returns_error() -> None:
    state = InMemoryState()
    cfg = _make_domain_config()
    state.domain_configs = {"sales": cfg}
    state.domain = "sales"
    controller = _make_controller(state=state)

    ts = _make_testset()
    result, err = controller.build_testrun_def("sales", ts)

    assert result is None
    assert err is not None
    assert "not loaded" in err.lower() or "specs" in err.lower()


def test_build_testrun_def_success() -> None:
    state = InMemoryState()
    cfg = _make_domain_config()
    state.domain_configs = {"sales": cfg}
    state.domain = "sales"

    # Seed specs for the testobject/testtype used in testset
    spec_entry = SpecEntryDTO(
        testobject_name="orders",
        testtype=TestType.SCHEMA,
        scenario=None,
        specs=[],
    )
    state.set_specs("sales", "test", [spec_entry])

    controller = _make_controller(state=state)

    ts = _make_testset()
    testrun_def, err = controller.build_testrun_def("sales", ts)

    assert err is None
    assert testrun_def is not None
    assert testrun_def.domain == "sales"
    assert len(testrun_def.testcase_defs) == 1
    assert testrun_def.testcase_defs[0].testtype == TestType.SCHEMA


# ---------------------------------------------------------------------------
# testruns() — merge with preliminary
# ---------------------------------------------------------------------------


def test_testruns_merges_preliminary_extras() -> None:
    state = InMemoryState()
    loaded_run = _make_testrun()
    preliminary_run = _make_testrun()  # different ID

    state.set_testruns("sales", [loaded_run])
    state.add_preliminary_testrun("sales", preliminary_run)

    controller = _make_controller(state=state)
    result = controller.testruns("sales")

    assert len(result) == 2
    ids = {str(r.id) for r in result}
    assert str(loaded_run.id) in ids
    assert str(preliminary_run.id) in ids


def test_testruns_preliminary_deduplicated_when_loaded() -> None:
    state = InMemoryState()
    run = _make_testrun()

    state.set_testruns("sales", [run])
    state.add_preliminary_testrun("sales", run)  # same ID

    controller = _make_controller(state=state)
    result = controller.testruns("sales")

    # Preliminary run with same ID is suppressed — only one entry
    assert len(result) == 1


# ---------------------------------------------------------------------------
# save_testset
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_testset_new_appends() -> None:
    state = InMemoryState()
    state.set_testsets("sales", [])

    client = AsyncMock(spec=DataTesterClient)
    client.save_testset = AsyncMock(return_value=None)

    controller = _make_controller(state=state, client=client)
    ts = _make_testset()
    err = await controller.save_testset("sales", ts)

    assert err is None
    assert len(state.testsets.get("sales", [])) == 1
    assert state.testsets["sales"][0].name == "orders_ts"


@pytest.mark.asyncio
async def test_save_testset_existing_updates_in_place() -> None:
    state = InMemoryState()
    ts = _make_testset()
    state.set_testsets("sales", [ts])

    client = AsyncMock(spec=DataTesterClient)
    client.save_testset = AsyncMock(return_value=None)

    # Modify the testset (same ID, new name)
    updated = TestSetDTO(
        testset_id=ts.testset_id,
        name="orders_ts_v2",
        domain="sales",
        default_stage="test",
        default_instance="alpha",
        testcases=ts.testcases,
    )
    controller = _make_controller(state=state, client=client)
    err = await controller.save_testset("sales", updated)

    assert err is None
    saved = state.testsets["sales"]
    assert len(saved) == 1
    assert saved[0].name == "orders_ts_v2"


# ---------------------------------------------------------------------------
# TTL staleness
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_testsets_skips_when_fresh() -> None:
    state = InMemoryState()
    state.set_last_loaded("sales", "testsets")  # mark as just loaded

    client = AsyncMock(spec=DataTesterClient)
    client.get_testsets = AsyncMock(return_value=[])

    controller = _make_controller(state=state, client=client)
    await controller.load_testsets("sales")

    client.get_testsets.assert_not_called()


@pytest.mark.asyncio
async def test_load_testsets_reloads_when_stale() -> None:
    state = InMemoryState()
    # Manually set a timestamp far in the past
    state._last_loaded["sales_testsets"] = time.time() - 9999

    client = AsyncMock(spec=DataTesterClient)
    client.get_testsets = AsyncMock(return_value=[])

    controller = _make_controller(state=state, client=client)
    await controller.load_testsets("sales")

    client.get_testsets.assert_called_once_with("sales")
