"""Shared UI styling constants.

Three buckets — never mix them:
  - CLASSES  →  Tailwind class strings, use with .classes()
  - PROPS    →  Quasar props strings, use with .props()
  - STYLE    →  Raw CSS strings, use with .style()
"""

# ── Tailwind class strings ────────────────────────────────────────────────────

PAGE_CONTENT_COLUMN_CLASSES = "w-full min-h-screen bg-[#0f1117] px-6 py-6"

CARD_SURFACE_CLASSES = "w-full bg-[#161b27] border border-slate-700 rounded-lg p-0"
CARD_SURFACE_PADDED_CLASSES = "w-full bg-[#161b27] border border-slate-700 rounded-lg"
CARD_HEADER_ROW_CLASSES = "w-full items-center px-4 py-2"
CARD_TITLE_GROUP_CLASSES = "items-center flex-1"

CARD_ITEM_TITLE_CLASSES = "font-bold text-white text-sm font-mono"
CARD_ITEM_DATE_CLASSES = "text-slate-500 text-xs font-mono"
CARD_ITEM_META_CLASSES = "text-slate-400 text-xs font-mono"

ICON_BUTTON_SECONDARY_CLASSES = (
    "text-slate-400 hover:text-teal-400 transition-colors duration-150"
)
ICON_BUTTON_PRIMARY_CLASSES = (
    "text-teal-400 hover:text-teal-300 transition-colors duration-150"
)

STATUS_CHIP_TEXT_CLASSES = "font-mono text-xs text-slate-400 tracking-widest"

# ── Quasar props strings ──────────────────────────────────────────────────────

SELECT_INPUT_PROPS = "dark outlined dense color=teal-4"

# ── Raw CSS strings ───────────────────────────────────────────────────────────

DIALOG_SEPARATOR_STYLE = "background: #1e293b; margin: 0.75rem 0;"

TABLE_HEADER_BORDER_STYLE = "border-bottom: 1px solid #1e293b;"
TABLE_ROW_BORDER_STYLE = "border-bottom: 1px solid #0f172a;"

MATRIX_CELL_NA_STYLE = "color: #475569; font-size: 0.7rem;"
