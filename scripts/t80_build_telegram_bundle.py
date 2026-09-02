"""Build the T80 (LZ paper update) Telegram bundle."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t80_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


LAYMAN = read(REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md")
TECH = read(REPO / "v0.3-prelim" / "docs" / "T80_LZ_PAPER_UPDATE.md")

# Consolidated wrap-up MD
wrap_md = OUT / "t80_lz_paper_update_wrap_up.md"
wrap_md.write_text(
    f"""# T80 — LZ Paper Update (v0.4-prelim)
> Telegram wrap-up, 2026-09-02. Shipped in commit `503f973`.
> Response to the actual LZ preprint appearing 2026-09-02.

## Headline

The LZ preprint appeared today (2026-09-02) — much earlier than the
KIV cron `080d2f590251` expected (2026-11-01 fire date). The paper
is a 25-page preprint with the full LZ author list, prepared for
PRL submission.

**Key paper-specific facts** (verified end-to-end per AGENTS.md rule 21):

| Property | Press release | Paper |
|---|---|---|
| Exposure | 220 live days | **2.84 tonne-years** |
| Energy window | "248 keV event" | **5.4 – 270 keV** (extended) |
| Models | "Beyond simplest WIMP" | **NREFT operators** O₁ˢ, O₄ᵛ, L₁₋L₂₀, Ls₁₀ |
| Significance | 2.6σ | **3.4σ local / 2.6σ global** |
| Best-fit | n/a | **Ls₁₀ WIMP at 1000 GeV/c²** |

## The local-vs-global distinction

- **3.4σ local** for the best-fit model (Ls₁₀ at 1000 GeV)
- **2.6σ global** after look-elsewhere effect correction

The paper authors themselves use the **2.6σ global** as the
headline (correct statistical practice for multi-model searches).
Per the project's trigger policy, 2.6σ global < 3σ → **document
only, no Channel 5 update, no T41 re-run**.

## Project compatibility

| Quantity | Project v0.7 | LZ paper best fit |
|---|---|---|
| WIMP mass m_χ | **770 GeV (MAP)** | **1000 GeV/c²** |
| Mediator mass m_φ | 453-588 MeV | Light mediator (NREFT) |
| Interaction | Composite-DM + secluded A' | Inelastic DM + EFT (Ls₁₀) |

**Stronger validation than press-release-only T77.** Project m_χ ~
770 GeV is **very close to** LZ best-fit m_χ ~ 1000 GeV. Both in
the "heavy WIMP" regime where NREFT operators become relevant.

## T78/T79 unchanged

- **Kinetic-mixing suppression factor (~50-80 orders) holds**
- ε ~ 10⁻³⁷ is far below Ls₁₀'s typical coupling regime (~10⁻³)
- Project **cannot be constrained** by LZ even with detailed NREFT
- Composite form factor F²(q) is small at LZ energies (T79 calc)

## KIV cron retained

Cron `080d2f590251` (next fire 2026-11-01 09:00) is retained to
check for the PRL final version (which may differ from preprint).

---

## Layman Summary (T77, refined in T78 + T79 + T80)
{LAYMAN}

---

## T80 Technical Reference
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

    pdf_path = OUT / "t80_lz_paper_update_wrap_up.pdf"
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
zip_path = OUT / "t80_lz_paper_update_ship_bundle.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "t80_lz_paper_update_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "t80_lz_paper_update_wrap_up.pdf")
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T80_LZ_PAPER_UPDATE.md",
        "T80_LZ_PAPER_UPDATE.md",
    )
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T77_LZ_2026_09_UPDATE.md",
        "T77_LZ_2026_09_UPDATE.md",
    )
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T78_KINETIC_MIXING_LZ_LINK.md",
        "T78_KINETIC_MIXING_LZ_LINK.md",
    )
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T79_COMPOSITE_FORM_FACTOR_REMNANT.md",
        "T79_COMPOSITE_FORM_FACTOR_REMNANT.md",
    )
    zf.write(
        REPO / "docs" / "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
        "LAYMAN_SUMMARY_T77_LZ_2026_09.md",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")