"""UI-specific configuration loaded from environment variables."""

import warnings

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

_DEFAULT_SECRET = (
    "dev-secret-change-in-productiondev-secret-change-in-production"
    + "dev-secret-change-in-productiondev-secret-change-in-production"
)


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
        default=_DEFAULT_SECRET,
        description=(
            "Secret key used to sign browser session cookies. "
            "Must be changed for any non-local deployment. Minimum 32 characters."
        ),
    )
    DATATESTER_DATA_PLATFORM: str = Field(
        default="DUMMY",
        description=(
            "Target data platform (DUMMY, DEMO, …). "
            "When DEMO, the UI clears all ui cache on startup and on each new connection."
        ),
    )
    DATATESTER_UI_TTL_DOMAIN_CONFIGS: int = Field(
        default=60,
        description="Seconds before domain config cache is considered stale.",
    )
    DATATESTER_UI_TTL_TESTSETS: int = Field(
        default=60,
        description="Seconds before testsets cache is considered stale.",
    )
    DATATESTER_UI_TTL_TESTOBJECTS: int = Field(
        default=60,
        description="Seconds before testobjects cache is considered stale.",
    )
    DATATESTER_UI_TTL_TESTRUNS: int = Field(
        default=60,
        description="Seconds before testruns cache is considered stale.",
    )
    DATATESTER_UI_TTL_SPECS: int = Field(
        default=10,
        description="Seconds before specs cache is considered stale.",
    )
    DATATESTER_UI_STATUS_REFRESH_INTERVAL: float = Field(
        default=1.0,
        description="Interval in seconds for the status bar chips refresh timer.",
    )

    @field_validator("DATATESTER_UI_STORAGE_SECRET")
    @classmethod
    def validate_storage_secret(cls, v: str) -> str:
        if v == _DEFAULT_SECRET:
            warnings.warn(
                "DATATESTER_UI_STORAGE_SECRET is set to the insecure default. "
                "Set a strong random value before any non-local deployment.",
                stacklevel=2,
            )
        if len(v) < 32:
            raise ValueError(
                "DATATESTER_UI_STORAGE_SECRET must be at least 32 characters."
            )
        return v
