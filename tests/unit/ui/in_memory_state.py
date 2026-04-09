"""In-memory State implementation for unit tests.

No NiceGUI dependencies — uses plain Python dicts.
"""

from __future__ import annotations

import time

from src.dtos import DomainConfigDTO, SpecEntryDTO, TestObjectDTO, TestRunDTO, TestSetDTO
from src.ui.common import Status
from src.ui.controller.state import State, StateError


class InMemoryState(State):
    """Plain-dict State for unit testing. No NiceGUI required."""

    def __init__(self) -> None:
        self._domain_configs: dict[str, DomainConfigDTO] = {}
        self._domains: list[str] = []
        self._domain_configs_status: dict[str, Status] = {}
        self._testsets: dict[str, list[TestSetDTO]] = {}
        self._testsets_status: dict[str, Status] = {}
        self._testobjects: dict[str, list[TestObjectDTO]] = {}
        self._testobjects_status: dict[str, Status] = {}
        self._testruns: dict[str, list[TestRunDTO]] = {}
        self._testruns_status: dict[str, Status] = {}
        self._specs: dict[str, dict[str, list[SpecEntryDTO]]] = {}
        self._specs_status: dict[str, Status] = {}
        self._domain: str | None = None
        self._preliminary_testruns: dict[str, dict[str, TestRunDTO]] = {}
        self._last_loaded: dict[str, float] = {}

    @property
    def domain_configs(self) -> dict[str, DomainConfigDTO]:
        return dict(self._domain_configs)

    @domain_configs.setter
    def domain_configs(self, val: dict[str, DomainConfigDTO]) -> None:
        self._domain_configs = dict(val)

    @property
    def domains(self) -> list[str]:
        return list(self._domains)

    @domains.setter
    def domains(self, val: list[str]) -> None:
        self._domains = list(val)

    @property
    def domain_configs_status(self) -> dict[str, Status]:
        return dict(self._domain_configs_status)

    def set_domain_config_status(self, domain: str, status: Status) -> None:
        self._domain_configs_status[domain] = status

    @property
    def testsets(self) -> dict[str, list[TestSetDTO]]:
        return {k: list(v) for k, v in self._testsets.items()}

    def set_testsets(self, domain: str, testsets: list[TestSetDTO]) -> None:
        self._testsets[domain] = list(testsets)

    @property
    def testsets_status(self) -> dict[str, Status]:
        return dict(self._testsets_status)

    def set_testsets_status(self, domain: str, status: Status) -> None:
        self._testsets_status[domain] = status

    @property
    def testobjects(self) -> dict[str, list[TestObjectDTO]]:
        return {k: list(v) for k, v in self._testobjects.items()}

    def set_testobjects(self, domain: str, testobjects: list[TestObjectDTO]) -> None:
        self._testobjects[domain] = list(testobjects)

    @property
    def testobjects_status(self) -> dict[str, Status]:
        return dict(self._testobjects_status)

    def set_testobjects_status(self, domain: str, status: Status) -> None:
        self._testobjects_status[domain] = status

    @property
    def testruns(self) -> dict[str, list[TestRunDTO]]:
        return {k: list(v) for k, v in self._testruns.items()}

    def set_testruns(self, domain: str, testruns: list[TestRunDTO]) -> None:
        self._testruns[domain] = list(testruns)

    @property
    def testruns_status(self) -> dict[str, Status]:
        return dict(self._testruns_status)

    def set_testruns_status(self, domain: str, status: Status) -> None:
        self._testruns_status[domain] = status

    def specs(self, domain: str) -> dict[str, list[SpecEntryDTO]]:
        return {k: list(v) for k, v in self._specs.get(domain, {}).items()}

    def set_specs(self, domain: str, stage: str, entries: list[SpecEntryDTO]) -> None:
        if domain not in self._specs:
            self._specs[domain] = {}
        self._specs[domain][stage] = list(entries)

    @property
    def specs_status(self) -> dict[str, Status]:
        return dict(self._specs_status)

    def set_specs_status(self, domain: str, status: Status) -> None:
        self._specs_status[domain] = status

    @property
    def domain(self) -> str | None:
        return self._domain

    @domain.setter
    def domain(self, val: str | None) -> None:
        if val is not None and val not in self._domain_configs:
            raise StateError(f"Domain {val} doesn't exist")
        self._domain = val

    @property
    def domain_config(self) -> DomainConfigDTO:
        if self._domain is None:
            raise StateError("No domain is selected.")
        return self._domain_configs[self._domain]

    def preliminary_testruns(self, domain: str) -> list[TestRunDTO]:
        return list(self._preliminary_testruns.get(domain, {}).values())

    def add_preliminary_testrun(self, domain: str, testrun: TestRunDTO) -> None:
        if domain not in self._preliminary_testruns:
            self._preliminary_testruns[domain] = {}
        self._preliminary_testruns[domain][str(testrun.id)] = testrun

    def remove_preliminary_testrun(self, domain: str, testrun_id: str) -> None:
        self._preliminary_testruns.get(domain, {}).pop(testrun_id, None)

    def get_last_loaded(self, domain: str, data_type: str) -> float | None:
        return self._last_loaded.get(f"{domain}_{data_type}")

    def set_last_loaded(self, domain: str, data_type: str) -> None:
        self._last_loaded[f"{domain}_{data_type}"] = time.time()

    def invalidate_last_loaded(self, domain: str, data_type: str) -> None:
        self._last_loaded.pop(f"{domain}_{data_type}", None)
