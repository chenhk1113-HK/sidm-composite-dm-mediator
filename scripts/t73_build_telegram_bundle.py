"""Build a Telegram-friendly wrap-up bundle for the T73 ship.

Creates:
- T73_wrap_up.md (consolidated summary suitable for chat / GitHub)
- T73_wrap_up.pdf (small PDF for archive)

Both go into <out_dir> for delivery via `hermes send --to telegram --file ...`.
"""
from __future__ import annotations

import os
import sys
import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t73_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# 1) Consolidate the technical + layman into a single wrap-up MD
LAYMAN = read(REPO / "docs" / "LAYMAN_SUMMARY_T73_DAMPE.md")
TECHNICAL = read(REPO / "v0.3-prelim" / "docs" / "T73_DAMPE_V04_INTEGRATION.md")
SMOKE_JSON = read(
    REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_dampe_poc"
    / "dampe_v04_integration.json"
)

consolidated = f"""# T73 — DAMPE CRE joint-fit integration (v0.4-prelim)
> Telegram wrap-up, 2026-09-02. Shipped in commit `1d40286` + layman `5b8fa8f`.

---

## Layman Summary
{LAYMAN.split("# Layman Summary — T73 DAMPE Joint-Fit Integration (v0.4-prelim)")[-1] if "# Layman Summary" in LAYMAN else LAYMAN}

---

## Technical reference (excerpt)
{TECHNICAL}

---

## Smoke-test JSON
```json
{SMOKE_JSON}
```
"""

wrap_md = OUT / "T73_wrap_up.md"
wrap_md.write_text(consolidated, encoding="utf-8")
print(f"[1/3] wrote {wrap_md} ({wrap_md.stat().st_size} B)")

# 2) Build a tiny PDF (text-only) for archive
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )

    pdf_path = OUT / "T73_wrap_up.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    story = []
    for raw_line in wrap_md.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("# "):
            story.append(Paragraph(raw_line[2:], styles["Title"]))
        elif raw_line.startswith("## "):
            story.append(Paragraph(raw_line[3:], styles["Heading1"]))
        elif raw_line.startswith("### "):
            story.append(Paragraph(raw_line[4:], styles["Heading2"]))
        elif raw_line.startswith("```"):
            continue  # skip code-block fences in PDF (too wide)
        elif raw_line.startswith("|"):
            # crude markdown table → paragraphs
            cells = [c.strip() for c in raw_line.strip().strip("|").split("|")]
            story.append(Paragraph(" &nbsp;|&nbsp; ".join(cells), styles["BodyText"]))
        elif raw_line.startswith(">"):
            story.append(Paragraph(raw_line[1:].strip(), styles["Italic"]))
        elif raw_line.startswith("- "):
            story.append(Paragraph(raw_line[2:], styles["BodyText"]))
        elif raw_line.startswith("---"):
            story.append(Spacer(1, 0.3 * cm))
        else:
            if raw_line.strip():
                story.append(Paragraph(raw_line, styles["BodyText"]))
    doc.build(story)
    print(f"[2/3] wrote {pdf_path} ({pdf_path.stat().st_size} B)")
except Exception as e:
    print(f"[2/3] PDF generation failed (will skip PDF): {e}")
    pdf_path = None

# 3) ZIP everything
zip_path = OUT / "T73_dampe_v04_prelim.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "T73_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "T73_wrap_up.pdf")
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T73_DAMPE_V04_INTEGRATION.md",
        "T73_DAMPE_V04_INTEGRATION.md",
    )
    zf.write(
        REPO / "docs" / "LAYMAN_SUMMARY_T73_DAMPE.md",
        "LAYMAN_SUMMARY_T73_DAMPE.md",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_dampe_poc"
        / "dampe_v04_integration.json",
        "dampe_v04_integration.json",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")
print(f"\nBundle directory: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")