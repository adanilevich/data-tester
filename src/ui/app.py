"""UI application factory — registers all NiceGUI routes."""

from .client import DataTesterClient
from .config import UIConfig
from .controller import Controller, NiceGuiState
from .pages import about, config, domain_selection, specs, testsets, testruns


def register_routes(client: DataTesterClient, ui_config: UIConfig) -> None:
    """Register all page routes with NiceGUI."""

    def make_controller() -> Controller:
        return Controller(client=client, state=NiceGuiState(), config=ui_config)

    domain_selection.register(make_controller)
    testsets.register(make_controller)
    testruns.register(make_controller)
    specs.register(make_controller)
    config.register(make_controller)
    about.register(make_controller)
