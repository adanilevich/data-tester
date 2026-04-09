"""Shared page layout context manager."""

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from nicegui import ui

from src.ui.styles import PAGE_CONTENT_COLUMN_CLASSES

if TYPE_CHECKING:
    from src.ui.controller import Controller


@contextmanager
def page_layout(
    controller: "Controller",
    domain: str | None,
    refresh_interval: float = 1.0,
) -> Generator[None, None, None]:
    """Context manager that renders NavBar + StatusBar and opens the content column.

    Usage::

        with page_layout(controller, domain, refresh_interval):
            ui.label("Page content")
    """
    from src.ui.components.navbar import NavBar
    from src.ui.components.statusbar import StatusBar

    NavBar(controller).render()
    StatusBar(controller, domain, refresh_interval=refresh_interval).render()
    with ui.column().classes(PAGE_CONTENT_COLUMN_CLASSES).style("row-gap: 1rem;"):
        yield
