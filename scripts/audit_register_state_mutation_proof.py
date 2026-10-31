#!/usr/bin/env python3
"""Mutation proof for gate layer 15 (audit_register_state.py, closes CG-17).

Principle (this project's own, quoted in the n22 review): "A check that has
never been shown to fail is an assumption."

Four runs against copies of the CURRENT live report (never the shipped one):

  CONTROL   unmodified copy            -> expect exit 0 (clean pass)
  MUT-A     drop a CG from the live open-set line
                                         -> expect exit 1, 'missing from prose'
                                            (the n23 finding-2 shape: a gap that
                                            lives in the table but not in the
                                            announced open set)
  MUT-B     flip the canonical table row of a CLOSED gap to OPEN
                                         -> expect exit 1, open-set disagreement
                                            (the n23 finding-1 shape: table and
                                            round prose disagree)
  MUT-C     inject 'CG-14 remains OPEN pending a glyph follow-up.' as its OWN
            line inside the live round section
                                         -> expect exit 1, status-sentence
                                            disagreement with the table
                                            (the stale-status-sentence class)

Plus the design-decision control that makes the layer usable: frozen historical
rounds DO contain superseded statements ('OPEN as of v1.12') — the CONTROL run
passing with those statements present is the proof that the live/frozen split
does not false-fire on history. If someone later 'fixes' the audit to scan
frozen sections too, this proof will start failing on the real report.

Version-agnostic anchoring (rewritten 2026-10-31 for the v1.15 roll): the
proof imports the audit's OWN live_region(), OPEN_ENUM_HEAD and parse_register
and resolves every injection target inside the live region, so a report roll
re-anchors automatically; the pre-conditions still REFUSE the run (never a
silent no-op) when the live region drifts from the expected shape. MUT-C
injects on its own line because the audit's Check C is line-scoped — a
sentence glued onto the open-set line would sit in a multi-CG line and be
exempt by design.

Exit: 0 = all four expectations fired; 1 = audit misbehaved (itself a finding).
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "scripts" / "audit_register_state.py"
SCRATCH = REPO / "scripts" / "_mutation_scratch"

_spec = importlib.util.spec_from_file_location("audit_register_state", AUDIT)
_ar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ar)

failures: list[str] = []


def run_audit(md: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(AUDIT), str(md)],
                       cwd=str(REPO), capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def expect(label: str, code: int, out: str, code_want: int, needle: str) -> None:
    ok = (code == code_want) and (needle in out)
    print(f"  [{'OK' if ok else 'VIOLATION'}] {label} (exit {code}, wanted {code_want})")
    if not ok:
        failures.append(label)
        print("".join(f"      | {l}\n" for l in out.splitlines()[-6:]))


def main() -> int:
    md = _ar.latest_report()
    text = md.read_text(encoding="utf-8")
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # ---- resolve live-region anchors via the audit's own definitions ----
    live_text, live_num = _ar.live_region(text)
    enums = list(_ar.OPEN_ENUM_HEAD.finditer(live_text))
    table, _ = _ar.parse_register(text)
    table_open = sorted(cid for cid, s in table.items() if s == "OPEN")

    pre = [
        (len(enums) == 1, f"exactly one canonical open-set line in live section ## {live_num}"),
        (len(table_open) >= 1, f"register table has a non-empty OPEN set {table_open}"),
    ]
    enum_line = None
    if enums:
        start = live_text.find("\n", enums[0].start())
        enum_line = live_text[enums[0].start():start if start != -1 else len(live_text)]
        listed = {int(g) for g in _ar.CG_ID.findall(enum_line)}
        pre.append((set(table_open) <= listed,
                    f"open-set line lists the table's OPEN set {table_open}"))
    cg8_rows = list(re.finditer(r"^\| \*\*CG-8\*\* \|.*$", text, re.M))
    pre.append((len(cg8_rows) >= 1 and "**CLOSED" in cg8_rows[0].group(0),
                "canonical CG-8 row findable and currently CLOSED"))
    print(f"report under mutation: {md.name}")
    for ok, label in pre:
        print(f"  [{'OK' if ok else 'VIOLATION'}] {label}")
        if not ok:
            print("PROOF REFUSED: report no longer matches the injection targets — "
                  "update the proof with the report, never against it.")
            return 1

    jobs = []

    # CONTROL — the shipped text, copied verbatim.
    p = SCRATCH / "report_control.md"
    p.write_text(text, encoding="utf-8")
    jobs.append(("CONTROL: unmodified report must PASS (frozen superseded "
                 "statements are exempt by design)", p, 0, "REGISTER STATE AUDIT PASSED"))

    # MUT-A — drop the last enumerated gap from the live open-set line.
    p = SCRATCH / "report_mut_a.md"
    drops = list(re.finditer(r",?\s*\*\*CG-\d+\*\*(?:\s*\([^)\n]*\))?", enum_line))
    d = drops[-1]
    dropped_id = re.search(r"CG-\d+", d.group(0)).group(0)
    mutated_line = enum_line[:d.start()] + enum_line[d.end():]
    p.write_text(text.replace(enum_line, mutated_line, 1), encoding="utf-8")
    jobs.append((f"MUT-A: open-set line missing {dropped_id} must FAIL", p, 1,
                 "missing from prose"))

    # MUT-B — flip the canonical CG-8 row CLOSED -> OPEN in the register table.
    p = SCRATCH / "report_mut_b.md"
    # flip only the canonical (first) CG-8 row's status cell
    rows = [m for m in re.finditer(r"^\| \*\*CG-8\*\* \|.*$", text, re.M)]
    row = rows[0].group(0)
    flipped = row.replace("**CLOSED", "**OPEN", 1)
    p.write_text(text.replace(row, flipped, 1), encoding="utf-8")
    jobs.append(("MUT-B: table row flipped to OPEN while prose open-set omits it must FAIL", p, 1,
                 "disagrees with the register table"))

    # MUT-C — stale status sentence as its own line inside the LIVE section.
    p = SCRATCH / "report_mut_c.md"
    mutated = text.replace(enum_line, enum_line + "\nCG-14 remains OPEN pending a glyph follow-up.", 1)
    p.write_text(mutated, encoding="utf-8")
    jobs.append(("MUT-C: live prose asserting OPEN for a table-CLOSED gap must FAIL", p, 1,
                 "asserts OPEN but the register table says CLOSED"))

    for label, path, code_want, needle in jobs:
        code, out = run_audit(path)
        expect(label, code, out, code_want, needle)

    for p in SCRATCH.glob("report_mut*.md"):
        p.unlink(missing_ok=True)
    for p in SCRATCH.glob("report_control.md"):
        p.unlink(missing_ok=True)
    try:
        SCRATCH.rmdir()
    except OSError:
        pass

    print()
    if failures:
        print(f"LAYER-15 MUTATION PROOF FAILED — {len(failures)} expectation(s) violated.")
        return 1
    print("LAYER-15 MUTATION PROOF PASSED: the register-vs-prose audit demonstrably "
          "catches all three n23 finding shapes (open-set missing a gap, table/prose "
          "disagreement, stale status sentence) while leaving frozen history unflagged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
