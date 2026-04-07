"""Generate SVG badges for the data-tester project."""

from __future__ import annotations

import base64
import json
import math
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

BADGES_DIR = Path(__file__).parent

# ── Logo SVG constants ───────────────────────────────────────

# Astral brand logo (used for ruff and uv badges)
_ASTRAL_LOGO_SVG = (
    '<svg width="510" height="622" viewBox="0 0 510 622" fill="none"'
    ' xmlns="http://www.w3.org/2000/svg">'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M206.701 0C200.964 0 196.314'
    " 4.64131 196.314 10.3667V41.4667C196.314 47.192 191.663 51.8333 185.927"
    " 51.8333H156.843C151.107 51.8333 146.456 56.4746 146.456 62.2V145.133C146.456"
    " 150.859 141.806 155.5 136.069 155.5H106.986C101.249 155.5 96.5988 160.141"
    " 96.5988 165.867V222.883C96.5988 228.609 91.9484 233.25 86.2118"
    " 233.25H57.1283C51.3917 233.25 46.7413 237.891 46.7413 243.617V300.633C46.7413"
    " 306.359 42.0909 311 36.3544 311H10.387C4.6504 311 0 315.641 0"
    " 321.367V352.467C0 358.192 4.6504 362.833 10.387 362.833H145.418C151.154"
    " 362.833 155.804 367.475 155.804 373.2V430.217C155.804 435.942 151.154 440.583"
    " 145.418 440.583H116.334C110.597 440.583 105.947 445.225 105.947"
    " 450.95V507.967C105.947 513.692 101.297 518.333 95.5601 518.333H66.4766C60.74"
    " 518.333 56.0896 522.975 56.0896 528.7V611.633C56.0896 617.359 60.74 622"
    " 66.4766 622H149.572C155.309 622 159.959 617.359 159.959"
    " 611.633V570.167H201.507C207.244"
    " 570.167 211.894 565.525 211.894 559.8V528.7C211.894 522.975 216.544 518.333"
    " 222.281 518.333H251.365C257.101 518.333 261.752 513.692 261.752"
    " 507.967V476.867C261.752 471.141 266.402 466.5 272.138 466.5H301.222C306.959"
    " 466.5 311.609 461.859 311.609 456.133V425.033C311.609 419.308 316.259 414.667"
    " 321.996 414.667H351.079C356.816 414.667 361.466 410.025 361.466"
    " 404.3V373.2C361.466 367.475 366.117 362.833 371.853 362.833H400.937C406.673"
    " 362.833 411.324 358.192 411.324 352.467V321.367C411.324 315.641 415.974 311"
    " 421.711 311H450.794C456.531 311 461.181 306.359 461.181 300.633V217.7C461.181"
    " 211.975 456.531 207.333 450.794 207.333H420.672C414.936 207.333 410.285"
    " 202.692 410.285 196.967V165.867C410.285 160.141 414.936 155.5 420.672"
    " 155.5H449.756C455.492 155.5 460.143 150.859 460.143 145.133V114.033C460.143"
    " 108.308 464.793 103.667 470.53 103.667H499.613C505.35 103.667 510 99.0253 510"
    " 93.3V10.3667C510 4.64132 505.35 0 499.613 0H206.701ZM168.269 440.583C162.532"
    " 440.583 157.882 445.225 157.882 450.95V507.967C157.882 513.692 153.231 518.333"
    " 147.495 518.333H118.411C112.675 518.333 108.024 522.975 108.024"
    " 528.7V559.8C108.024 565.525 112.675 570.167 118.411 570.167H159.959V528.7C159.959"
    " 522.975 164.61 518.333 170.346 518.333H199.43C205.166 518.333 209.817 513.692"
    " 209.817 507.967V476.867C209.817 471.141 214.467 466.5 220.204"
    " 466.5H249.287C255.024 466.5 259.674 461.859 259.674 456.133V425.033C259.674"
    " 419.308 264.325 414.667 270.061 414.667H299.145C304.881 414.667 309.532"
    " 410.025 309.532 404.3V373.2C309.532 367.475 314.182 362.833 319.919"
    " 362.833H349.002C354.739 362.833 359.389 358.192 359.389 352.467V321.367C359.389"
    " 315.641 364.039 311 369.776 311H398.859C404.596 311 409.246 306.359 409.246"
    " 300.633V269.533C409.246 263.808 404.596 259.167 398.859 259.167H318.88C313.143"
    " 259.167 308.493 254.525 308.493 248.8V217.7C308.493 211.975 313.143 207.333"
    " 318.88 207.333H347.963C353.7 207.333 358.35 202.692 358.35 196.967V165.867C358.35"
    " 160.141 363.001 155.5 368.737 155.5H397.821C403.557 155.5 408.208 150.859"
    " 408.208 145.133V114.033C408.208 108.308 412.858 103.667 418.595"
    " 103.667H447.678C453.415 103.667 458.065 99.0253 458.065 93.3V62.2C458.065"
    " 56.4746 453.415 51.8333 447.678 51.8333H208.778C203.041 51.8333 198.391"
    " 56.4746 198.391 62.2V145.133C198.391 150.859 193.741 155.5 188.004"
    " 155.5H158.921C153.184 155.5 148.534 160.141 148.534 165.867V222.883C148.534"
    " 228.609 143.883 233.25 138.147 233.25H109.063C103.327 233.25 98.6762 237.891"
    " 98.6762 243.617V300.633C98.6762 306.359 103.327 311 109.063 311H197.352C203.089"
    " 311 207.739 315.641 207.739 321.367V430.217C207.739 435.942 203.089 440.583"
    ' 197.352 440.583H168.269Z" fill="#D7FF64"/></svg>'
)

# ty brand logo (T-cross shape in teal)
_TY_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48">'
    '<path d="M48 7.7H27.8V0h-24v7.7H0v18.2h3.8v14.3c0 4.3 3.5 7.8 7.8 7.8H48V29.8H27.8'
    'v-3.9h12.4c4.3 0 7.8-3.5 7.8-7.8V7.7Z" fill="#46ebe1"/></svg>'
)


# ── Badge data ───────────────────────────────────────────────


@dataclass
class BadgeData:
    label: str
    value: str
    color: str
    filename: str
    logo_svg: str | None = None


BadgeProvider = Callable[[], BadgeData]


# ── Rendering ────────────────────────────────────────────────


def render_badge_svg(badge: BadgeData) -> str:
    """Render a shields.io flat-style SVG badge, with optional logo."""
    char_w, pad = 6.8, 10
    vw = int(math.ceil(len(badge.value) * char_w) + pad * 2)

    if badge.logo_svg is not None:
        logo_b64 = base64.b64encode(badge.logo_svg.encode()).decode()
        lw = 24
        tw = lw + vw
        vx = lw + vw / 2
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="20">'
            f'<linearGradient id="s" x2="0" y2="100%">'
            f'<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
            f'<stop offset="1" stop-opacity=".1"/>'
            f"</linearGradient>"
            f'<clipPath id="r">'
            f'<rect width="{tw}" height="20" rx="3" fill="#fff"/>'
            f"</clipPath>"
            f'<g clip-path="url(#r)">'
            f'<rect width="{lw}" height="20" fill="#555"/>'
            f'<rect x="{lw}" width="{vw}" height="20" fill="{badge.color}"/>'
            f'<rect width="{tw}" height="20" fill="url(#s)"/>'
            f"</g>"
            f'<image x="5" y="3" width="14" height="14"'
            f' href="data:image/svg+xml;base64,{logo_b64}"/>'
            f'<g fill="#fff" text-anchor="middle"'
            f' font-family="Verdana,Geneva,DejaVu Sans,sans-serif"'
            f' font-size="11">'
            f'<text x="{vx}" y="15" fill="#010101"'
            f' fill-opacity=".3">{badge.value}</text>'
            f'<text x="{vx}" y="14">{badge.value}</text>'
            f"</g></svg>"
        )

    lw = int(math.ceil(len(badge.label) * char_w) + pad * 2)
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
    return BadgeData("License", "MIT", "#97ca00", "licence.svg")


def ruff_badge() -> BadgeData:
    return BadgeData("", "Ruff", "#261230", "ruff.svg", logo_svg=_ASTRAL_LOGO_SVG)


def uv_badge() -> BadgeData:
    return BadgeData("", "uv", "#261230", "uv.svg", logo_svg=_ASTRAL_LOGO_SVG)


def ty_badge() -> BadgeData:
    return BadgeData("", "ty", "#261230", "ty.svg", logo_svg=_TY_LOGO_SVG)


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
        label = badge.label or f"[logo] {badge.filename}"
        print(f"  {label}: {badge.value} -> {path}")


if __name__ == "__main__":
    main()
