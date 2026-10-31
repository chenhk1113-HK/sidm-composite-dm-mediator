#!/usr/bin/env python
"""Gate layer 15: report register-vs-prose state audit — closes CG-17.

WHY THIS EXISTS (n24 review round item 1, 2026-10-31)
-----------------------------------------------------
The n23 round caught four defects that were all ONE class: this report keeps
its gap-state in several copies (front matter, round prose, the §17.3 register
table, the round-end open-set line), and a status fixed in one copy survives
stale in the others. The project's answer to the same class on the PAPER side
(stale values resurrecting in prose) was a machine check — gate layer 13. The
answer for the REPORT side had been "wait for the next external reviewer to
notice". Layer 15 is the machine answer.

WHAT THIS LAYER ASSERTS
-----------------------
Target: the newest SIDM_ROUND5_CONSOLIDATED_FIXES_v*.md (version-agnostic:
it is never pinned to a literal version string, so bumping the report cannot
break this check or make it pass vacuously).

Canonical state = the §17.3 register table rows (CG-n rows; status column).

LIVE region  = the highest-numbered '## N.' round section (the current round).
FROZEN       = every earlier round section. Frozen sections record what was
               true at their time ("OPEN as of v1.12") and are deliberately
               NOT asserted — a naive checker that scans them false-fires on
               history and trains humans to ignore it. This live/frozen split
               is the design decision that makes the layer usable; the
               mutation proof exercises both directions.

Checks (live region only, unless stated):
  A. TABLE SANITY — every CG row has a status of OPEN or CLOSED. A CG id
     repeated across tables (frozen rounds restate closures) is allowed only
     when the statuses AGREE; a disagreement is itself a finding.
  B. OPEN-SET EQUALITY — the 'Open set ...:' enumeration line in the live
     region must list exactly the table's OPEN set (missing an open gap, or
     listing a closed one, is a FAIL — this is exactly n23 findings 1/2/3's
     shape). A live round with NO open-set statement also fails: the current
     round must state the set.
  C. STATUS-SENTENCE AGREEMENT — a status token asserts a status only on the
     SAME LINE as a single CG mention (line-scoped, deliberately: ±char
     windows bleed across table rows and attribute another gap's status word,
     which false-fired on the first smoke run). A line with one CG id and
     exactly one uppercase OPEN/CLOSED token is an assertion and must match
     the table. Lines with several CG ids (adjudication tables, open/closed
     lists) or several status tokens (transition narratives) are exempt — a
     status word with an ambiguous owner is not an assertion about any one gap.

Exit codes (gate contract)
--------------------------
  0 = PASS   1 = state inconsistency found   2 = audit crashed (gate fails)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs" / "dual_review_5loop"

CG_ROW = re.compile(r"^\|\s*\*\*CG-(\d+)\*\*\s*\|", re.M)
CG_ID = re.compile(r"CG-(\d+)")
# Canonical open-set line only: the enumeration must START the line
# ('Open set ...:' / 'open gaps are ...'). Deliberately anchored — a status
# sentence like "CG-5 remains OPEN:" must not be mistaken for the open-set
# enumeration; sentence-level status claims are check C's territory, not B's.
OPEN_ENUM_HEAD = re.compile(
    r"^[ \t>*-]*(?:The\s+)?Open\s+set\b[^\n|]*?:|^[ \t>*-]*open gaps are\b", re.I | re.M)
STATUS_WORD = re.compile(r"\b(OPEN|CLOSED)\b")  # uppercase only: report convention
ROUND_SECTION = re.compile(r"^## (\d+)\. ", re.M)


def latest_report(docs_dir: Path = DOCS) -> Path:
    cands = list(docs_dir.glob("SIDM_ROUND5_CONSOLIDATED_FIXES_v*.md"))
    if not cands:
        raise FileNotFoundError(f"no consolidated FIXES report found under {docs_dir}")

    def key(p: Path):
        m = re.search(r"_v(\d+)\.(\d+)_", p.name)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

    return max(cands, key=key)


def parse_register(text: str) -> dict[int, str]:
    """Canonical state: {cg_id: OPEN|CLOSED} from the §17.3 table."""
    rows: dict[int, str] = {}
    defects: list[str] = []
    for m in CG_ROW.finditer(text):
        cid = int(m.group(1))
        rest = text[m.end():].split("\n", 1)[0]
        cells = [c.strip() for c in rest.split("|")]
        status_cell = cells[2] if len(cells) > 2 else ""
        if "OPEN" not in status_cell and "CLOSED" not in status_cell:
            # column split can be disturbed by an in-cell pipe; fall back to
            # the first status token anywhere on the row
            status_cell = rest
        i_open = status_cell.find("OPEN")
        i_closed = status_cell.find("CLOSED")
        if i_open == -1 and i_closed == -1:
            defects.append(f"CG-{cid}: status cell has neither OPEN nor CLOSED: {status_cell[:80]!r}")
            continue
        if i_closed != -1 and (i_open == -1 or i_closed < i_open):
            status = "CLOSED"
        else:
            status = "OPEN"
        if cid in rows:
            # Frozen round sections repeat register rows as history (the CG-9
            # row restates its closure inside §17's own narrative). A duplicate
            # is only a defect when it DISAGREES with the first-parsed status —
            # that is exactly the stale-copy class this layer exists to catch.
            # Agreement across copies is expected and allowed.
            if rows[cid] != status:
                defects.append(
                    f"CG-{cid} appears in two register tables with DIFFERING status "
                    f"({rows[cid]} vs {status}) — stale-copy class (CG-17)")
            continue
        rows[cid] = status
    return rows, defects  # type: ignore[return-value]


def live_region(text: str) -> tuple[str, int]:
    """The highest-numbered '## N.' section: the live round. Everything
    earlier (including earlier round sections) is frozen history."""
    sections = list(ROUND_SECTION.finditer(text))
    if not sections:
        raise ValueError("no '## N.' round sections found — cannot locate the live region")
    live = max(sections, key=lambda m: int(m.group(1)))
    nxt = [s for s in sections if int(s.group(1)) > int(live.group(1))]
    end = min((s.start() for s in nxt), default=len(text))
    # live section extends to the next H2 of ANY kind after the live heading
    after = re.search(r"^## ", text[live.end():], re.M)
    if after:
        end = live.end() + after.start()
    return text[live.start():end], int(live.group(1))


def check(text: str) -> list[str]:
    defects: list[str] = []
    table, table_defects = parse_register(text)
    defects.extend(table_defects)
    if not table:
        return defects + ["no CG register rows parsed — the canonical table is missing or unreadable"]

    live_text, live_num = live_region(text)
    table_open = {cid for cid, s in table.items() if s == "OPEN"}

    # B. open-set enumerations in the live region
    enums = list(OPEN_ENUM_HEAD.finditer(live_text))
    if not enums:
        defects.append(
            f"live section (## {live_num}) states no 'Open:' gap set — the current round "
            "must enumerate the open set explicitly (CG-17: an open set that only "
            "lives in the table is unannounced; one that only lives in prose is unregistered)")
    for e in enums:
        span = live_text[e.start(): e.start() + 1200]
        # The canonical open-set line is ONE line: the enumeration ends at the
        # first newline (or an explicit 'Closed' tail on the same line).
        # Swallowing following paragraphs would collect unrelated CG mentions
        # and manufacture 'extra' findings — strictly line-scoped instead.
        stop = re.search(r"\bClosed\b|\n", span)
        if stop:
            span = span[:stop.start()]
        listed = {int(g) for g in CG_ID.findall(span)}
        if listed != table_open:
            missing = sorted(table_open - listed)
            extra = sorted(listed - table_open)
            defects.append(
                f"open-set enumeration at live §{live_num} disagrees with the register table: "
                f"prose lists {sorted(listed)}; table says OPEN "
                f"{sorted(table_open)}"
                + (f"; missing from prose: {missing}" if missing else "")
                + (f"; closed but still listed open: {extra}" if extra else ""))

    # C. per-CG status sentences in the live region.
    # LINE-scoped (see module docstring): a ±140-char window was the first
    # implementation and it is the wrong unit — a window starting inside one
    # table row can swallow the neighbouring row's status token and attribute
    # another gap's status word to this one. Line scope makes that class
    # structurally impossible, at the cost of ignoring cross-line claims,
    # which is exactly what this report's status sentences never do.
    checked = 0
    for line in live_text.splitlines():
        ids = {int(g) for g in CG_ID.findall(line)}
        if len(ids) != 1:
            continue  # multi-gap lines: adjudication tables, open/closed lists
        cid = next(iter(ids))
        if cid not in table:
            continue  # mentions of unregistered CGs are finding B's / triage's job
        statuses = {s.group(1) for s in STATUS_WORD.finditer(line)}
        if len(statuses) == 1:
            asserted = statuses.pop()
            checked += 1
            if asserted != table[cid]:
                defects.append(
                    f"CG-{cid}: live prose asserts {asserted} but the register table says "
                    f"{table[cid]} — stale-state class (n23 findings 1-3 shape)")
        elif len(statuses) > 1:
            checked += 1  # transition narrative: opened-and-closed etc., exempt by design
    print(f"register rows parsed: {len(table)}; table OPEN set: {sorted(table_open)}")
    print(f"live section: ## {live_num}; status assertions checked: {checked}")
    return defects


def main(argv: list[str]) -> int:
    md = Path(argv[1]) if len(argv) > 1 else latest_report()
    text = md.read_text(encoding="utf-8")
    defects = check(text)
    print(f"report audited: {md.name}")
    if defects:
        print("\nREGISTER STATE AUDIT FAILED (CG-17 class: register vs prose state drift):")
        for d in defects:
            print(f"  - {d}")
        return 1
    print("\nREGISTER STATE AUDIT PASSED (CG-17: the live round's state statements agree "
          "with the canonical §17.3 register; frozen historical rounds are exempt by design)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:  # a crashed audit must never read as 'clean'
        print(f"AUDIT CRASHED (exit 2): {type(exc).__name__}: {exc}")
        sys.exit(2)
