"""NiceGUI frontend entry point for the Data Tester application.

===========================================================================
HOW TO RUN LOCALLY
===========================================================================

Prerequisites
-------------
1. The FastAPI backend must already be running.

Starting the UI
---------------
From the project root run::

    uv run python -m src.ui.main_ui

Configuration via environment variables (all optional — shown with defaults)::

    DATATESTER_UI_BACKEND_URL=http://localhost:8000   # backend base URL
    DATATESTER_UI_PORT=3000                            # UI server port
    DATATESTER_UI_HOST=0.0.0.0                        # UI bind address
    DATATESTER_UI_STORAGE_SECRET=dev-secret-change-in-production
    DATATESTER_DATA_PLATFORM=DUMMY   # set DEMO to reset storage on startup

Open your browser at http://localhost:3000 (or whatever port you configured).

===========================================================================
"""

from nicegui import app, ui

from .app import register_routes
from .config import UIConfig
from .client import DataTesterClient


def create_ui(config: UIConfig | None = None) -> None:
    """Register all UI routes and start the NiceGUI server.

    Parameters
    ----------
    config:
        Optional pre-built ``UIConfig``.  When *None* the config is loaded
        from environment variables automatically.
    """
    cfg = config or UIConfig()
    client = DataTesterClient(base_url=cfg.DATATESTER_UI_BACKEND_URL)

    register_routes(client)

    if cfg.DATATESTER_DATA_PLATFORM == "DEMO":
        app.on_startup(lambda: app.storage.general.clear())
        app.on_connect(lambda: app.storage.user.clear())

    ui.run(
        host=cfg.DATATESTER_UI_HOST,
        port=cfg.DATATESTER_UI_PORT,
        title="Data Tester",
        dark=True,
        storage_secret=cfg.DATATESTER_UI_STORAGE_SECRET,
        reload=False,
        show=False,
        favicon=(
            "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
            "viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧪</text></svg>"
        ),
    )


if __name__ == "__main__":
    create_ui()
