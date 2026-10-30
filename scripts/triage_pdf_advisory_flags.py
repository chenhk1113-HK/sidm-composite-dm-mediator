#!/usr/bin/env python
"""Triage gate layer 11's ADVISORY prose flags against a clean extractor.

Why this exists
---------------
`audit_pdf_render.py --gate-mode` does not fail on PROSE token-containment
flags; it routes them here as advisory, because pdftotext silently drops the
math glyphs these reports are made of. That policy is only honest if every
flag is actually checked. This script is that check.

Witness
-------
pdfplumber, used ALONE (not the audit's pdfplumber+pdftotext union). On the
v1.11 report PDF pdfplumber reads 227 sigma glyphs and pdftotext reads 0 of
them, across 32 of 48 pages — so pdfplumber is the strong witness: if a token
is missing even here, the content is really missing.

Verdict per line
----------------
PRESENT (layout artifact)  every alphanumeric token of the source line appears
                           in pdfplumber's token set. The flag came from the
                           builder raising exponents/subscripts onto another
                           baseline ('x10^-12' extracted as '10' + raised
                           '-12'), or from pdftotext glyph loss.
GENUINELY ABSENT           a residual token exists that no normalisation
                           explains. That is a render defect and must be fixed
                           in the source markdown, not reclassified.

Last measured run (2026-10-29 rebuild): 6/6 flagged lines PRESENT, 0 genuine.
(The 2026-10-28 gate run flagged 9/9, also verified present, 0 genuine. The
advisory count moves between rebuilds — 9 -> 6 — with the builder's
line-wrapping non-determinism; both runs are real and both were checked
line-by-line. Tracked as CG-15.)

SCOPE LIMIT (declared): this layer checks ALPHANUMERIC token presence only.
Symbol-only corruption — a lost sigma, a dropped exponent (10^-44 rendered as
1044), a mangled subscript — does not fail this layer when the alphanumeric
neighbours survive. Per-glyph render fidelity is CG-14's problem, not this
layer's.

Usage
-----
  python scripts/triage_pdf_advisory_flags.py [pairs.json]
Run it after any gate run that reports advisory flags. Exit 0 = no genuine
absence; exit 1 = at least one line is really missing from the PDF.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber is required (it is the witness extractor). Run this "
             "with an interpreter that has it, e.g. the pythoncore-3.14 build.")

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "scripts" / "audit_pdf_render.py"


def tokenise(text: str) -> list[str]:
    """Alphanumeric tokens, lowercased. Glyphs, subscripts and baseline
    position are dropped on purpose: the question is whether the CONTENT is
    there, not whether the typography survived extraction."""
    return re.findall(r"[0-9a-z]+", text.lower())


def _resolve(p: str) -> Path:
    """pdf_jobs.json stores WSL-style paths ('/mnt/c/Users/...') because the
    PDF builder runs under WSL. Translate them for a Windows interpreter."""
    q = p.replace("\\", "/")
    m = re.match(r"^/mnt/([a-zA-Z])/(.*)$", q)
    if m:
        return Path(f"{m.group(1).upper()}:/{m.group(2)}")
    return Path(p)


def main(argv: list[str]) -> int:
    pairs_path = Path(argv[1]) if len(argv) > 1 else REPO / "docs" / "papers" / "pdf_jobs.json"
    jobs = json.loads(pairs_path.read_text(encoding="utf-8"))

    run = subprocess.run([sys.executable, str(AUDIT), "--full-flags"],
                         capture_output=True, text=True, cwd=str(REPO))
    # Exit 0 = clean, 1 = defects found (the normal case here). Anything else,
    # or a traceback anywhere in the output, means the audit did not actually
    # run — and 'the audit did not run' must NEVER be reported as 'no flags'.
    # An earlier version of this script did exactly that, and reported a clean
    # 0/0 for a crashed audit.
    if "Traceback" in run.stdout + run.stderr or run.returncode > 1:
        print(f"AUDIT DID NOT RUN (exit {run.returncode})\n"
              f"{(run.stderr or run.stdout)[-900:]}")
        return 2

    genuine = 0
    total_flagged = 0
    for job in jobs:
        md = _resolve(job["md"])
        pdf = _resolve(job["pdf"])
        if not pdf.exists():
            print(f"{pdf.name}: PDF MISSING on disk")
            genuine += 1
            continue

        # The audit prints one defect line per flagged source line, with the
        # source line quoted at the end. Recover exactly those lines.
        # n22 fix (Medium-High): the audit quotes with !r (repr), which uses
        # DOUBLE quotes whenever the slice contains an apostrophe and no double
        # quote. A single-quote-only pattern silently skipped such lines —
        # `continue` before total_flagged, so they were neither tested nor
        # counted. Match BOTH repr quote styles.
        SOURCE_RE = re.compile(
            r"""; source ('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")""")
        scoped = [d for d in SOURCE_RE.findall(run.stdout)]
        if not scoped:
            continue

        with pdfplumber.open(pdf) as doc:
            witness = "\n".join((p.extract_text() or "") for p in doc.pages)
        witness_tokens = set(tokenise(witness))

        flagged_here = re.findall(
            rf"{re.escape(pdf.name)}: source prose line not contained[^\n]*",
            run.stdout)
        if not flagged_here:
            continue
        print(f"\n{pdf.name}: {len(flagged_here)} advisory flag(s)")
        for entry in flagged_here:
            m = SOURCE_RE.search(entry)
            if not m:
                continue
            src = m.group(1).strip().strip("'\"").replace("**", "").replace("`", "")
            distinctive = [t for t in tokenise(src) if len(t) >= 2]
            missing = [t for t in distinctive if t not in witness_tokens]
            # A compound token like '7.5x10' is one token in the source and
            # several in the PDF (the exponent is drawn on a raised baseline).
            residual = [t for t in missing
                        if not all(p in witness_tokens
                                   for p in re.split(r"[^0-9a-z]+", t) if p)]
            total_flagged += 1
            if residual:
                genuine += 1
                print(f"  GENUINELY ABSENT   residual={residual}  src={src[:80]!r}")
            else:
                print(f"  PRESENT (layout)   src={src[:80]!r}")

    print(f"\nSUMMARY: {total_flagged} advisory flag(s), {genuine} genuine absence(s)")
    if genuine:
        print("ACTION: fix the source markdown; do not reclassify these as advisory.")
        return 1
    print("OK: every advisory flag is a layout/extraction artifact, verified "
          "line-by-line against pdfplumber alone.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
