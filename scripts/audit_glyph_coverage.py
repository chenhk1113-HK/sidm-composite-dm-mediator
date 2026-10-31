#!/usr/bin/env python
"""Gate layer 14: glyph-coverage audit — closes CG-14 (the D1 empty-box class).

WHY THIS EXISTS (n22 finding, CG-14)
------------------------------------
Layers 11/12 compare ALPHANUMERIC token containment. A character that renders
as .notdef (an empty box) — the original D1 defect: CJK quoting a review became
U+0000 boxes in the v1.5 PDFs — is invisible to token checks: its ASCII
neighbours survive, so the line "contains" everything the source line contains.
Layer 11's own docstring admits empty boxes pass. Until now CG-14 rested on the
builder's SimHei font registration — a fix, not a gate.

WHAT THIS LAYER ASSERTS (per md<->PDF pair in docs/papers/pdf_jobs.json)
------------------------------------------------------------------------
1. NULL/REPLACEMENT SCAN: no page.chars entry has text '\\x00', '\\ufffd' or ''.
   (A .notdef glyph surfaces as a null byte or U+FFFD in the extraction.)
2. NON-ASCII SOURCE COVERAGE: every distinct non-ASCII character present in the
   markdown source appears at least once in the PDF's page.chars text set.
   A source glyph entirely absent from the PDF's character stream is a render
   loss, even when its surrounding words survive.
3. ZERO-WIDTH ASSERTION: no page.chars entry with non-empty text has width <= 0
   AND a null/zero font signature (x1==x0) — the empty-box drawing signature.
   (Zero-width plain spaces are normal kerning artefacts and are exempt.)
4. CJK EXPLICIT CHECK: for codepoints 0x4E00-0x9FFF present in the source, each
   must be present in page.chars text — CJK is the known failure family.

Exit codes (gate contract)
--------------------------
  0 = PASS   1 = glyph defects found   2 = audit crashed (gate must fail)

Honest limitations
------------------
- Extraction-level check: a font that maps a codepoint to a *wrong but
  printable* glyph (glyph substitution, not .notdef) is NOT caught. That is a
  visual-fidelity problem, out of scope here and stated as such.
- Characters legitimately re-encoded by the builder (e.g. unicode superscripts
  drawn as caret form, '≪' substituted with '<<') are handled by an explicit
  substitution allowance list below — additions there require evidence.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The substitution allowance for builder re-encodes is DERIVED from the same
# maps the builder imports (scripts/pdf_rencode_maps.py). n24 item 3
# (2026-10-31): this file previously hand-copied the builder's strip map with
# a "These MUST mirror ..." comment — a second copy held together by prose,
# the exact pattern CG-6 closed for the physics scripts. A checker's hand
# copy is worse than a script's: its table is read as evidence. Reference,
# not mirror: both sides now import the same dict.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_rencode_maps import SUP, SUB, MONO_FALLBACK

# Extractor-level allowances: the builder WROTE the original glyph and the
# extractor reads it back in a different form (× extracted as x, dashes
# collapsing). These are extractor behaviours measured on these PDF pipelines,
# not builder re-encodes, so they live here with their evidence and are NOT
# derived from the builder maps.
EXTRACTION_ALLOWANCE = {
    "\u00d7": {"x"},           # × may extract as x in some font paths
    "\u2013": {"-"}, "\u2014": {"-"},   # dashes collapse
    "\u2192": {"->"},          # arrow fallback
    "\u2264": {"<="}, "\u2265": {">="},
}


def _derived_allowance() -> dict:
    """Allowances for characters the BUILDER re-encodes, derived from the
    shared maps. Digits fold to their plain ASCII form; caret/underscore
    forms are accepted as alternates because AGENTS.md rule 27 makes the
    source itself use 10^-N, so a future builder switch to caret rendering
    would match without touching this code. U+207B/U+207A fold to '-'/'+',
    but a bare '-'/'+' match proves nothing (every PDF contains them), so the
    caret form is their only allowance — same semantics as the table this
    derivation replaces."""
    allow = {k: {v} for k, v in MONO_FALLBACK.items()}
    for k, v in SUP.items():
        allow[k] = {v, "^" + v} if v.isdigit() else {"^" + v}
    for k, v in SUB.items():
        allow[k] = {v, "_" + v}
    return allow


SUBSTITUTION_ALLOWANCE = {**EXTRACTION_ALLOWANCE, **_derived_allowance()}

# Completeness guard (fail closed): every character the builder re-encodes
# must have an allowance in this audit. A builder adding a re-encode without
# touching the audit is automatically covered; a future refactor that drops
# the derivation trips this assert.
_missing = (set(SUP) | set(SUB) | set(MONO_FALLBACK)) - set(SUBSTITUTION_ALLOWANCE)
assert not _missing, f"glyph audit not covering builder re-encodes: {sorted(_missing)}"

NULLISH = {"\x00", "\ufffd", ""}

# Benign-family evidence (measured 2026-10-30 on the live v1.12 + REFINT PDFs):
# every '(cid:N)' placeholder entry sits at LINE-START x0 (57.2), has x1==x0
# (zero advance) and an unmapped font — the builder's (reportlab text pipeline)
# line-assembly separators.
# They draw nothing and advance nothing: no source glyph is lost (checks 1/2
# are what catch real losses). Counted and reported, never a failure. A REAL
# .notdef from the D1 family extracted as \x00 in these very PDF pipelines
# (consolidated report §17.2) — check 1 catches exactly that signature.
CID_PLACEHOLDER = re.compile(r"^\(cid:\d+\)$")

# (cid:0) is glyph id 0 = .notdef in pdfplumber's cid-extraction path (proven
# synthetically 2026-10-30: a literal \000 in a content stream extracts as
# '(cid:0)'). Always a defect, width or not.
# Zero-width exemption for combining marks / variation selectors / format
# chars (Unicode Mn/Me/Cf, e.g. U+FE0F): invisible by design, zero advance is
# their definition, not a render loss.
# Superscript/subscript caret allowances are DERIVED above from the shared
# re-encode maps (see the reference note at the top of this file) — no literal
# super/subscript table lives in this script any more, by construction.


def _resolve(p: str) -> Path:
    q = p.replace("\\", "/")
    m = re.match(r"^/mnt/([a-zA-Z])/(.*)$", q)
    if m:
        return Path(f"{m.group(1).upper()}:/{m.group(2)}")
    return Path(p)


def audit_pair(md: Path | None, pdf: Path) -> tuple[list[str], int]:
    """Return (defect_lines, chars_scanned) for one pair (md may be None)."""
    import pdfplumber

    defects: list[str] = []
    pdf_chars: set[str] = set()
    text_parts: list[str] = []
    n_scanned = 0
    n_benign_cid = 0

    with pdfplumber.open(pdf) as doc:
        for pno, page in enumerate(doc.pages, 1):
            for ch in (page.chars or []):
                n_scanned += 1
                t = ch.get("text", "")
                if t in NULLISH:
                    defects.append(
                        f"p{pno}: nullish char in glyph stream (text={t!r} "
                        f"font={ch.get('font_name','?')}) — .notdef empty-box signature")
                    continue
                x0, x1 = ch.get("x0"), ch.get("x1")
                zero_w = x0 is not None and x1 is not None and x1 <= x0
                if CID_PLACEHOLDER.match(t):
                    if t == "(cid:0)":
                        defects.append(
                            f"p{pno}: (cid:0) glyph — glyph id 0 is .notdef, the "
                            f"empty-box signature (width {x0}..{x1})")
                    elif zero_w:
                        n_benign_cid += 1      # line-assembly separator: draws nothing
                    else:
                        defects.append(
                            f"p{pno}: unmapped glyph {t!r} WITH width "
                            f"(x0={x0}, x1={x1}) — draws a box for a codepoint "
                            f"the extraction cannot name")
                    continue
                pdf_chars.add(t)
                text_parts.append(t)
                if (zero_w and t not in " \t"
                        and unicodedata.category(t) not in ("Mn", "Me", "Cf")):
                    defects.append(f"p{pno}: zero-width drawn glyph {t!r} (x0==x1)")

    full_text = "".join(text_parts)

    if md is not None and md.exists():
        src = md.read_text(encoding="utf-8", errors="replace")
        src_nonascii = {c for c in src if ord(c) > 127}
        n_allowed = 0
        for c in sorted(src_nonascii):
            if c in pdf_chars:
                continue
            allowed = SUBSTITUTION_ALLOWANCE.get(c)
            if allowed and any(a in pdf_chars or a in full_text for a in allowed):
                n_allowed += 1
                print(f"  allowed substitution: source U+{ord(c):04X} {c!r} -> "
                      f"builder ASCII form present in PDF (disclosed behaviour)")
                continue
            defects.append(
                f"source glyph U+{ord(c):04X} {c!r} appears 0 times in the PDF "
                f"glyph stream (no substitution allowance matched)")

    return defects, n_scanned, n_benign_cid


def main(argv: list[str]) -> int:
    try:
        import pdfplumber  # noqa: F401  (fail fast with clear message)
    except ImportError:
        print("pdfplumber is required for the glyph-coverage audit (fail closed).")
        return 2

    if len(argv) > 1 and argv[1] == "--pdf-only":
        # mutation-testing / spot-check mode: no md, checks 1+3 only
        total_bad = 0
        for raw in argv[2:]:
            pdf = _resolve(raw)
            defects, n, benign = audit_pair(None, pdf)
            print(f"{pdf.name}: {n} glyph entries scanned ({benign} benign line-assembly cid separators)")
            for d in defects[:10]:
                print(f"  {d}")
            if defects:
                print(f"  VERDICT: FAIL — {len(defects)} glyph defect(s)")
                total_bad += 1
            else:
                print("  VERDICT: PASS")
        return 1 if total_bad else 0

    pairs_path = Path(argv[1]) if len(argv) > 1 else REPO / "docs" / "papers" / "pdf_jobs.json"
    jobs = json.loads(pairs_path.read_text(encoding="utf-8"))
    total_bad = 0
    for job in jobs:
        md = _resolve(job["md"]) if job.get("md") else None
        pdf = _resolve(job["pdf"])
        if not pdf.exists():
            print(f"{pdf.name}: PDF MISSING on disk")
            total_bad += 1
            continue
        defects, n, benign = audit_pair(md, pdf)
        print(f"{pdf.name}: {n} glyph entries scanned, md={'yes' if md and md.exists() else 'no'} "
              f"({benign} benign line-assembly cid separators)")
        for d in defects[:15]:
            print(f"  {d}")
        if defects:
            print(f"  VERDICT: FAIL — {len(defects)} glyph defect(s)")
            total_bad += 1
        else:
            print("  VERDICT: PASS — no nullish glyphs; all source non-ASCII glyphs "
                  "present in the PDF glyph stream")
    if total_bad:
        print(f"\nGLYPH COVERAGE AUDIT FAILED — {total_bad} PDF(s) defective. CG-14 class.")
        return 1
    print("\nGLYPH COVERAGE AUDIT PASSED (CG-14: empty-box class is now machine-checked)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:  # a crashed audit must never read as 'clean'
        print(f"AUDIT CRASHED (exit 2): {type(exc).__name__}: {exc}")
        sys.exit(2)
