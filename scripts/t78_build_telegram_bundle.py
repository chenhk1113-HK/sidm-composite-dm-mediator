"""Build the T78 (kinetic-mixing link refinement) Telegram bundle."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t78_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


LAYMAN = read(REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md")
TECH = read(REPO / "v0.3-prelim" / "docs" / "T78_KINETIC_MIXING_LZ_LINK.md")
CALC = read(REPO / "v0.3-prelim" / "docs" / "T77_LZ_2026_09_UPDATE.md")

# Consolidated wrap-up MD (T78 lead + layman + tech)
wrap_md = OUT / "t78_kinetic_mixing_refinement_wrap_up.md"
wrap_md.write_text(
    f"""# T78 — Kinetic-Mixing Link Refinement (v0.4-prelim)
> Telegram wrap-up, 2026-09-02. Shipped in commit `686f016`.
> Response to the Consider2.docx technical review of T77.

## Headline

The Consider2.docx reviewer raised 4 points about the T77 framing
of σ_DM-DM vs σ_DM-nucleon orthogonality. **All 4 points were
correct**, and T78 addresses each:

1. "Completely orthogonal" is physically overstated → replaced with
   "practically decoupled"
2. The 10²³ ratio is hand-wavy → replaced with model-specific
   calculation showing ~70 orders of magnitude suppression
3. Pre-register the ≥3σ re-run protocol → done in T77 docs
4. Watch XENONnT/PandaX-4T → already in T77 trigger conditions

## The kinetic-mixing calculation (Kahlhoefer et al.)

σ_SI_Xp = 1.5×10⁻²⁴ cm² × ε²_γ × (α_X/10⁻²) × (m_φ/30 MeV)⁻⁴

At v0.7 MAP (ε=1.12e-37, α_X=6.84e-17, m_φ=453 MeV):

| Quantity | Value |
|---|---|
| Predicted σ_DM-nuc | **~10⁻¹¹⁷ cm²** |
| LZ 2024 limit | ~10⁻⁴⁶ cm² |
| **Suppression** | **~10⁻⁷¹** (70 orders!) |

**Verdict:** even at LZ's hypothetical 5σ confirmation, the project
cannot be constrained. The link is theoretically real but
practically inert.

---

## Layman Summary (T77, refined in T78)
{LAYMAN}

---

## T78 Technical Reference
{TECH}

---

## T77 Technical Reference (with pre-registered protocol)
{CALC}
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

    pdf_path = OUT / "t78_kinetic_mixing_refinement_wrap_up.pdf"
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
zip_path = OUT / "t78_kinetic_mixing_refinement_ship_bundle.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "t78_kinetic_mixing_refinement_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "t78_kinetic_mixing_refinement_wrap_up.pdf")
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T78_KINETIC_MIXING_LZ_LINK.md",
        "T78_KINETIC_MIXING_LZ_LINK.md",
    )
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T77_LZ_2026_09_UPDATE.md",
        "T77_LZ_2026_09_UPDATE.md",
    )
    zf.write(
        REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
        "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
    )
    zf.write(
        REPO / "scripts" / "epsilon_lz_check.py",
        "epsilon_lz_check.py",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_t78_epsilon_lz_check.json",
        "2026-09-02_t78_epsilon_lz_check.json",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")