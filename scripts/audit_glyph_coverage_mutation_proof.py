#!/usr/bin/env python3
"""Mutation proof for gate layer 14 (audit_glyph_coverage.py) — CG-14 closure evidence.

Builds synthetic MUTANT PDFs from raw bytes (stdlib only; no reportlab needed) and
asserts the layer-14 audit FAILS on each, and PASSES on a clean control. This is the
mutation half of the CG-14 closure claimed in the consolidated report §23.3; the
other half is the live-pair run in the normal gate (layer 14).

Mutants:
  A  null byte inside the content string with a base-14 font (no ToUnicode CMap):
     extracts as (cid:0) — the .notdef/empty-box signature of the original D1 class.
  B  PDF draws only "AB" while the paired markdown source contains 漢字 —
     coverage check must catch the missing CJK glyph.
Control:
  C  pdfplumber over the live REFINT PDF (pdf-only mode): must PASS — proves the
     checks are not vacuously failing.

Exit 0 iff every expectation holds. Run:
  python scripts/audit_glyph_coverage_mutation_proof.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "audit_glyph_coverage.py"
REPO = HERE.parent
REFINT_PDF = Path(r"C:/Users/lamkuenai/round5_deliver/SIDM_REFERENCE_INTEGRITY_v1.0_2026-10-27.pdf")


def _wrap_pdf(content: bytes) -> bytes:
    """Minimal one-page PDF (Helvetica base-14, no ToUnicode) wrapping a content stream."""
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref_pos = len(out)
    out += b"xref\n0 %d\n" % (len(objs) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (len(objs) + 1, xref_pos))
    return bytes(out)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="n22_glyph_mutants_"))
    results = []

    # --- Mutant A: null byte in content stream -> (cid:0) / nullish glyph ---------
    content_a = b"BT /F1 24 Tf 40 100 Td (AB\x00CD) Tj ET"
    pdf_a = tmp / "mutant_A_null_cid0.pdf"
    pdf_a.write_bytes(_wrap_pdf(content_a))
    ra = subprocess.run([sys.executable, str(AUDIT), "--pdf-only", str(pdf_a)],
                        capture_output=True, text=True)
    a_failed = ra.returncode == 1 and ("(cid:0)" in ra.stdout or "\x00" in ra.stdout)
    results.append(("A null-byte .notdef caught as (cid:0)/nullish", a_failed, ra.stdout.strip()))

    # --- Mutant B: CJK in source md, absent from PDF ------------------------------
    content_b = b"BT /F1 24 Tf 40 100 Td (AB) Tj ET"
    pdf_b = tmp / "mutant_B_missing_cjk.pdf"
    pdf_b.write_bytes(_wrap_pdf(content_b))
    md_b = tmp / "mutant_B_source.md"
    md_b.write_text("# mutant\n\nThis source contains \u6f22\u5b57 CJK glyphs the PDF never draws.\n",
                    encoding="utf-8")
    jobs_b = tmp / "jobs_B.json"
    jobs_b.write_text(json.dumps([{"md": str(md_b), "pdf": str(pdf_b)}]), encoding="utf-8")
    rb = subprocess.run([sys.executable, str(AUDIT), str(jobs_b)],
                        capture_output=True, text=True)
    b_failed = rb.returncode == 1 and "appears 0 times" in rb.stdout
    results.append(("B missing source CJK glyph caught by coverage", b_failed, rb.stdout.strip()))

    # --- Control C: live REFINT pdf-only audit must PASS --------------------------
    if REFINT_PDF.exists():
        rc = subprocess.run([sys.executable, str(AUDIT), "--pdf-only", str(REFINT_PDF)],
                            capture_output=True, text=True)
        c_ok = rc.returncode == 0 and "VERDICT: PASS" in rc.stdout
        results.append(("C live REFINT control passes", c_ok, rc.stdout.strip()))
    else:
        results.append(("C live REFINT control passes", False, f"missing {REFINT_PDF}"))

    print("LAYER-14 MUTATION PROOF (CG-14 closure evidence)")
    print("=" * 60)
    ok_all = True
    for name, ok, out in results:
        print(f"[{'PASS' if ok else 'FAIL'}] expectation: {name}")
        for line in out.splitlines():
            if line.strip():
                print(f"    {line}")
        ok_all = ok_all and ok
    print("=" * 60)
    print("ALL MUTATION EXPECTATIONS MET" if ok_all else "MUTATION PROOF BROKEN")
    print(f"mutants kept for inspection at: {tmp}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
