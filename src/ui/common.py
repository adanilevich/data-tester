from enum import Enum

from nicegui import ui

from src.dtos import Result, TestType
from src.dtos import Status as RunStatus


class Status(Enum):
    LOADING = "LOADING"
    LOADED = "LOADED"
    ERROR = "ERROR"
    UNCLEAR = "UNCLEAR"


IGNORED_TESTTYPES: frozenset[TestType] = frozenset(
    {
        TestType.ABSTRACT,
        TestType.UNKNOWN,
        TestType.DUMMY_OK,
        TestType.DUMMY_NOK,
        TestType.DUMMY_EXCEPTION,
    }
)

_STATUS_BADGE_CLASSES: dict[RunStatus, tuple[str, str]] = {
    RunStatus.FINISHED: ("bg-teal-900", "text-teal-400"),
    RunStatus.ERROR: ("bg-red-900", "text-red-400"),
    RunStatus.EXECUTING: ("bg-yellow-900", "text-yellow-400"),
    RunStatus.PRECONDITIONS: ("bg-yellow-900", "text-yellow-400"),
    RunStatus.INITIATED: ("bg-slate-700", "text-slate-400"),
    RunStatus.ABORTED: ("bg-orange-900", "text-orange-400"),
    RunStatus.NOT_STARTED: ("bg-slate-800", "text-slate-600"),
}

_RESULT_COLOR: dict[Result, str] = {
    Result.OK: "#2dd4bf",
    Result.NOK: "#f87171",
    Result.NA: "#fbbf24",
}

_RESULT_ICON: dict[Result, str] = {
    Result.OK: "check_circle",
    Result.NOK: "cancel",
    Result.NA: "help",
}


def format_elapsed(seconds: float) -> str:
    """Format elapsed seconds as a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)} s ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)} min ago"
    else:
        return f"{int(seconds // 3600)} h ago"


def notify_error(msg: str) -> None:
    ui.notify(msg, type="negative", close_button=True)


def notify_success(msg: str) -> None:
    ui.notify(msg, type="positive")


def render_status_badge(status: RunStatus) -> None:
    """Render a small inline status badge chip."""
    bg, fg = _STATUS_BADGE_CLASSES.get(status, ("bg-slate-700", "text-slate-400"))
    with ui.element("div").classes(f"{bg} {fg} text-xs font-mono px-2 py-0.5 rounded"):
        ui.label(status.value)


def render_result_badge(result: Result) -> None:
    """Render a small inline result badge chip."""
    color = _RESULT_COLOR.get(result, "#94a3b8")
    with ui.element("div").style(
        f"background: #1e293b; color: {color}; "
        "font-size: 0.7rem; font-family: monospace; "
        "padding: 0.125rem 0.5rem; border-radius: 0.25rem;"
    ):
        ui.label(result.value)
