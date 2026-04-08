"""Domain home page — route: /{domain}/"""

from nicegui import ui

from src.ui.components import NavBar, StatusBar
from src.ui.controller import Controller


def register(controller: Controller) -> None:
    """Register the domain home page route."""

    @ui.page("/{domain}/")
    async def domain_home(domain: str) -> None:
        _ = NavBar(controller).render()
        _ = StatusBar(controller).render()

        # load_backend_data refreshes domain_configs first, so domain setter
        # validation is safe to call after it.
        await controller.load_backend_data(domain)
        if controller.domain != domain:
            controller.domain = domain

        with ui.column().classes(
            "flex-1 flex items-center justify-center min-h-screen "
            "bg-[#0f1117] w-full"
        ):
            ui.label(f"/{domain}/").classes(
                "text-slate-600 font-mono text-xs tracking-widest"
            )
            ui.label("Select a section from the navbar to get started.").classes(
                "text-slate-500 text-sm mt-2"
            )
