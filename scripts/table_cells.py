"""table_cells.py — shared Markdown-table cell logic (CG-21, 2026-11-02).

Single source of truth for how a table ROW is split into cells, used by
scripts/build_round5_report_pdfs.py (builder) and by the unit tests, so the
tested logic and the shipped logic cannot drift apart.

Rules (established by the D5/D6 incidents of the n25 round):
  * Cells are separated by UNESCAPED pipes only: re.split(r"(?<!\\)\\|", ...).
    An escaped pipe '\\|' inside a cell is literal content (code spans that
    quote Markdown tables, e.g. the CG-11 mutation-proof row). The old
    split-on-everything cut such rows mid-cell and silently widened tables.
  * A table's width is the HEADER row's width. Every other data row must
    match it. Ragged tables were previously padded to max(len(row)) — that
    padding is what let D5 (a 5-cell row missing its closing pipe) render as
    a leak and D6 (escaped pipes cut as delimiters, 10 cells) render as a
    garbled 10-column table. Raggedness is now a loud error.
"""
from __future__ import annotations

import re

_SPLIT = re.compile(r"(?<!\\)\|")


def split_cells(raw: str) -> list[str]:
    """Split one Markdown table row into stripped cell texts.

    Escaped pipes ('\\|') stay inside their cell and appear as literal '|'
    in the returned text.
    """
    return [c.strip().replace("\\|", "|") for c in _SPLIT.split(raw.strip().strip("|"))]


def is_separator_row(cells: list[str]) -> bool:
    return all(set(c) <= set("-: ") and c for c in cells)


def validate_rows(rows: list[list[str]], label: str = "") -> int:
    """Assert every row has the header's cell count; return the width.

    Raises ValueError (message contains 'TABLE WIDTH MISMATCH') on any ragged
    row. This is the CG-21 gate: both known instances of the pipe-handling
    defect class (missing trailing pipe -> short row; escaped pipes treated
    as delimiters -> wide row) fail here loudly instead of rendering wrong.
    """
    if not rows:
        return 0
    ncol = len(rows[0])
    bad = [(i + 1, len(r)) for i, r in enumerate(rows) if len(r) != ncol]
    if bad:
        detail = "; ".join(f"row {i}: {w} cells vs header {ncol}" for i, w in bad[:4])
        raise ValueError(f"TABLE WIDTH MISMATCH (CG-21){(' in ' + label) if label else ''}: {detail}")
    return ncol
