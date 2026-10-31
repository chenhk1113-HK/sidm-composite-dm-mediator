#!/usr/bin/env python3
"""End-to-end mutation proof for the gate's crash semantics (n24 item 2).

WHY (review quote, n22.docx §3.3): "§22.3's dismissal rests on reading the
code — nobody ever showed that a KILLED layer subprocess actually turns the
gate red. This document's own principle, quoted at least three times: 'A
check that has never been shown to fail is an assumption.'"

This script upgrades that dismissal from argument to evidence:

  MUTANT RUN — take the shipped verify_release_gate.py, replace exactly one
  audit (layer 13) with a subprocess that exits 3, run the whole gate, and
  assert: exit code 1, the layer reads FAILED (exit code 3), the summary
  says ONE OR MORE GATE LAYERS FAILED, the poisoned layer is absent from
  the 'Checked:' list, and no PASS phrasing appears anywhere.

  CONTROL RUN — run the UNMODIFIED shipped gate with --quick and assert:
  exit 0, pytest recorded as SKIP (never PASS), the SKIP is named in the
  summary, and the SCOPE disclosure line is present. This is the CG-10 /
  CG-5 evidence produced in the same 30-second-spirit exercise: the summary
  honesty contract is exercised end-to-end, not just read.

No shipped file is mutated: the mutant is a scratch copy inside the repo
(scripts/_mutation_scratch/) so its relative audit paths still resolve; the
copy is deleted afterwards.

Exit: 0 = both proofs fired as expected; 1 = the gate did NOT behave as
promised (which would itself be the finding).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "scripts" / "verify_release_gate.py"
SCRATCH = REPO / "scripts" / "_mutation_scratch"

# The layer to poison. Exact literal must appear exactly once in the gate,
# so the replacement is unambiguous and provably confined to layer 13.
TARGET = '"scripts/audit_stale_strings.py"'
POISON = '"-c", "raise SystemExit(3)"'

failures: list[str] = []


def check(cond: bool, label: str) -> None:
    print(f"  [{'OK' if cond else 'VIOLATION'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    gate_src = GATE.read_text(encoding="utf-8")

    print("== PRE-CONDITIONS ==========================================")
    check(gate_src.count(TARGET) == 1,
          f"poison target {TARGET!r} appears exactly once in the shipped gate "
          "(mutation is provably scoped to layer 13)")
    check("raise SystemExit(3)" not in gate_src,
          "shipped gate contains no SystemExit(3) poison of its own")

    SCRATCH.mkdir(exist_ok=True)
    mutant = SCRATCH / "verify_gate_mutant.py"
    try:
        mutant.write_text(gate_src.replace(TARGET, POISON), encoding="utf-8")

        print("\n== RUN 1: MUTANT GATE (layer 13 poisoned to exit 3) ======")
        r1 = subprocess.run([sys.executable, str(mutant), "--quick"],
                            cwd=str(REPO), capture_output=True, text=True,
                            timeout=1800)
        out1 = r1.stdout + r1.stderr
        check(r1.returncode == 1, "mutant gate exits 1 (a poisoned layer must not exit clean)")
        check("FAILED (exit code 3)" in out1, "poisoned layer prints FAILED (exit code 3)")
        check("ONE OR MORE GATE LAYERS FAILED" in out1, "summary reads ONE OR MORE GATE LAYERS FAILED")
        checked_line = [l for l in out1.splitlines() if l.startswith("Checked:")]
        check(len(checked_line) == 1 and "audit_stale_strings.py" not in checked_line[0],
              "the 'Checked:' list excludes the poisoned layer (it asserted nothing)")
        check("ALL GATES PASSED" not in out1, "no 'ALL GATES PASSED' phrasing survives a poisoned layer")
        check("GATE PASSED" not in out1, "no 'GATE PASSED' phrasing survives a poisoned layer")
    finally:
        mutant.unlink(missing_ok=True)
        try:
            SCRATCH.rmdir()
        except OSError:
            pass

    print("\n== RUN 2: CONTROL (shipped gate, --quick: SKIP semantics) ==")
    r2 = subprocess.run([sys.executable, str(GATE), "--quick"],
                        cwd=str(REPO), capture_output=True, text=True,
                        timeout=1800)
    out2 = r2.stdout + r2.stderr
    check(r2.returncode == 0, "control gate exits 0 on the current tree")
    check("[SKIP] pytest" in out2, "--quick records pytest as SKIP, not PASS (CG-10)")
    check("SKIPPED: pytest" in out2, "the skip is NAMED in the summary line (CG-10)")
    check("asserts nothing" in out2, "summary states that a skipped layer asserts nothing")
    check("SCOPE:" in out2, "CG-5 scope disclosure line is printed")
    check("ALL GATES PASSED" not in out2, "even a fully green run never prints 'ALL GATES PASSED'")

    print("\n== VERDICT ==============================================")
    if failures:
        print(f"MUTATION PROOF FAILED — {len(failures)} assertion(s) violated:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("MUTATION PROOF PASSED: a killed layer demonstrably turns the gate red "
          "(n24 item 2: dismissal upgraded from code-reading to evidence), and the "
          "--quick SKIP + SCOPE contract fires end-to-end (CG-5, CG-10).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
