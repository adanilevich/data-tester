"""UI application factory — registers all NiceGUI routes."""

from .client import DataTesterClient
from .pages import about, config, domain_selection, testsets, testruns


def register_routes(client: DataTesterClient) -> None:
    """Register all page routes with NiceGUI."""
    domain_selection.register(client)
    testsets.register(client)
    testruns.register(client)
    config.register(client)
    about.register(client)
