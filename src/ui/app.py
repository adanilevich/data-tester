"""UI application factory — registers all NiceGUI routes."""

from .controller import Controller, NiceGuiState
from .data import DataTesterClient
from .pages import domain_home, domain_selection


def register_routes(client: DataTesterClient) -> None:
    """Register all page routes with NiceGUI."""
    state = NiceGuiState()
    controller = Controller(client=client, state=state)

    domain_selection.register(controller)
    domain_home.register(controller)
