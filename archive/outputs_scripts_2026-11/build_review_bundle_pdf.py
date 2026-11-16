"""
Build review bundle PDF containing all front-facing docs.
For sidm-composite-dm-mediator publication review (2026-08-14).

Inputs (all from project root C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/):
- README.md
- CITATION.cff
- CONTRIBUTING.md
- LICENSE
- docs/DATA_SOURCES.md
- docs/MATHEMATICS.md
- docs/TUTORIAL.md
- docs/findings_2026_SIDM_papers.md
- v0.3-prelim/docs/FINDINGS.md  (truncated to first 60 + last 30 lines for size)

Output:
- outputs/sidm-composite-dm-mediator_REVIEW_BUNDLE_2026-08-14.pdf

Run on WSL with the canonical venv:
  wsl -e bash -c "/home/lamkuenai/wimpy/bin/python outputs/build_review_bundle_pdf.py"
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Preformatted,
    KeepTogether,
)
import re


# --- Configuration ---------------------------------------------------------

ROOT = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator")
OUT_PDF = ROOT / "outputs" / "sidm-composite-dm-mediator_REVIEW_BUNDLE_2026-08-14.pdf"

# (label, path, truncate_to_first_N_or_None)
SECTIONS = [
    ("README.md", ROOT / "README.md", None),
    ("CONTRIBUTING.md", ROOT / "CONTRIBUTING.md", None),
    ("CITATION.cff", ROOT / "CITATION.cff", None),
    ("LICENSE", ROOT / "LICENSE", None),
    ("docs/DATA_SOURCES.md", ROOT / "docs" / "DATA_SOURCES.md", None),
    ("docs/MATHEMATICS.md", ROOT / "docs" / "MATHEMATICS.md", None),
    ("docs/TUTORIAL.md", ROOT / "docs" / "TUTORIAL.md", None),
    ("docs/findings_2026_SIDM_papers.md", ROOT / "docs" / "findings_2026_SIDM_papers.md", None),
    # FINDINGS.md is 542 lines / 35 KB; truncate to header + tier-1+2+3 + summary tail
    ("v0.3-prelim/docs/FINDINGS.md (excerpts)", ROOT / "v0.3-prelim" / "docs" / "FINDINGS.md", "excerpt"),
    ("docs/REVIEWER_AUDIT_R9.md (NEW 2026-08-14)", ROOT / "docs" / "REVIEWER_AUDIT_R9.md", None),
]


# --- Styles -----------------------------------------------------------------

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "title", parent=styles["Heading1"],
    fontSize=20, leading=24, spaceAfter=12, alignment=1,  # center
    textColor=HexColor("#1a1a6e"),
)
subtitle_style = ParagraphStyle(
    "subtitle", parent=styles["Heading2"],
    fontSize=13, leading=16, alignment=1, spaceAfter=10,
    textColor=HexColor("#444466"),
)
cover_meta = ParagraphStyle(
    "cover_meta", parent=styles["BodyText"],
    fontSize=10, leading=14, alignment=1, spaceAfter=4,
)
toc_heading = ParagraphStyle(
    "toc_heading", parent=styles["Heading2"],
    fontSize=14, leading=18, spaceAfter=10,
    textColor=HexColor("#1a1a6e"),
)
toc_item = ParagraphStyle(
    "toc_item", parent=styles["BodyText"],
    fontSize=11, leading=15, leftIndent=20, spaceAfter=3,
)
section_label = ParagraphStyle(
    "section_label", parent=styles["Heading1"],
    fontSize=18, leading=22, spaceAfter=8,
    textColor=HexColor("#1a1a6e"),
    borderPadding=4, borderWidth=0,
)
section_path = ParagraphStyle(
    "section_path", parent=styles["BodyText"],
    fontSize=9, leading=11, spaceAfter=8,
    textColor=HexColor("#666666"),
    fontName="Courier",
)
h1 = ParagraphStyle(
    "h1", parent=styles["Heading1"],
    fontSize=14, leading=18, spaceAfter=8,
    textColor=HexColor("#1a1a6e"),
)
h2 = ParagraphStyle(
    "h2", parent=styles["Heading2"],
    fontSize=12, leading=15, spaceAfter=6,
    textColor=HexColor("#2a2a8e"),
)
h3 = ParagraphStyle(
    "h3", parent=styles["Heading3"],
    fontSize=11, leading=14, spaceAfter=4,
    textColor=HexColor("#444466"),
)
body = ParagraphStyle(
    "body", parent=styles["BodyText"],
    fontSize=9, leading=12, spaceAfter=5, alignment=4,  # justified
)
list_item = ParagraphStyle(
    "list_item", parent=body,
    leftIndent=14, bulletIndent=4, spaceAfter=2,
)
code_block = ParagraphStyle(
    "code_block", parent=styles["Code"],
    fontName="Courier", fontSize=8, leading=10,
    leftIndent=10, rightIndent=10,
    backColor=HexColor("#f5f5f5"),
    borderColor=HexColor("#cccccc"),
    borderWidth=0.5, borderPadding=6,
    spaceBefore=4, spaceAfter=8,
)
note_style = ParagraphStyle(
    "note", parent=body,
    fontSize=8, leading=11,
    textColor=HexColor("#555555"),
    leftIndent=8, rightIndent=8,
    backColor=HexColor("#fff8dc"),
    borderColor=HexColor("#dddddd"),
    borderWidth=0.5, borderPadding=5,
    spaceAfter=5,
)


# --- Helpers ----------------------------------------------------------------

def _md_to_inline(text: str) -> str:
    """Convert simple markdown to ReportLab inline markup.

    Order matters: extract inline code first (and protect it from later
    bold/italic transforms that would mis-interpret the * / _ inside).
    """
    # Escape XML special chars
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    # 1. Extract inline code `text` into placeholders that later transforms
    #    won't touch. Use a unique sentinel that survives bold/italic passes.
    code_segments = []

    def _stash_code(m):
        idx = len(code_segments)
        code_segments.append(m.group(1))
        return f"\x00CODE{idx}\x00"

    text = re.sub(r"`([^`]+)`", _stash_code, text)

    # 2. Bold **text** -> <b>text</b>
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)

    # 3. Italic *text* -> <i>text</i>. Use word-boundary-like guards so that
    #    we don't match across lines or inside the now-empty placeholders.
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", text)

    # 4. Restore inline code as <font face="Courier">...</font>
    def _restore_code(m):
        idx = int(m.group(1))
        return f'<font face="Courier">{code_segments[idx]}</font>'

    text = re.sub(r"\x00CODE(\d+)\x00", _restore_code, text)

    # 5. Links: [text](url) -> text (url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<font color="#0066cc">\1</font> (\2)',
        text,
    )

    return text


def render_markdown(md_text: str, flow: list) -> None:
    """Render a markdown string into reportlab flowables."""
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flow.append(Spacer(1, 3))
            i += 1
            continue

        # Code block (```...```)
        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].rstrip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            block = "\n".join(code_lines).rstrip()
            if block:
                flow.append(Preformatted(block, code_block))
            continue

        # Heading levels
        if stripped.startswith("### "):
            flow.append(Paragraph(_md_to_inline(stripped[4:]), h3))
            i += 1
            continue
        if stripped.startswith("## "):
            flow.append(Paragraph(_md_to_inline(stripped[3:]), h2))
            i += 1
            continue
        if stripped.startswith("# "):
            flow.append(Paragraph(_md_to_inline(stripped[2:]), h1))
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            flow.append(Spacer(1, 8))
            i += 1
            continue

        # Blockquote (> ...)
        if stripped.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].rstrip().startswith("> "):
                quote_lines.append(lines[i].rstrip()[2:])
                i += 1
            flow.append(Paragraph(_md_to_inline(" ".join(quote_lines)), note_style))
            continue

        # Lists (numbered or bulleted)
        m_num = re.match(r"^(\d+)\.\s+(.*)", stripped)
        m_bul = re.match(r"^[-*]\s+(.*)", stripped)
        if m_num or m_bul:
            items = []
            while i < len(lines):
                s = lines[i].rstrip().strip()
                m_n = re.match(r"^(\d+)\.\s+(.*)", s)
                m_b = re.match(r"^[-*]\s+(.*)", s)
                if m_n:
                    items.append((str(m_n.group(1)) + ".", m_n.group(2)))
                    i += 1
                elif m_b:
                    items.append(("•", m_b.group(1)))
                    i += 1
                else:
                    break
            for marker, content in items:
                flow.append(Paragraph(_md_to_inline(f"{marker} {content}"), list_item))
            continue

        # Tables (simple markdown tables with | separators)
        if "|" in stripped and i + 1 < len(lines) and re.search(r"\|\s*-+", lines[i + 1]):
            tbl_lines = [stripped]
            j = i + 1
            # collect until non-table line
            while j < len(lines) and "|" in lines[j]:
                tbl_lines.append(lines[j].rstrip())
                j += 1
            i = j
            # parse table
            rows = [re.split(r"\s*\|\s*", t.strip().strip("|")) for t in tbl_lines]
            if len(rows) >= 2 and all(len(r) == len(rows[0]) for r in rows):
                from reportlab.platypus import Table, TableStyle
                data = [[Paragraph(_md_to_inline(c), body) for c in r] for r in rows]
                # header bold
                header_style = ParagraphStyle("tbl_header", parent=body, fontName="Helvetica-Bold")
                data[0] = [Paragraph(_md_to_inline(c), header_style) for c in rows[0]]
                # skip alignment row (rows[1])
                data = data[:1] + data[2:]
                col_w = min(180 / max(1, len(rows[0])), 50) * mm
                t = Table(
                    data,
                    colWidths=[col_w] * len(rows[0]),
                    repeatRows=1,
                )
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#dddddd")),
                    ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#888888")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]))
                flow.append(t)
                flow.append(Spacer(1, 4))
            continue

        # Regular paragraph (collect until blank/list/heading)
        para_lines = [line]
        i += 1
        while i < len(lines):
            s = lines[i].rstrip()
            ss = s.strip()
            if not ss:
                break
            if (
                ss.startswith("#")
                or ss.startswith(">")
                or re.match(r"^[-*]\s+", ss)
                or re.match(r"^\d+\.\s+", ss)
                or ss == "---"
                or ss.startswith("```")
                or ("|" in ss and i + 1 < len(lines) and re.search(r"\|\s*-+", lines[i + 1]))
            ):
                break
            para_lines.append(s)
            i += 1
        text = " ".join(para_lines).strip()
        if text:
            flow.append(Paragraph(_md_to_inline(text), body))


def truncate_findings(md_text: str) -> str:
    """Truncate FINDINGS.md to: header + TIER 1+2+3 block + S.6 + S.7 tail."""
    lines = md_text.split("\n")
    keep_indices = []
    # Always keep first 16 lines (header)
    keep_indices.extend(range(0, min(16, len(lines))))
    # Keep the TIER 1+2+3 section (lines 14-55) — name-based detection
    in_tier123 = False
    s6_seen = False
    for idx, line in enumerate(lines):
        if idx < 16:
            continue
        if "TIER 1+2+3" in line:
            in_tier123 = True
        if "TIER 2.5" in line:
            in_tier123 = False
        if in_tier123:
            keep_indices.append(idx)
        if "S.6 Per-galaxy SPARC fits" in line:
            s6_seen = True
            keep_indices.extend(range(idx, min(idx + 15, len(lines))))
        if "S.7 Total systematic budget" in line:
            keep_indices.extend(range(idx, min(idx + 20, len(lines))))
    # Dedupe and sort
    keep_indices = sorted(set(keep_indices))
    out_lines = []
    last_idx = -2
    for idx in keep_indices:
        if idx > last_idx + 1:
            out_lines.append(f"\n... [lines {last_idx+2}–{idx-1} elided for PDF brevity; see CHANGELOG.md for full v0.3-prelim-D8 record] ...\n")
        out_lines.append(lines[idx])
        last_idx = idx
    if last_idx < len(lines) - 1:
        out_lines.append(f"\n... [lines {last_idx+2}–{len(lines)} elided] ...\n")
    return "\n".join(out_lines)


# --- Build ------------------------------------------------------------------

flow = []

# Cover page
flow.append(Spacer(1, 60))
flow.append(Paragraph("sidm-composite-dm-mediator", title_style))
flow.append(Paragraph(
    "Documentation Review Bundle", subtitle_style,
))
flow.append(Spacer(1, 30))
flow.append(Paragraph("Review date: 2026-08-14", cover_meta))
flow.append(Paragraph("Project version: v0.3-prelim-D15-CORRECTED3 + Mediator_Detection_v12", cover_meta))
flow.append(Paragraph("Author: K. Lam", cover_meta))
flow.append(Paragraph("License: MIT", cover_meta))
flow.append(Paragraph("Repository: github.com/lamkuenai/sidm-composite-dm-mediator", cover_meta))
flow.append(Spacer(1, 30))
flow.append(Paragraph(
    "<b>Contents</b>", toc_heading,
))
for label, path, trunc in SECTIONS:
    flow.append(Paragraph(
        f"• <b>{label}</b>  <i>({path.relative_to(ROOT)})</i>",
        toc_item,
    ))
flow.append(PageBreak())

# Body sections
for label, path, trunc in SECTIONS:
    if not path.exists():
        flow.append(Paragraph(f"<b>{label}</b>", section_label))
        flow.append(Paragraph(f"<i>File not found: {path}</i>", body))
        flow.append(PageBreak())
        continue

    text = path.read_text(encoding="utf-8")
    if trunc == "excerpt":
        text = truncate_findings(text)

    flow.append(Paragraph(label, section_label))
    flow.append(Paragraph(str(path.relative_to(ROOT)), section_path))
    flow.append(Spacer(1, 4))

    render_markdown(text, flow)

    flow.append(PageBreak())

# Build
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(OUT_PDF),
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=18 * mm,
    title="sidm-composite-dm-mediator — Documentation Review Bundle",
    author="K. Lam",
    subject="Pre-publication review of README + supporting docs (2026-08-14)",
)
doc.build(flow)

size_kb = OUT_PDF.stat().st_size / 1024
print(f"PDF -> {OUT_PDF}")
print(f"Size: {size_kb:.1f} KB ({size_kb/1024:.2f} MB)")
print(f"Pages (approx): {size_kb // 6:.0f}")  # rough estimate
