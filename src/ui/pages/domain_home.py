"""Domain home page — route: /{domain}/"""

from nicegui import background_tasks, ui

from src.ui.components import NavBar, StatusBar
from src.ui.controller import Controller


def register(controller: Controller) -> None:
    """Register the domain home page route."""

    @ui.page("/{domain}/")
    async def domain_home(domain: str) -> None:
        _ = NavBar(controller).render()
        _ = StatusBar(controller, domain).render()
        background_tasks.create(controller.load_backend_data(domain))

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
