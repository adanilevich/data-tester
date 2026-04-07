"""Generate SVG badges for the data-tester project."""

from __future__ import annotations

import json
import math
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

BADGES_DIR = Path(__file__).parent


@dataclass
class BadgeData:
    label: str
    value: str
    color: str
    filename: str


BadgeProvider = Callable[[], BadgeData]


def render_badge_svg(badge: BadgeData) -> str:
    """Render a shields.io flat-style SVG badge."""
    char_w, pad = 6.8, 10
    lw = int(math.ceil(len(badge.label) * char_w) + pad * 2)
    vw = int(math.ceil(len(badge.value) * char_w) + pad * 2)
    tw = lw + vw
    lx, vx = lw / 2, lw + vw / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{tw}" height="20">'
        f'<linearGradient id="s" x2="0" y2="100%">'
        f'<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        f'<stop offset="1" stop-opacity=".1"/>'
        f"</linearGradient>"
        f'<clipPath id="r">'
        f'<rect width="{tw}" height="20" rx="3" fill="#fff"/>'
        f"</clipPath>"
        f'<g clip-path="url(#r)">'
        f'<rect width="{lw}" height="20" fill="#555"/>'
        f'<rect x="{lw}" width="{vw}" height="20"'
        f' fill="{badge.color}"/>'
        f'<rect width="{tw}" height="20" fill="url(#s)"/>'
        f"</g>"
        f'<g fill="#fff" text-anchor="middle"'
        f' font-family="Verdana,Geneva,DejaVu Sans,sans-serif"'
        f' font-size="11">'
        f'<text x="{lx}" y="15" fill="#010101"'
        f' fill-opacity=".3">{badge.label}</text>'
        f'<text x="{lx}" y="14">{badge.label}</text>'
        f'<text x="{vx}" y="15" fill="#010101"'
        f' fill-opacity=".3">{badge.value}</text>'
        f'<text x="{vx}" y="14">{badge.value}</text>'
        f"</g></svg>"
    )


# ── Badge providers ─────────────────────────────────────────


def _get_coverage_total() -> tuple[int, bool]:
    """Run coverage report and return (pct, success)."""
    result = subprocess.run(
        ["coverage", "report", "--format=total"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0, False
    try:
        return int(result.stdout.strip()), True
    except ValueError:
        return 0, False


def _coverage_color(pct: int) -> str:
    if pct >= 90:
        return "#97ca00"
    if pct >= 75:
        return "#dfb317"
    if pct >= 50:
        return "#fe7d37"
    return "#e05d44"


def tests_badge() -> BadgeData:
    """Show passing/failing based on whether a valid coverage report exists."""
    _, success = _get_coverage_total()
    if success:
        return BadgeData("tests", "passing", "#97ca00", "tests.svg")
    return BadgeData("tests", "failing", "#e05d44", "tests.svg")


def coverage_badge() -> BadgeData:
    """Show total coverage percentage from last coverage run."""
    pct, success = _get_coverage_total()
    if not success:
        return BadgeData("coverage", "unknown", "#9f9f9f", "coverage.svg")
    return BadgeData("coverage", f"{pct}%", _coverage_color(pct), "coverage.svg")


def python_loc_badge() -> BadgeData:
    """Count Python lines of code in src/ using pygount."""
    result = subprocess.run(
        ["pygount", "src", "--suffix=py", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    loc = 0
    for lang in data.get("languages", []):
        if lang.get("language") == "Python":
            loc = lang.get("codeCount", 0)
            break
    return BadgeData("python LOC", str(loc), "#3572a5", "loc.svg")


def licence_badge() -> BadgeData:
    return BadgeData("licence", "MIT", "#97ca00", "licence.svg")


def ruff_badge() -> BadgeData:
    return BadgeData("linter", "ruff", "#d7ff64", "ruff.svg")


def uv_badge() -> BadgeData:
    return BadgeData("pkg", "uv", "#de5fe9", "uv.svg")


def ty_badge() -> BadgeData:
    return BadgeData("types", "ty", "#007ec6", "ty.svg")


BADGE_PROVIDERS: list[BadgeProvider] = [
    tests_badge,
    coverage_badge,
    python_loc_badge,
    licence_badge,
    ruff_badge,
    uv_badge,
    ty_badge,
]


# ── Main ────────────────────────────────────────────────────


def main() -> None:
    BADGES_DIR.mkdir(parents=True, exist_ok=True)
    for provider in BADGE_PROVIDERS:
        badge = provider()
        svg = render_badge_svg(badge)
        path = BADGES_DIR / badge.filename
        path.write_text(svg, encoding="utf-8")
        print(f"  {badge.label}: {badge.value} -> {path}")


if __name__ == "__main__":
    main()
