from __future__ import annotations

from abc import ABC, abstractmethod

from src.dtos import DomainConfigDTO, SpecEntryDTO, TestObjectDTO, TestRunDTO, TestSetDTO
from src.ui.common import Status


class StateError(Exception):
    """"""


class State(ABC):
    """Typed state contract."""

    @property
    @abstractmethod
    def domain_configs(self) -> dict[str, DomainConfigDTO]:
        pass

    @domain_configs.setter
    @abstractmethod
    def domain_configs(self, val: dict[str, DomainConfigDTO]) -> None:
        pass

    @property
    @abstractmethod
    def domains(self) -> list[str]:
        pass

    @domains.setter
    @abstractmethod
    def domains(self, val: list[str]) -> None:
        pass

    @property
    @abstractmethod
    def domain_configs_status(self) -> dict[str, Status]:
        pass

    @abstractmethod
    def set_domain_config_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def testsets(self) -> dict[str, list[TestSetDTO]]:
        pass

    @abstractmethod
    def set_testsets(self, domain: str, testsets: list[TestSetDTO]) -> None:
        pass

    @property
    @abstractmethod
    def testsets_status(self) -> dict[str, Status]:
        pass

    @abstractmethod
    def set_testsets_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def testobjects(self) -> dict[str, list[TestObjectDTO]]:
        pass

    @abstractmethod
    def set_testobjects(self, domain: str, testobjects: list[TestObjectDTO]) -> None:
        pass

    @property
    @abstractmethod
    def testobjects_status(self) -> dict[str, Status]:
        pass

    @abstractmethod
    def set_testobjects_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def testruns(self) -> dict[str, list[TestRunDTO]]:
        pass

    @abstractmethod
    def set_testruns(self, domain: str, testruns: list[TestRunDTO]) -> None:
        pass

    @property
    @abstractmethod
    def testruns_status(self) -> dict[str, Status]:
        pass

    @abstractmethod
    def set_testruns_status(self, domain: str, status: Status) -> None:
        pass

    @abstractmethod
    def specs(self, domain: str) -> dict[str, list[SpecEntryDTO]]:
        pass

    @abstractmethod
    def set_specs(
        self, domain: str, stage: str, entries: list[SpecEntryDTO]
    ) -> None:
        pass

    @property
    @abstractmethod
    def specs_status(self) -> dict[str, Status]:
        pass

    @abstractmethod
    def set_specs_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def domain(self) -> str | None:
        pass

    @domain.setter
    @abstractmethod
    def domain(self, val: str | None) -> None:
        pass

    @property
    @abstractmethod
    def domain_config(self) -> DomainConfigDTO:
        pass

    @abstractmethod
    def preliminary_testruns(self, domain: str) -> list[TestRunDTO]:
        """Testruns submitted but not yet confirmed by the backend."""
        pass

    @abstractmethod
    def add_preliminary_testrun(self, domain: str, testrun: TestRunDTO) -> None:
        pass

    @abstractmethod
    def remove_preliminary_testrun(self, domain: str, testrun_id: str) -> None:
        pass

    @abstractmethod
    def get_last_loaded(self, domain: str, data_type: str) -> float | None:
        """Return the Unix timestamp of the last successful load, or None."""
        pass

    @abstractmethod
    def set_last_loaded(self, domain: str, data_type: str) -> None:
        """Record the current time as the last successful load timestamp."""
        pass

    @abstractmethod
    def invalidate_last_loaded(self, domain: str, data_type: str) -> None:
        """Clear the last-loaded timestamp, forcing a reload on next access."""
        pass
