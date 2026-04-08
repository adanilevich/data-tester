from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from nicegui import app

from src.client_interface import TestSetDTO, DomainConfigDTO
from src.ui.common import Status

class StateError(Exception):
    """"""


class State(ABC):
    """Typed state contract. Each property maps to a named object in a storage scope.

    storage.general: domain_configs, domains
    storage.user:    domain_selection
    """

    # --- storage.general ---

    @property
    @abstractmethod
    def domain_configs(self) -> Dict[str, DomainConfigDTO]:
        pass

    @domain_configs.setter
    @abstractmethod
    def domain_configs(self, val: Dict[str, DomainConfigDTO]) -> None:
        pass

    @property
    @abstractmethod
    def domains(self) -> List[str]:
        pass

    @domains.setter
    @abstractmethod
    def domains(self, val: List[str]) -> None:
        pass

    @property
    @abstractmethod
    def testsets(self) -> Dict[str, List[TestSetDTO]]:
        pass

    @abstractmethod
    def set_testsets(self, domain: str, testsets: List[TestSetDTO]):
        pass

    @property
    @abstractmethod
    def testsets_status(self) -> Dict[str, Status]:
        pass

    @abstractmethod
    def set_testsets_status(self, domain: str, status: Status):
        pass

    # --- storage.user ---

    @property
    @abstractmethod
    def domain(self) -> str | None:
        pass

    @domain.setter
    @abstractmethod
    def domain(self, val: str) -> None:
        pass

    @property
    @abstractmethod
    def domain_config(self) -> DomainConfigDTO:
        pass

    @domain_config.setter
    @abstractmethod
    def domain_config(self, val: DomainConfigDTO) -> None:
        pass


class NiceGuiState(State):
    """
    Concrete State backed by app.storage.*. Never caches storage objects.
    State must handle de/serialization and return/receive only DTOs
    """

    # --- storage.general ---

    @property
    def domain_configs(self) -> Dict[str, DomainConfigDTO]:
        cfgs_ = app.storage.general.get("domain_configs", {})
        cfgs = {k: DomainConfigDTO.model_validate(v) for k, v in cfgs_.items()}
        return cfgs

    @domain_configs.setter
    def domain_configs(self, val: Dict[str, DomainConfigDTO]) -> None:
        cfgs = {k: v.to_dict() for k, v in val.items()}
        app.storage.general["domain_configs"] = cfgs

    @property
    def domains(self) -> list[str]:
        return app.storage.general.get("domains", [])

    @domains.setter
    def domains(self, value: list[str]) -> None:
        app.storage.general["domains"] = value

    @property
    def testsets(self) -> Dict[str, List[TestSetDTO]]:
        ts_ = app.storage.general.get("testsets", {})
        ts = {
            domain: [TestSetDTO.model_validate(v) for v in serialized_testsets]
            for domain, serialized_testsets in ts_.items()
        }
        return ts

    def set_testsets(self, domain: str, testsets: List[TestSetDTO]):
        testsets_ = [testset.to_dict() for testset in testsets]
        app.storage.general.setdefault("testsets", {})[domain] = testsets_

    @property
    def testsets_status(self) -> Dict[str, Status]:
        """Dict, keyed by domain name"""
        raw = app.storage.general.get("testsets_status", {})
        return {domain: Status(status) for domain, status in raw.items()}

    def set_testsets_status(self, domain: str, status: Status):
        app.storage.general.setdefault("testsets_status", {})[domain] = status

    # --- storage.user ---

    @property
    def domain(self) -> str | None:
        return app.storage.user.get("domain")

    @domain.setter
    def domain(self, val: str | None) -> None:
        if val not in self.domain_configs:
            raise StateError(f"Domain {val} doesn't exist")
        app.storage.user["domain"] = val

    @property
    def domain_config(self) -> DomainConfigDTO:
        domain_selection = self.domain
        if domain_selection is None:
            msg = "No domain is selected."
            raise StateError(msg)
        return self.domain_configs[domain_selection]

    @domain_config.setter
    def domain_config(self, val: DomainConfigDTO) -> None:
        if self.domain is None:
            raise StateError("Can not set domain config: No domain is selected")
        if val.domain not in self.domain_configs:
            raise StateError("Can not set domain config: domain not in backend DTOs")
        self.domain_config = val
