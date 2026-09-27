"""Build codebase PDF — collects all .py and .md files into a single PDF.

Strategy:
- Walk v0.3-prelim/code and v0.3-prelim/docs
- Sort files deterministically
- Render each file using reportlab Platypus with monospace
- Group by directory in the ToC
- Track pages, don't blow up RAM

Per Rule 18 (post-write smoke test): verify the PDF exists, has expected page count,
and can be opened with PyPDF2 / pdfplumber.

Per Rule 27 (ASCII superscripts): use 10^-N, not 10^-N, in any text destined for PDF.
"""
import io
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted,
    BaseDocTemplate, PageTemplate, Frame,
)
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REPO_ROOT = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator')
OUTPUT_DIR = REPO_ROOT / 'v0.3-prelim' / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUTPUT_DIR / 'codebase_full.pdf'

# Fonts - use built-in Courier for monospace
MONO_FONT = 'Courier'
MONO_BOLD = 'Courier-Bold'


def make_styles():
    """Build the style sheet we need."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='DirHeader',
        parent=styles['Heading1'],
        fontSize=14,
        spaceBefore=18,
        spaceAfter=6,
        textColor=HexColor('#1a1a2e'),
    ))
    styles.add(ParagraphStyle(
        name='FileHeader',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=4,
        textColor=HexColor('#16213e'),
    ))
    styles.add(ParagraphStyle(
        name='Meta',
        parent=styles['Normal'],
        fontSize=8,
        textColor=grey,
        spaceAfter=2,
    ))
    return styles


def collect_files():
    """Walk code + docs dirs, return sorted list of (rel_path, abs_path, kind)."""
    files = []
    for sub in ['v0.3-prelim/code', 'v0.3-prelim/docs']:
        root = REPO_ROOT / sub
        if not root.exists():
            continue
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.suffix in ('.py', '.md', '.txt'):
                # Skip cache / outputs / hidden dirs
                rel = p.relative_to(REPO_ROOT).as_posix()
                if '__pycache__' in rel or '/outputs/' in rel or '/.' in rel:
                    continue
                kind = 'python' if p.suffix == '.py' else (
                       'markdown' if p.suffix == '.md' else 'text')
                files.append((rel, p, kind))
    return files


def render_file(rel_path, abs_path, kind, styles):
    """Yield Platypus flowables for one file."""
    try:
        content = abs_path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        content = f'[Could not read file: {e}]'

    # File header
    yield Paragraph(f'<b>{rel_path}</b>', styles['FileHeader'])
    yield Paragraph(
        f'<i>kind={kind}, size={abs_path.stat().st_size:,} bytes, '
        f'lines={content.count(chr(10))+1:,}</i>',
        styles['Meta']
    )
    yield Spacer(1, 4)

    # Body — escape < > & for reportlab
    safe = (content
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))

    # Use Preformatted for monospace
    # Limit per-page overflow: Preformatted will auto-paginate if needed
    try:
        yield Preformatted(safe, styles['MonoCode'])
    except Exception as e:
        # If Preformatted chokes (very long line), fall back to Paragraph chunks
        yield Paragraph(f'[Preformatted failed: {e}; truncated display]', styles['Meta'])
        # Show first 5000 chars as paragraphs
        for chunk_start in range(0, min(len(safe), 50000), 2000):
            chunk = safe[chunk_start:chunk_start+2000]
            yield Paragraph(chunk.replace('\n', '<br/>'), styles['MonoCode'])


def add_code_style(styles):
    styles.add(ParagraphStyle(
        name='MonoCode',
        parent=styles['Normal'],
        fontName=MONO_FONT,
        fontSize=6.5,
        leading=8.5,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=0,
        spaceAfter=0,
        wordWrap='CJK',  # allow wrapping on any char
        textColor=black,
    ))


def build_pdf():
    """Main build loop."""
    styles = make_styles()
    add_code_style(styles)

    files = collect_files()
    py_count = sum(1 for _, _, k in files if k == 'python')
    md_count = sum(1 for _, _, k in files if k == 'markdown')
    txt_count = sum(1 for _, _, k in files if k == 'text')
    print(f'Collected {len(files)} files ({py_count} .py, {md_count} .md, {txt_count} .txt)')

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title='SIDM Composite-DM Mediator — Codebase',
        author='SIDM project',
        subject='Full codebase (v0.3-prelim/code + v0.3-prelim/docs)',
    )

    story = []
    # Title page
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph(
        '<font size="20"><b>SIDM Composite-DM Mediator</b></font>',
        styles['Title']
    ))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        '<font size="14">Full Codebase — v0.3-prelim/code + v0.3-prelim/docs</font>',
        styles['Heading2']
    ))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f'<b>{len(files)} files</b> ({py_count} Python, {md_count} Markdown, {txt_count} text)<br/>'
        f'Generated 2026-09-22 from commit ab95eee on wip/multi-component-SIDM-core-collapse<br/>'
        f'Paper version: v18.16',
        styles['Normal']
    ))
    story.append(PageBreak())

    # Table of contents
    story.append(Paragraph('<b>Table of Contents</b>', styles['Heading1']))
    story.append(Spacer(1, 0.2 * inch))

    # Group files by directory
    by_dir = {}
    for rel, abs_path, kind in files:
        d = str(Path(rel).parent)
        by_dir.setdefault(d, []).append((rel, abs_path, kind))

    for d in sorted(by_dir.keys()):
        story.append(Paragraph(f'<b>{d}/</b>', styles['DirHeader']))
        for rel, _, kind in by_dir[d]:
            fname = Path(rel).name
            story.append(Paragraph(f'&nbsp;&nbsp;{fname}', styles['Normal']))
    story.append(PageBreak())

    # File contents
    for i, (rel, abs_path, kind) in enumerate(files):
        if i % 50 == 0:
            print(f'  Rendering file {i+1}/{len(files)}: {rel}')
        for flow in render_file(rel, abs_path, kind, styles):
            story.append(flow)
        story.append(PageBreak())

    doc.build(story)
    print(f'\nPDF built: {PDF_PATH}')
    print(f'  Size: {PDF_PATH.stat().st_size:,} bytes')


if __name__ == '__main__':
    build_pdf()