"""Build the T79 (composite form-factor refinement) Telegram bundle."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t79_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


LAYMAN = read(REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md")
TECH = read(REPO / "v0.3-prelim" / "docs" / "T79_COMPOSITE_FORM_FACTOR_REMNANT.md")

# Consolidated wrap-up MD
wrap_md = OUT / "t79_composite_form_factor_wrap_up.md"
wrap_md.write_text(
    f"""# T79 — Composite Form-Factor Correction + Relic-Density Check (v0.4-prelim)
> Telegram wrap-up, 2026-09-02. Shipped in commit `6b83904`.
> Quantitative refinement of T78 in response to 'comment T78 wrap-u.docx'.

## Headline

The reviewer raised 3 fragilities in T78's "70 orders" claim. T79
addresses all 3:

1. **Composite form factor F²(q) computed** for Gaussian + dipole
   - At LZ event energy (248 keV): F²_gaussian = 0.93, F²_dipole = 0.87
   - **Composite form factor does NOT significantly suppress σ_DM-nuc**
   - Dominant suppression is still ε²

2. **LZ limit at 770 GeV is interpolated** (±5 orders)
   - Acknowledged in uncertainty band
   - KIV cron `080d2f590251` re-checks 2026-11-01

3. **ε ~ 10⁻³⁷ falls in freeze-in regime**
   - Per Coogan et al. arXiv:1907.04324v1
   - Requires T_RH > 10¹⁵ GeV or non-standard cosmology
   - **Consistent with project's v0.7 posterior**

## Updated framing

**Old (T78):** "σ_DM-nucleon is suppressed by ~70 orders of magnitude"
**New (T79):** "σ_DM-nucleon is suppressed by **~50-80 orders of magnitude**"

The qualitative claim (LZ cannot bite this model at any reasonable
discovery significance) is robust. The exact quantitative figure is
approximate.

## Form factor at LZ energies

| E_R | F²_gaussian | F²_dipole |
|---|---|---|
| 1 keV | 0.9997 | 0.9994 |
| 10 keV | 0.9971 | 0.9942 |
| 50 keV | 0.9855 | 0.9715 |
| 248 keV (LZ event) | **0.9303** | **0.8699** |

Composite DM (Λ ~ m_ρ ~ 30 MeV) is "compact" at LZ energy scale, so
form factor is small. Dominant suppression is still ε².

## Relic-density consistency

ε ~ 10⁻³⁷ is in the **freeze-in regime** (29 orders below "secluded"
threshold of 10⁻⁸). Production rate:

Γ ~ ε² × m_ρ × T_RH³ / M_Pl

For ε ~ 10⁻³⁷: requires T_RH > 10¹⁵ GeV or non-standard cosmology.
**Consistent with v0.7 posterior** (caveat: T41 does not include
relic-density as a channel).

---

## Layman Summary (T77, refined in T78 + T79)
{LAYMAN}

---

## T79 Technical Reference
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

    pdf_path = OUT / "t79_composite_form_factor_wrap_up.pdf"
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
zip_path = OUT / "t79_composite_form_factor_ship_bundle.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "t79_composite_form_factor_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "t79_composite_form_factor_wrap_up.pdf")
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T79_COMPOSITE_FORM_FACTOR_REMNANT.md",
        "T79_COMPOSITE_FORM_FACTOR_REMNANT.md",
    )
    zf.write(
        REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
        "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
    )
    zf.write(
        REPO / "scripts" / "t79_composite_form_factor.py",
        "t79_composite_form_factor.py",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_t79_composite_form_factor.json",
        "2026-09-02_t79_composite_form_factor.json",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")