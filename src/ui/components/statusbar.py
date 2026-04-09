"""Shared status bar component shown at the bottom of every page."""

import time
from typing import Any

from nicegui import ui

from src.ui.common import Status, format_elapsed
from src.ui.controller import Controller
from src.ui.styles import ICON_BUTTON_SECONDARY_CLASSES, STATUS_CHIP_TEXT_CLASSES

_client_chips_timers: dict[str, Any] = {}

_DOT_COLOR: dict[Status, str] = {
    Status.LOADED: "bg-teal-400",
    Status.LOADING: "bg-yellow-400",
    Status.ERROR: "bg-red-500",
    Status.UNCLEAR: "bg-slate-600",
}

_CHIPS_DATA: list[tuple[str, str]] = [
    ("Config", "domain_configs"),
    ("Testsets", "testsets"),
    ("Testobjects", "testobjects"),
    ("Testruns", "testruns"),
    ("Specs", "specs"),
]


class StatusBar:

    def __init__(
        self,
        controller: Controller,
        domain: str | None = None,
        refresh_interval: float = 1.0,
    ):
        self.controller = controller
        self._domain = domain
        self._refresh_interval = refresh_interval

    def _chip(self, label: str, status: Status, elapsed: str | None = None) -> None:
        dot = _DOT_COLOR[status]
        text = f"{label}: {status.value}"
        if elapsed and status == Status.LOADED:
            text = f"{label}: {status.value} ({elapsed})"
        with ui.row().classes("items-center").style("gap: 0.75rem;"):
            ui.element("div").classes(f"w-3 h-2 rounded-sm {dot}")
            ui.label(text).classes(STATUS_CHIP_TEXT_CLASSES)

    def render(self) -> ui.footer:
        domain = self._domain or self.controller.domain

        with ui.footer().classes(
            "flex items-center px-6 py-2 "
            "bg-[#0b0d13] border-t border-slate-800 h-10"
        ) as footer:
            with ui.row().classes("items-center").style("gap: 2.5rem;"):
                # --- Domain selector: refreshes until domains are loaded ---
                @ui.refreshable
                def _domain_selector() -> None:
                    self._render_domain_selector(domain)

                _domain_selector()

                def _maybe_refresh_selector() -> None:
                    _domain_selector.refresh()
                    if self.controller.domains:
                        _selector_timer.cancel()

                _selector_timer = ui.timer(0.5, _maybe_refresh_selector)

                # --- Status chips: one timer per client connection ---
                if domain:

                    @ui.refreshable
                    def _chips() -> None:
                        for label, data_type in _CHIPS_DATA:
                            status = self._get_status(data_type, domain)
                            last = self.controller.state.get_last_loaded(
                                domain, data_type
                            )
                            elapsed = (
                                format_elapsed(time.time() - last)
                                if last is not None
                                else None
                            )
                            self._chip(label, status, elapsed)

                    _chips()

                    # Per-client timer: cancel the previous one for this client (if
                    # navigating between pages), then create a fresh timer pointing
                    # at the current _chips refreshable.
                    client_id = str(ui.context.client.id)
                    if client_id in _client_chips_timers:
                        _client_chips_timers[client_id].cancel()
                    chips_timer = ui.timer(self._refresh_interval, _chips.refresh)
                    _client_chips_timers[client_id] = chips_timer
                    _cid = client_id
                    ui.context.client.on_disconnect(
                        lambda: _client_chips_timers.pop(_cid, None)
                    )

        return footer

    def _get_status(self, data_type: str, domain: str) -> Status:
        getter_map = {
            "domain_configs": self.controller.get_domain_config_status,
            "testsets": self.controller.get_testset_status,
            "testobjects": self.controller.get_testobjects_status,
            "testruns": self.controller.get_testruns_status,
            "specs": self.controller.get_specs_status,
        }
        getter = getter_map.get(data_type)
        if getter is None:
            return Status.UNCLEAR
        return getter(domain)

    def _render_domain_selector(self, domain: str | None) -> None:
        """Render the domain indicator/selector. Called once — never refreshed."""
        dot = "bg-teal-400" if domain else "bg-slate-600"
        domain_text = (
            f"Domain: {domain.capitalize()}" if domain else "No domain selected"
        )

        def _navigate_to_domain(d: str) -> None:
            ui.navigate.to(f"/{d}/testsets")

        with ui.row().classes("items-center").style("gap: 0.75rem;"):
            ui.element("div").classes(f"w-3 h-2 rounded-sm {dot}")
            domains = self.controller.domains
            if domain and len(domains) > 1:
                with ui.button(domain_text).props("flat dense no-caps").classes(
                    f"{STATUS_CHIP_TEXT_CLASSES} p-0 min-w-0 "
                    + ICON_BUTTON_SECONDARY_CLASSES
                ):
                    with ui.menu().classes(
                        "bg-[#161b27] border border-slate-700"
                    ):
                        for d in sorted(domains):
                            is_current = d == domain
                            ui.menu_item(
                                d.capitalize(),
                                on_click=lambda _, d=d: _navigate_to_domain(d),
                            ).classes(
                                "font-mono text-xs "
                                + (
                                    "text-teal-400 font-semibold"
                                    if is_current
                                    else "text-slate-300"
                                )
                            )
            else:
                ui.label(domain_text).classes(STATUS_CHIP_TEXT_CLASSES)
