"""Async HTTP client for the Data Tester backend API.

Only imports from src.dtos and src.client_interface (import-linter contract 12).
"""

from typing import Any

import httpx

from src.client_interface import DomainConfigDTO, TestObjectDTO, TestRunDTO, TestSetDTO
from src.client_interface.requests import FindSpecsRequest
from src.dtos import TestRunDefDTO


class BackendError(Exception):
    """Raised when the backend returns an unexpected response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Backend error {status_code}: {detail}")


class DataTesterClient:
    """Async HTTP client for the Data Tester FastAPI backend."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def _get(self, path: str) -> Any:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30.0) as client:
            response = await client.get(path)
            if not response.is_success:
                raise BackendError(status_code=response.status_code, detail=response.text)
            return response.json()

    async def _post(self, path: str, body: Any) -> Any:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30.0) as client:
            response = await client.post(path, json=body)
            if not response.is_success:
                raise BackendError(status_code=response.status_code, detail=response.text)
            return response.json()

    async def _put(self, path: str, body: Any) -> None:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30.0) as client:
            response = await client.put(path, json=body)
            if not response.is_success:
                raise BackendError(status_code=response.status_code, detail=response.text)

    async def get_domain_configs(self) -> dict[str, DomainConfigDTO]:
        """Fetch all domain configurations from the backend."""
        data: dict[str, Any] = await self._get("/domain-config")
        return {
            domain: DomainConfigDTO.model_validate(cfg) for domain, cfg in data.items()
        }

    async def get_domain_config(self, domain: str) -> DomainConfigDTO:
        """Fetch a single domain configuration by domain name."""
        data: Any = await self._get(f"/domain-config/{domain}")
        return DomainConfigDTO.model_validate(data)

    async def get_testsets(self, domain: str) -> list[TestSetDTO]:
        """Fetch testsets by domain name."""
        data: Any = await self._get(f"/{domain}/testset")
        return [TestSetDTO.model_validate(testset) for testset in data]

    async def get_testobjects(
        self, domain: str, stage: str, instance: str
    ) -> list[TestObjectDTO]:
        """Fetch testobjects for a specific stage/instance."""
        data: Any = await self._get(
            f"/{domain}/platform/testobjects?stage={stage}&instance={instance}"
        )
        return [TestObjectDTO.model_validate(o) for o in data]

    async def get_testruns(self, domain: str) -> list[TestRunDTO]:
        """Fetch all testruns for a domain."""
        data: Any = await self._get(f"/{domain}/testrun/")
        return [TestRunDTO.model_validate(r) for r in data]

    async def find_specs(
        self, domain: str, body: FindSpecsRequest
    ) -> TestRunDefDTO:
        """Find specifications for a testset."""
        data: Any = await self._post(
            f"/{domain}/specification/find", body.model_dump(mode="json")
        )
        return TestRunDefDTO.model_validate(data)

    async def save_domain_config(self, domain: str, dto: DomainConfigDTO) -> None:
        """Save a domain configuration via PUT /domain-config/{domain}."""
        await self._put(f"/domain-config/{domain}", dto.model_dump(mode="json"))
