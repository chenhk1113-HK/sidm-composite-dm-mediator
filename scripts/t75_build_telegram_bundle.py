"""Build the T75 v0.7 final Telegram bundle.

Combines:
- T75 docs (technical)
- T73 layman summary
- T74 technical doc
- v0.7 ablation JSON
- v0.7 raw results
into a single deliverable bundle.
"""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t75_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# 1) Build consolidated wrap-up MD
T73_LAYMAN = read(REPO / "docs" / "LAYMAN_SUMMARY_T73_DAMPE.md")
T74_TECH = read(REPO / "v0.3-prelim" / "docs" / "T74_LSS_ZHANG_2025.md")
T75_TECH = read(REPO / "v0.3-prelim" / "docs" / "T75_V07_FULL_T41_RERUN.md")
V07_ABLATION = read(
    REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_dampe_poc"
    / "t75_v07_ablation_summary.json"
)

consolidated = f"""# v0.4-prelim+T75 — DAMPE + Zhang+2025 LSS ship bundle
> Telegram wrap-up, 2026-09-02. Shipped across 3 commits: T73 (5b8fa8f), T74 (114465b), T75 (9c5b580).

## Headline (one paragraph)

Adding the DAMPE cosmic-ray electron+positron channel (Channel 17, T73)
and the Zhang+2025 large-scale-structure / assembly-bias channel
(Channel 18, T74) to the T41 joint fit produces a **major posterior
shift** in v0.7 vs v0.6. The MAP moves toward heavier dark matter
(m_chi: 364 → 957 GeV, +162%) and a higher self-interaction cross-
section (σ/m: 0.06 → 0.24 cm²/g, +303%). **The velocity-slope
tension between the Yukawa prediction (a ≈ 0.03) and the data-preferred
T39 value (a ≈ 0.94) drops from 0.91 to 0.70** — below the 1.0
"no tension" threshold. The Bayesian evidence increases by +52 log-
units (log Z: -215 → -163). DAMPE alone (+84 log Z) is the primary
tension-resolver; LSS alone (+72 log Z, 4× σ/m shift) is the primary
σ/m-shifter.

## Standing-version bump

`v0.3-prelim+T71.7` → **`v0.4-prelim+T75`** (Tier-1 milestone).
Drift guard: VERSION, README badge, CITATION.cff, CHANGELOG.md all agree.

---

## T73 layman summary (already shipped to Telegram)
{T73_LAYMAN}

---

## T74 technical reference (excerpt)
{T74_TECH}

---

## T75 technical reference (excerpt)
{T75_TECH}

---

## v0.7 ablation summary
```json
{V07_ABLATION}
```
"""

wrap_md = OUT / "v0_4_prelim_t75_wrap_up.md"
wrap_md.write_text(consolidated, encoding="utf-8")
print(f"[1/3] wrote {wrap_md} ({wrap_md.stat().st_size} B)")

# 2) Build PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    pdf_path = OUT / "v0_4_prelim_t75_wrap_up.pdf"
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

# 3) ZIP
zip_path = OUT / "v0_4_prelim_t75_ship_bundle.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "v0_4_prelim_t75_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "v0_4_prelim_t75_wrap_up.pdf")
    zf.write(REPO / "v0.3-prelim" / "docs" / "T75_V07_FULL_T41_RERUN.md", "T75_V07_FULL_T41_RERUN.md")
    zf.write(REPO / "v0.3-prelim" / "docs" / "T74_LSS_ZHANG_2025.md", "T74_LSS_ZHANG_2025.md")
    zf.write(REPO / "docs" / "LAYMAN_SUMMARY_T73_DAMPE.md", "LAYMAN_SUMMARY_T73_DAMPE.md")
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_dampe_poc"
        / "t75_v07_ablation_summary.json",
        "t75_v07_ablation_summary.json",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results"
        / "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive500.json",
        "t41_v07_with_dampe_lss.json",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results"
        / "t41_mediator_mass_joint_fit_v0_7_dampe_only_nlive500.json",
        "t41_v07_dampe_only.json",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results"
        / "t41_mediator_mass_joint_fit_v0_7_lss_only_nlive500.json",
        "t41_v07_lss_only.json",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle directory: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")