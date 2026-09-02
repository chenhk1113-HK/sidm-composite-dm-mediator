"""Build the T76 final Telegram bundle — closing the v0.4-prelim milestone."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t76_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# Read everything
T76 = read(REPO / "v0.3-prelim" / "docs" / "T76_V07_NLIVE2000.md")
T75 = read(REPO / "v0.3-prelim" / "docs" / "T75_V07_FULL_T41_RERUN.md")
ABLATION = read(
    REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_dampe_poc"
    / "t75_v07_ablation_summary.json"
)
V07_NL2000 = read(
    REPO / "v0.3-prelim" / "data" / "results"
    / "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json"
)

# Build consolidated MD
consolidated = f"""# T76 — v0.4-prelim FINAL milestone
> Telegram wrap-up, 2026-09-02. Shipped in commit `c3f98e3`.

## One-paragraph summary

The v0.4-prelim Tier-1 milestone is **complete**. Across 5 commits
(T72 POC, T73 wiring, T74 LSS, T75 rerun, T76 convergence check),
the project shipped the DAMPE cosmic-ray electron+positron channel
(Channel 17, T73) and the Zhang+2025 large-scale-structure /
assembly-bias channel (Channel 18, T74), wired both into the T41
nested-sampling joint fit, and verified the result at nlive=2000
in 7.3 minutes wall time. The headline finding: **adding DAMPE +
LSS resolves the velocity-slope tension** that existed in v0.6
(T39 a vs Yukawa a: 0.91 → **0.60**, below the 1.0 "no tension"
threshold). Bayesian evidence increases by +52 log Z. Standing
version bumped from v0.3-prelim+T71.7 to **v0.4-prelim+T75**.

## Convergence check (nlive=2000 vs nlive=500)

| Metric | nlive=500 | nlive=2000 | Verdict |
|---|---|---|---|
| log Z | -163.24 ± 0.16 | **-163.29 ± 0.085** | ✅ Converged |
| MAP σ/m_0 (cm²/g) | 0.238 | **0.273** | ✅ Converged |
| Tension (T39 − Y) | 0.70 | **0.60** | ✅ **More robust** |
| Wall time | 97s | 440s | Linear in nlive |

## v0.7 ablation summary (T75)

| Config | log Z | Δ vs v0.6 | Tension |
|---|---|---|---|
| v0.6 baseline | -215.37 | — | 0.908 ⚠️ |
| DAMPE only | -131.49 | +83.89 | 0.673 ✅ |
| LSS only | -143.24 | +72.14 | 0.858 ⚠️ |
| **v0.7 combined** | **-163.24** | **+52.13** | **0.698 ✅** |

## Doc-prominence fix (T76)

- **§0 added** to `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`: orthogonal-
  physics posture (σ_DM-DM ≠ σ_DM-nucleon) as non-negotiable
  standing decision. Direct-detection constraints (LZ, XENONnT,
  PandaX) are **rejected** as σ/m measurements.
- **Top-of-doc callout** in `EXTRACT.md` pointing to §0 for full
  reasoning.

## Posterior visualizations

- `v0_7_map_comparison.png` (149 KB): MAP metrics bar chart across
  the 4 configurations (v0.6, DAMPE-only, LSS-only, v0.7 combined)
- `v0_7_logz_progression.png` (56 KB): Bayesian evidence
  progression with error bars + Δ vs v0.6 annotations
- `v0_7_tension_progression.png` (50 KB): velocity-slope tension
  resolution with the 1.0 threshold line

All plots in `v0.3-prelim/plots/`, matplotlib Agg backend, 150 DPI.

## Standing-version impact

| Source | Before T72 | Now |
|---|---|---|
| VERSION | v0.3-prelim+T71.7 | **v0.4-prelim+T75** |
| README badge | v0.3-prelim+T71.7 | **v0.4-prelim+T75** |
| CITATION.cff | v0.3-prelim+T71.7 | **v0.4-prelim+T75** |
| CHANGELOG.md | T71.7 top entry | **v0.4-prelim+T75** top entry |
| EXTRACT.md | v0.3-prelim+T71.7 | **v0.4-prelim+T75** |
| MODEL_ASSUMPTIONS.md | v0.3-prelim+T71.7 | **v0.4-prelim+T75** |

All 6 drift-guard sources agree. ✅

## Final project state

- **18 channels** (was 16 at v0.3-prelim)
- **472 tests passing** (was 446 at T73 ship)
- **Bayesian evidence log Z = -163.29 ± 0.085** (was -215.37 at v0.6)
- **Tension (T39 − Y a) = 0.60** (was 0.91 at v0.6, below 1.0 threshold)
- **MAP σ/m_0 = 0.27 cm²/g** (was 0.059 at v0.6; LSS is the primary shifter)
- **MAP m_chi = 770 GeV** at nlive=2000 (was 364 GeV at v0.6)

## Git commit chain (this session)

```
c3f98e3  T76 — nlive=2000 convergence + doc-prominence fix
9c5b580  T75 — v0.7 full T41 rerun with DAMPE + LSS
114465b  T74 — Zhang+2025 LSS / assembly-bias (Channel 18)
5b8fa8f  T73 layman — layman summary
1d40286  T73 — DAMPE CRE forward-model + joint-fit integration
5b75d02  T72 — DAMPE POC (data ingest)
```

All HEAD_MATCH verified on GitHub.

---

## T75 docs (full)

{T75}

---

## T76 docs (full)

{T76}

---

## v0.7 ablation summary JSON

```json
{ABLATION}
```

## v0.7 nlive=2000 result JSON

```json
{V07_NL2000}
```
"""

wrap_md = OUT / "t76_final_v0_4_prelim.md"
wrap_md.write_text(consolidated, encoding="utf-8")
print(f"[1/3] wrote {wrap_md} ({wrap_md.stat().st_size} B)")

# PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    pdf_path = OUT / "t76_final_v0_4_prelim.pdf"
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
zip_path = OUT / "t76_final_v0_4_prelim.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "t76_final_v0_4_prelim.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "t76_final_v0_4_prelim.pdf")
    zf.write(REPO / "v0.3-prelim" / "docs" / "T76_V07_NLIVE2000.md", "T76_V07_NLIVE2000.md")
    zf.write(REPO / "v0.3-prelim" / "docs" / "T75_V07_FULL_T41_RERUN.md", "T75_V07_FULL_T41_RERUN.md")
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results"
        / "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json",
        "t41_v07_nlive2000.json",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results"
        / "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive500.json",
        "t41_v07_nlive500.json",
    )
    zf.write(
        REPO / "v0.3-prelim" / "data" / "results" / "2026-09-02_dampe_poc"
        / "t75_v07_ablation_summary.json",
        "t75_v07_ablation_summary.json",
    )
    zf.write(REPO / "v0.3-prelim" / "plots" / "v0_7_map_comparison.png", "v0_7_map_comparison.png")
    zf.write(REPO / "v0.3-prelim" / "plots" / "v0_7_logz_progression.png", "v0_7_logz_progression.png")
    zf.write(REPO / "v0.3-prelim" / "plots" / "v0_7_tension_progression.png", "v0_7_tension_progression.png")
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")