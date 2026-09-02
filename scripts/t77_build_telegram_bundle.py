"""Build the T77 (LZ signal update) Telegram bundle.

Pattern: layman MD as body, PDF as attachment, ZIP with extras.
Same shape as t73/t75/t76 bundles.
"""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t77_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


LAYMAN = read(REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md")
TECH = read(REPO / "v0.3-prelim" / "docs" / "T77_LZ_2026_09_UPDATE.md")

# Consolidated wrap-up MD (layman + tech reference)
wrap_md = OUT / "t77_lz_2026_09_wrap_up.md"
wrap_md.write_text(
    f"""# T77 — LZ 2026-09-01 Mysterious Signal Update (v0.4-prelim)
> Telegram wrap-up, 2026-09-02. Shipped in commit `14de661`.

## Layman Summary
{LAYMAN}

---

## Technical Reference
{TECH}
""",
    encoding="utf-8",
)
print(f"[1/3] wrote {wrap_md} ({wrap_md.stat().st_size} B)")

# PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    pdf_path = OUT / "t77_lz_2026_09_wrap_up.pdf"
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
            continue
        elif raw_line.startswith("|"):
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
    print(f"[2/3] PDF failed: {e}")
    pdf_path = None

# ZIP
zip_path = OUT / "t77_lz_2026_09_ship_bundle.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "t77_lz_2026_09_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "t77_lz_2026_09_wrap_up.pdf")
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T77_LZ_2026_09_UPDATE.md",
        "T77_LZ_2026_09_UPDATE.md",
    )
    zf.write(
        REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
        "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")