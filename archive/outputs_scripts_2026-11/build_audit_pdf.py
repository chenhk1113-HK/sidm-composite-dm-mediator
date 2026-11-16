"""Build audit-only PDF for sidm-composite-dm-mediator review9 audit.

Standalone build (separate from build_review_bundle_pdf.py because that
script hangs in some import paths).
"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator")
OUT = ROOT / "outputs" / "REVIEWER_AUDIT_R9_2026-08-14.pdf"
SRC = ROOT / "docs" / "REVIEWER_AUDIT_R9.md"

styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Heading1"], fontSize=18, leading=22, alignment=1, textColor=HexColor("#1a1a6e"), spaceAfter=8)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, leading=18, textColor=HexColor("#1a1a6e"), spaceAfter=6)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, leading=15, textColor=HexColor("#2a2a8e"), spaceAfter=4)
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=4)
code = ParagraphStyle("code", parent=styles["Code"], fontName="Courier", fontSize=8, leading=10, backColor=HexColor("#f5f5f5"), borderColor=HexColor("#cccccc"), borderWidth=0.5, borderPadding=5, leftIndent=10, rightIndent=10)

import re

def md_to_inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    code_segs = []
    def stash(m):
        idx = len(code_segs)
        code_segs.append(m.group(1))
        return f"\x00CODE{idx}\x00"
    text = re.sub(r"`([^`]+)`", stash, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", text)
    def restore(m):
        return f'<font face="Courier">{code_segs[int(m.group(1))]}</font>'
    text = re.sub(r"\x00CODE(\d+)\x00", restore, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<font color="#0066cc">\1</font>', text)
    return text

flow = [Paragraph("REVIEWER AUDIT — Full Review 9.docx", title)]
flow.append(Paragraph("sidm-composite-dm-mediator", h2))
flow.append(Paragraph("Audit date: 2026-08-14", body))
flow.append(Spacer(1, 8))

text = SRC.read_text(encoding="utf-8")
lines = text.split("\n")

i = 0
while i < len(lines):
    line = lines[i].rstrip()
    s = line.strip()
    if not s:
        flow.append(Spacer(1, 3))
        i += 1
        continue
    if s.startswith("### "):
        flow.append(Paragraph(md_to_inline(s[4:]), h2))
    elif s.startswith("## "):
        flow.append(Paragraph(md_to_inline(s[3:]), h1))
    elif s.startswith("# "):
        flow.append(Paragraph(md_to_inline(s[2:]), title))
    elif s == "---":
        flow.append(Spacer(1, 6))
    elif s.startswith("> "):
        flow.append(Paragraph(md_to_inline(s[2:]), body))
    elif re.match(r"^[-*]\s+", s):
        flow.append(Paragraph(md_to_inline("• " + s[2:]), body))
    elif re.match(r"^\d+\.\s+", s):
        flow.append(Paragraph(md_to_inline(s), body))
    elif s.startswith("```"):
        i += 1
        code_lines = []
        while i < len(lines) and not lines[i].rstrip().startswith("```"):
            code_lines.append(lines[i])
            i += 1
        from reportlab.platypus import Preformatted
        flow.append(Preformatted("\n".join(code_lines), code))
    else:
        flow.append(Paragraph(md_to_inline(s), body))
    i += 1

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm,
                        title="REVIEWER AUDIT — Full Review 9", author="K. Lam")
doc.build(flow)
print(f"PDF -> {OUT}")
print(f"Size: {OUT.stat().st_size/1024:.1f} KB")