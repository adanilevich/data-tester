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
        with ui.row().classes("items-center gap-3"):
            ui.element("div").classes(f"w-3 h-2 rounded-sm {dot}")
            ui.label(f"{label}: {status.value}").classes(
                "font-mono text-xs text-slate-400 tracking-widest"
            )

    def render(self) -> ui.footer:
        with ui.footer().classes(
            "flex items-center px-6 py-2 "
            "bg-[#0b0d13] border-t border-slate-800 h-10"
        ) as footer:

            @ui.refreshable
            def _content() -> None:
                domain = self._domain or self.controller.domain
                dot = "bg-teal-400" if domain else "bg-slate-600"
                domain_text = (
                    f"Domain: {domain.capitalize()}" if domain else "No domain selected"
                )
                with ui.row().classes("items-center gap-10"):
                    with ui.row().classes("items-center gap-3"):
                        ui.element("div").classes(f"w-3 h-2 rounded-sm {dot}")
                        ui.label(domain_text).classes(
                            "font-mono text-xs text-slate-400 tracking-widest"
                        )
                    if domain:
                        self._chip(
                            "Config", self.controller.get_domain_config_status(domain)
                        )
                        self._chip(
                            "Testsets", self.controller.get_testset_status(domain)
                        )
                        self._chip(
                            "Testobjects", self.controller.get_testobjects_status(domain)
                        )
                        self._chip(
                            "Testruns", self.controller.get_testruns_status(domain)
                        )
                        self._chip(
                            "Specs", self.controller.get_specs_status(domain)
                        )

            _content()

            if self._domain:
                ui.timer(0.5, _content.refresh)

        return footer
