"""
T237 (D-17): PDF build for PAPER_V1_DRAFT.md (using fpdf2)

Per R85 reviewer's standing rule:
- Use 10^-N (not unicode superscript) for cross-render fidelity
- No TTS (timed out twice)
"""
import sys
from pathlib import Path

from fpdf import FPDF


PAPER_PATH = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\docs\PAPER_V1_DRAFT.md")
PDF_PATH = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\docs\PAPER_V19_2_D_R88.pdf")


# Unicode superscript to ASCII replacement
SUPERSCRIPTS = {
    "⁻": "^-",
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
}


def convert_unicode_superscripts(text):
    """Convert unicode superscripts to ASCII notation."""
    for u, a in SUPERSCRIPTS.items():
        text = text.replace(u, a)
    return text


def clean_for_fpdf(text):
    """Clean text for fpdf (latin-1 only)."""
    text = convert_unicode_superscripts(text)
    text = text.encode('latin-1', 'replace').decode('latin-1')
    return text


def main():
    md_text = PAPER_PATH.read_text()
    md_text = convert_unicode_superscripts(md_text)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Helvetica", size=9)

    lines = md_text.split('\n')
    for line in lines:
        cleaned = clean_for_fpdf(line)

        if cleaned.startswith('# '):
            pdf.set_font("Helvetica", "B", size=12)
            pdf.multi_cell(0, 6, cleaned[2:])
            pdf.set_font("Helvetica", size=9)
            pdf.ln(2)
        elif cleaned.startswith('## '):
            pdf.set_font("Helvetica", "B", size=11)
            pdf.multi_cell(0, 6, cleaned[3:])
            pdf.set_font("Helvetica", size=9)
            pdf.ln(1)
        elif cleaned.startswith('### '):
            pdf.set_font("Helvetica", "B", size=10)
            pdf.multi_cell(0, 5, cleaned[4:])
            pdf.set_font("Helvetica", size=9)
            pdf.ln(1)
        elif cleaned.startswith('|'):
            pdf.set_font("Courier", size=7)
            pdf.multi_cell(0, 4, cleaned)
            pdf.set_font("Helvetica", size=9)
            pdf.ln(1)
        elif cleaned.strip() == '---':
            pdf.ln(2)
        elif cleaned.strip():
            text = cleaned.replace('**', '').replace('*', '').replace('`', '')
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