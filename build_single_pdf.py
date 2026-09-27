"""Single-file PDF builder — extract one source file as a stand-alone PDF."""
import io
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted


def build_single_file_pdf(source_path: Path, output_path: Path, title: str):
    """Render a single source file as a monospace PDF."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='MonoCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=black,
        wordWrap='CJK',
    ))
    styles.add(ParagraphStyle(
        name='Meta',
        parent=styles['Normal'],
        fontSize=8,
        textColor=grey,
    ))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=title,
    )

    content = source_path.read_text(encoding='utf-8', errors='replace')
    safe = (content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

    story = [
        Paragraph(f'<font size="16"><b>{title}</b></font>', styles['Title']),
        Spacer(1, 0.2 * inch),
        Paragraph(
            f'<b>Source:</b> {source_path}<br/>'
            f'<b>Size:</b> {source_path.stat().st_size:,} bytes, '
            f'<b>Lines:</b> {content.count(chr(10))+1:,}<br/>'
            f'<b>Generated:</b> 2026-09-23',
            styles['Meta']
        ),
        Spacer(1, 0.3 * inch),
        Preformatted(safe, styles['MonoCode']),
    ]
    doc.build(story)
    print(f'PDF: {output_path} ({output_path.stat().st_size:,} bytes)')


if __name__ == '__main__':
    src = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code\T199_corrected_lz_analysis.py')
    out = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\outputs\T199_corrected_lz_analysis.pdf')
    out.parent.mkdir(parents=True, exist_ok=True)
    build_single_file_pdf(src, out, 'T199_corrected_lz_analysis.py')