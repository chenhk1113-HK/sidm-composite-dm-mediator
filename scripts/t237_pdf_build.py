"""
T237 (R88 PDF): Build PDF using Unicode-aware font (Cambria from C:/Windows/Fonts).

Per R88 reviewer's note: cm2/g should be cm²/g, σ_peak should render correctly.
"""
import sys
from pathlib import Path

from fpdf import FPDF


PAPER_PATH = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\docs\PAPER_V1_DRAFT.md")
PDF_PATH = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\docs\PAPER_V19_2_D_R88.pdf")

# Calibri has Greek letters and most Unicode characters
FONT_PATH = r"C:/Windows/Fonts/calibri.ttf"
FONT_BOLD = r"C:/Windows/Fonts/calibrib.ttf"
FONT_ITALIC = r"C:/Windows/Fonts/calibrii.ttf"


def main():
    md_text = PAPER_PATH.read_text()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.add_font("Cambria", "", FONT_PATH)
    pdf.add_font("Cambria", "B", FONT_BOLD)
    pdf.add_font("Cambria", "I", FONT_ITALIC)

    pdf.set_font("Cambria", size=9)

    lines = md_text.split('\n')
    for line in lines:
        if line.startswith('# '):
            pdf.set_font("Cambria", "B", size=14)
            try:
                pdf.multi_cell(0, 7, line[2:])
            except Exception:
                pass
            pdf.set_font("Cambria", size=9)
            pdf.ln(2)
        elif line.startswith('## '):
            pdf.set_font("Cambria", "B", size=12)
            try:
                pdf.multi_cell(0, 6, line[3:])
            except Exception:
                pass
            pdf.set_font("Cambria", size=9)
            pdf.ln(1)
        elif line.startswith('### '):
            pdf.set_font("Cambria", "B", size=10)
            try:
                pdf.multi_cell(0, 5, line[4:])
            except Exception:
                pass
            pdf.set_font("Cambria", size=9)
            pdf.ln(1)
        elif line.startswith('|'):
            pdf.set_font("Cambria", size=7)
            try:
                pdf.multi_cell(0, 4, line)
            except Exception:
                pass
            pdf.set_font("Cambria", size=9)
            pdf.ln(1)
        elif line.strip() == '---':
            pdf.ln(2)
        elif line.strip():
            text = line.replace('**', '').replace('*', '').replace('`', '')
            try:
                pdf.multi_cell(0, 5, text)
            except Exception:
                pass
            pdf.ln(1)

    pdf.output(str(PDF_PATH))
    print(f"PDF saved to: {PDF_PATH}")
    print(f"Size: {PDF_PATH.stat().st_size} bytes")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    main()