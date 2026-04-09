"""Shared status bar component shown at the bottom of every page."""

from nicegui import ui

from src.ui.common import Status
from src.ui.controller import Controller

_DOT_COLOR: dict[Status, str] = {
    Status.LOADED: "bg-teal-400",
    Status.LOADING: "bg-yellow-400",
    Status.ERROR: "bg-red-500",
    Status.UNCLEAR: "bg-slate-600",
}


class StatusBar:

    def __init__(self, controller: Controller, domain: str | None = None):
        self.controller = controller
        self._domain = domain

    def _chip(self, label: str, status: Status) -> None:
        dot = _DOT_COLOR[status]
        with ui.row().classes("items-center").style("gap: 0.75rem;"):
            ui.element("div").classes(f"w-3 h-2 rounded-sm {dot}")
            ui.label(f"{label}: {status.value}").classes(
                "font-mono text-xs text-slate-400 tracking-widest"
            )

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

                # --- Status chips: refresh every 0.5 s ---
                if domain:

                    @ui.refreshable
                    def _chips() -> None:
                        self._chip(
                            "Config",
                            self.controller.get_domain_config_status(domain),
                        )
                        self._chip(
                            "Testsets",
                            self.controller.get_testset_status(domain),
                        )
                        self._chip(
                            "Testobjects",
                            self.controller.get_testobjects_status(domain),
                        )
                        self._chip(
                            "Testruns",
                            self.controller.get_testruns_status(domain),
                        )
                        self._chip(
                            "Specs",
                            self.controller.get_specs_status(domain),
                        )

                    _chips()
                    ui.timer(0.5, _chips.refresh)

        return footer

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
                    "font-mono text-xs text-slate-400 tracking-widest "
                    "p-0 min-w-0 hover:text-teal-400 transition-colors duration-150"
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
                ui.label(domain_text).classes(
                    "font-mono text-xs text-slate-400 tracking-widest"
                )
