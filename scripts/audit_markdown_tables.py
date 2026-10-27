#!/usr/bin/env python3
"""
audit_markdown_tables.py — verify that every markdown table in a document
actually renders AS A TABLE.

WHY THIS EXISTS
Six tables in PAPER_V1_DRAFT.md had their header row glued to the end of the
preceding prose line. CommonMark requires a header row IMMEDIATELY followed by
a separator row; when the header is mid-line the table never forms, and the
whole block renders as ordinary paragraph text with pipes in it. The content
was not lost, but a reader sees a wall of `| a | b |` instead of a table, and
the table's own column structure is lost to the reader.

No existing layer caught this. audit_doc_anchors.py resolves SECTION
references; audit_claims.py checks numeric claims; audit_units.py checks
units. None of them parse table structure, so the defect survived every gate
run and shipped in the paper.

WHAT IT CHECKS
  A. Every separator row has a real table row immediately above it
     (a header row must start the line with `|`).
  B. Every data row under a separator has the same cell count as the
     separator row.
  C. The document's rendered table count equals its separator-row count
     (i.e. every separator actually produced a table, and no table is
     produced twice or lost).
  D. No table is split by a blank line or prose in the middle of its body
     (a table body interrupted mid-way renders as two separate tables).

The check is PARSER-BASED, not regex-based: it uses markdown_it's CommonMark
parser with the table extension enabled and compares what the parser actually
produced against the source's intent. A regex cannot tell whether a table
formed.

WHAT IT DOES NOT DO
  - It does not judge the CONTENT of a cell (that is audit_claims.py).
  - It does not check units (that is audit_units.py).
  - It does not require a table to exist. A document with zero tables passes.

Usage:
    python scripts/audit_markdown_tables.py [doc.md ...]

With no arguments it audits the paper, the report, and the companion
(the same document set audit_doc_anchors.py covers).

Exit: 0 = all documents' tables are well-formed; 1 = at least one defect.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DEFAULT_DOCS = [
    REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md",
    REPO / "docs" / "dual_review_5loop" / "SIDM_ROUND5_CONSOLIDATED_FIXES_v1.11_2026-10-26.md",
    REPO / "docs" / "dual_review_5loop" / "SIDM_ROUND5_CHANGED_CODE_v1.9_2026-10-26.md",
]


def _is_separator(line: str) -> bool:
    """A markdown separator row: only | - : and spaces, at least 2 pipes."""
    s = line.strip()
    return bool(s) and set(s) <= set("|-: ") and s.count("|") >= 2


def _n_delimiters(line: str) -> int:
    """Count UNESCAPED pipes in a row.

    A pipe inside a cell is written `\\|` (e.g. `| halos with \\|sigma_HL\\| < 0.05 |`).
    Counting every `|` treats the escaped pair as cell delimiters and reports a
    cell-count mismatch on a perfectly good row. A pipe is a delimiter only
    when it is preceded by an EVEN number of backslashes (`\\\\|` = literal
    backslash then a real delimiter).
    """
    n = 0
    i = 0
    while i < len(line):
        if line[i] == "|":
            # count the run of backslashes immediately before this pipe
            k = i - 1
            bs = 0
            while k >= 0 and line[k] == "\\":
                bs += 1
                k -= 1
            if bs % 2 == 0:
                n += 1
        i += 1
    return n


def _cell_count(line: str) -> int:
    """Number of cells in a table row (unescaped pipes minus 1)."""
    return _n_delimiters(line) - 1


def _parser():
    """markdown_it with the table extension. Returns None if unavailable."""
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        return None
    return MarkdownIt("commonmark").enable("table")


_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def _code_line_flags(lines):
    """Return a list[bool]: True for each line that sits INSIDE a fenced code
    block (including the fence lines themselves).

    This matters because the companion report embeds unified DIFFS of the
    paper. A diff of a table contains lines that look exactly like table
    rows and separator rows, so a naive scan reports the diff's own content
    as malformed tables. Those lines are code, not document structure, and
    the markdown parser never sees them as tables either.
    """
    flags = [False] * len(lines)
    fence = None  # the opening fence marker, e.g. ``` or ~~~
    for i, line in enumerate(lines):
        m = _FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0] * 3
                flags[i] = True
                continue
            # an INDENTED code block (4+ spaces) also hides structure
            if line.startswith("    ") or line.startswith("\t"):
                flags[i] = True
            continue
        # inside a fence
        flags[i] = True
        if m and m.group(1)[0] * 3 == fence:
            fence = None
    return flags


def audit(doc_path: Path) -> list:
    """Return a list of defect strings for one document (empty = clean)."""
    defects = []
    if not doc_path.exists():
        return [f"{doc_path.name}: FILE NOT FOUND"]

    text = doc_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    code = _code_line_flags(lines)

    # Only lines that are real document structure count. Lines inside a code
    # fence (e.g. the diff blocks the companion report embeds) are excluded:
    # they are not tables, and the parser does not treat them as tables.
    def is_struct_row(i):
        return (
            0 <= i < len(lines)
            and not code[i]
            and lines[i].lstrip().startswith("|")
        )

    sep_indices = [
        i for i, l in enumerate(lines) if _is_separator(l) and not code[i]
    ]
    n_struct_seps = len(sep_indices)

    # A: header must be a real table row immediately above the separator.
    for i in sep_indices:
        if not is_struct_row(i - 1):
            prev = lines[i - 1] if i > 0 else ""
            defects.append(
                f"{doc_path.name} L{i + 1}: table header is not a table row "
                f"(the line above the separator is prose, so the table does "
                f"not render as a table). Offending line starts: "
                f"{prev.strip()[:70]!r}"
            )

    # B: data-row cell count must match the separator's.
    for i in sep_indices:
        ncols = _cell_count(lines[i])
        j = i + 1
        while is_struct_row(j):
            got = _cell_count(lines[j])
            if got != ncols:
                defects.append(
                    f"{doc_path.name} L{j + 1}: row has {got} cells but the "
                    f"separator row declares {ncols} — the extra/missing cell "
                    f"silently shifts every column after it. Row starts: "
                    f"{lines[j].strip()[:70]!r}"
                )
            j += 1

    # C: rendered table count must equal the STRUCTURAL separator-row count.
    md = _parser()
    if md is None:
        defects.append(
            f"{doc_path.name}: markdown_it is not installed — cannot verify "
            f"that tables actually RENDER. This check needs "
            f"`pip install markdown-it-py` in the project venv."
        )
    else:
        tokens = md.parse(text)
        rendered = sum(1 for t in tokens if t.type == "table_open")
        if rendered != n_struct_seps:
            defects.append(
                f"{doc_path.name}: {rendered} tables render but the source has "
                f"{n_struct_seps} structural separator rows — "
                f"{'some tables do not render' if rendered < n_struct_seps else 'some tables render more than once'}."
            )

    # D: a table body interrupted by a blank line splits into two tables.
    #
    # The distinction that matters: a table body that resumes after a blank
    # line is a DEFECT only when the resumed block has NO header+separator of
    # its own. Two legitimate tables separated by a blank line (each with its
    # own header and separator) are the normal case and must NOT be flagged —
    # an earlier version of this check flagged every adjacent table pair.
    for i in sep_indices:
        j = i + 1
        while is_struct_row(j):
            j += 1
        if j >= len(lines) or code[j] or lines[j].strip():
            continue
        k = j + 1
        while k < len(lines) and not lines[k].strip():
            k += 1
        if j == i + 1:
            # separator followed immediately by a blank line: no data rows.
            # Legitimate only if the next structural block is a NEW table
            # (its own header + separator); otherwise the body was orphaned.
            if k < len(lines) and is_struct_row(k) and not (
                k + 1 < len(lines)
                and _is_separator(lines[k + 1])
                and not code[k + 1]
            ):
                defects.append(
                    f"{doc_path.name} L{i + 1}: separator row has no data rows "
                    f"beneath it (blank line at L{j + 1}) and the following "
                    f"table rows have no header of their own."
                )
            continue
        if k < len(lines) and is_struct_row(k):
            # the resumed rows belong to a NEW table if a separator follows
            # their header line
            if k + 1 < len(lines) and _is_separator(lines[k + 1]) and not code[k + 1]:
                continue
            defects.append(
                f"{doc_path.name} L{i + 1}: table body is interrupted by a "
                f"blank line at L{j + 1} — it renders as two separate tables."
            )
    return defects


def main(argv):
    paths = [Path(a) for a in argv[1:]] if len(argv) > 1 else DEFAULT_DOCS
    all_defects = []
    print("=" * 70)
    print("MARKDOWN TABLE STRUCTURE AUDIT")
    print("=" * 70)
    for p in paths:
        defects = audit(p)
        ntab = (
            sum(1 for l in p.read_text(encoding="utf-8").split("\n") if _is_separator(l))
            if p.exists()
            else 0
        )
        if defects:
            print(f"\n  {p.name}: {ntab} table(s), {len(defects)} DEFECT(S)")
            for d in defects:
                print(f"    - {d}")
        else:
            print(f"\n  {p.name}: {ntab} table(s) - all well-formed")
        all_defects.extend(defects)

    print()
    print("-" * 70)
    if all_defects:
        print(f"RESULT: FAIL — {len(all_defects)} defect(s) across "
              f"{len(paths)} document(s).")
        print("-" * 70)
        return 1
    print("OK: every table header is a real table row, every row's cell count")
    print("    matches its separator, and every table renders.")
    print("-" * 70)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
