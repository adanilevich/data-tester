"""UI-specific configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings


class UIConfig(BaseSettings):
    """Configuration for the NiceGUI frontend process.

    All values can be overridden via environment variables using the
    ``DATATESTER_UI_`` prefix, e.g.::

        DATATESTER_UI_BACKEND_URL=http://backend:8000
        DATATESTER_UI_PORT=3000
    """

    DATATESTER_UI_BACKEND_URL: str = Field(
        default="http://localhost:8000",
        description="Base URL of the Data Tester FastAPI backend.",
    )
    DATATESTER_UI_PORT: int = Field(
        default=3000,
        description="Port the NiceGUI server listens on.",
    )
    DATATESTER_UI_HOST: str = Field(
        default="0.0.0.0",
        description="Host the NiceGUI server binds to.",
    )
    DATATESTER_UI_STORAGE_SECRET: str = Field(
        default="dev-secret-change-in-production",
        description=(
            "Secret key used to sign browser session cookies. "
            "Must be changed for any non-local deployment."
        ),
    )
