"""Build the T81 (LZ review response + Channel 19) Telegram bundle."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OUT = Path(tempfile.gettempdir()) / "t81_telegram_bundle"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


TECH = read(REPO / "v0.3-prelim" / "docs" / "T81_LZ_REVIEW_RESPONSE.md")

# Consolidated wrap-up MD
wrap_md = OUT / "t81_lz_review_response_wrap_up.md"
wrap_md.write_text(
    f"""# T81 — LZ Review Response + Channel 19 (v0.4-prelim)
> Telegram wrap-up, 2026-09-02. Shipped in commit `6a0ee59`.

## Headline

The `LZ1.docx` review identified 5 specific recommendations. T81
addresses all 5:

1. **"Cross-validation" → "compatibility"** (rec #1) — softened in README, T77, T80
2. **"σ/m survives all scenarios" → "σ/m unchanged at current LZ precision"** (rec #2) — softened in layman + EXTRACT
3. **T79 (composite form factor) completed** (rec #3) — F²(q) at LZ energies documented (F² ≈ 0.93 at 248 keV)
4. **LSS phenomenological status prominent** (rec #4) — added prominent note in T74 docs
5. **XENONnT + PandaX-4T watch registered** (rec #5) — **Channel 19** added

## Channel 19: XENONnT + PandaX-4T direct-detection competitor watch

Per reviewer rec #5: "If either sees a consistent high-energy event in
the same 200-270 keV window, the case strengthens dramatically."

**Implementation:**
- `XENONNT_2025_LIMITS` (arXiv:2502.18005, PRL 135, 221003) — 7 mass points, 1.7e-47 cm² minimum at 30 GeV
- `PANDAX4T_2025_LIMITS` (arXiv:2408.00664, PRL 134, 011805) — 7 mass points, ~3e-47 cm² minimum at 40 GeV
- Helper functions: `sigma_XENONnT_2025_limit`, `sigma_PandaX4T_2025_limit`, `is_excluded_by_XENONnT_or_PandaX`, `loglike_competitor_dd_watch`
- Wired into T41 joint fit with `T81_COMPETITOR_DD_DISABLE=1` env-var gate
- Marked as "experimental — NOT in primary production" in CHANNEL_STATUS
- **13 new tests** (all passing)

**At v0.7 MAP:** predicted σ_DM-nuc ~10⁻¹¹⁷ cm² (Kahlhoefer formula) is
~10⁻⁷¹ below both XENONnT and PandaX-4T limits (~3e-46). Channel 19
contributes 0 to the log-likelihood — same kinetic-mixing suppression
as LZ applies to all three direct-detection experiments.

## Test count

- **Before T81:** 472 passed, 7 skipped
- **After T81:** **504 passed, 6 skipped** (+32 new tests)

## Standing-version impact

**No version bump.** T81 is refinement + Channel 19 addition.
Standing version: `v0.4-prelim+T75`.

---

## T81 Technical Reference
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

    pdf_path = OUT / "t81_lz_review_response_wrap_up.pdf"
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
zip_path = OUT / "t81_lz_review_response_ship_bundle.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(wrap_md, "t81_lz_review_response_wrap_up.md")
    if pdf_path and pdf_path.exists():
        zf.write(pdf_path, "t81_lz_review_response_wrap_up.pdf")
    zf.write(
        REPO / "v0.3-prelim" / "docs" / "T81_LZ_REVIEW_RESPONSE.md",
        "T81_LZ_REVIEW_RESPONSE.md",
    )
    zf.write(
        REPO / "v0.3-prelim" / "tests" / "test_channel_19_competitor_dd.py",
        "test_channel_19_competitor_dd.py",
    )
print(f"[3/3] wrote {zip_path} ({zip_path.stat().st_size} B)")

print(f"\nBundle: {OUT}")
for p in OUT.iterdir():
    print(f"  {p.name}: {p.stat().st_size} B")