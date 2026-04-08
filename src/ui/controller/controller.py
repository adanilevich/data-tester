from typing import List

from src.client_interface import TestSetDTO
from src.ui.data import BackendError, DataTesterClient
from .state import State
from src.ui.common import Status


class Controller:
    """
    UI Controller and state machine.
    All state access and modification MUST go through Controller.
    Controller exposes properties to get and set and modifies State.
    """

    def __init__(self, client: DataTesterClient, state: State) -> None:
        self._client: DataTesterClient = client
        self.state: State = state

    @property
    def domain(self) -> str | None:
        return self.state.domain

    @domain.setter
    def domain(self, val: str):
        self.state.domain = val

    @property
    def domains(self) -> List[str]:
        return self.state.domains

    def testsets(self, domain: str) -> List[TestSetDTO]:
        return self.state.testsets.get(domain, [])

    def get_testset_status(self, domain: str) -> Status:
        return self.state.testsets_status.get(domain, Status.UNCLEAR)

    async def load_domains(self) -> str | None:
        """
        Fetch domain configs from backend, populate state.
        Returns error_message, None on success.
        """
        try:
            configs = await self._client.get_domain_configs()
            self.state.domain_configs = configs
            self.state.domains = list(configs.keys())
            return None
        except BackendError as exc:
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            return f"Could not reach backend: {exc}"

    async def load_testsets(self, domain: str) -> str | None:
        """
        Fetch testsets from backend, populate state. Returns error_message or None
        """
        self.state.set_testsets_status(domain, Status.LOADING)
        try:
            testsets = await self._client.get_testsets(domain)
            self.state.set_testsets(domain, testsets)
            self.state.set_testsets_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_testsets_status(domain, Status.ERROR)
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            self.state.set_testsets_status(domain, Status.ERROR)
            return f"Could not reach backend: {exc}"

