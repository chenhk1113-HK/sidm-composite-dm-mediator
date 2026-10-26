#!/usr/bin/env python3
"""
Markdown -> PDF renderer for the SIDM Round 5 deliverables.

Builds one PDF per markdown source. Verified on this host via the WSL venv
(/home/lamkuenai/.venv/bin/python, reportlab 4.5.1 + valid PIL).

FONT NOTE (this is the part that matters for a scientific document):
  reportlab's default Helvetica/Times lack ~50 Unicode math/astronomy glyphs
  (U+2070-U+209F sub/superscripts, U+2265-U+2273 math operators, and the Greek
  sigma / mu / phi / rho / sigma_peak characters the paper is full of). Those
  render as EMPTY BOXES even though text extraction returns the right
  characters - so extraction alone will NOT catch it.

  The fix used here is to register DejaVuSans (ships with matplotlib, covers
  Latin + Greek + math operators + super/subscripts) for body text and
  DejaVuSansMono for code blocks, and to map the ASCII '10^-54' style
  superscripts (AGENTS.md rule 27) rather than relying on Unicode super
  characters.

  DejaVu has NO CJK glyphs. The report quotes the Chinese-language n18 review
  (26 CJK ideographs), so a CJK face must be registered too and CJK runs
  wrapped in it - otherwise those characters render as .notdef (a null byte
  in the content stream, an empty box on the page) and the text is silently
  LOST to the reader. SimHei (C:/Windows/Fonts/simhei.ttf) covers all 26.

SILENT-LOSS NOTE:
  Preformatted does NOT wrap. A code line longer than the frame is drawn past
  the frame edge and CLIPPED - the characters vanish from the page and from
  text extraction, with no error. The companion had 34 such lines (the
  longest was 867 chars). Code lines are therefore hard-wrapped at CODE_WRAP
  columns, breaking at a space when there is one so that every source
  character is preserved.

Usage:
    wsl -- bash -c "/home/lamkuenai/.venv/bin/python /mnt/c/Users/<u>/<this>.py"
"""

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,
                                PageTemplate, Paragraph, Preformatted, Spacer,
                                Table, TableStyle)

# ---------------------------------------------------------------- fonts

def find_dejavu():
    """Locate DejaVuSans.ttf / DejaVuSansMono.ttf on this host."""
    cands = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
    ]
    for c in cands:
        if Path(c).exists():
            return c
    # matplotlib bundles them
    for root in Path('/home/lamkuenai').rglob('DejaVuSans.ttf'):
        return str(root)
    raise SystemExit('DejaVuSans.ttf not found')


def find_cjk():
    """Locate a CJK-capable face. DejaVu has no CJK glyphs at all."""
    cands = [
        '/mnt/c/Windows/Fonts/simhei.ttf',
        '/mnt/c/Windows/Fonts/msyh.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]
    for c in cands:
        if Path(c).exists():
            return c
    return None


def register_fonts():
    base = find_dejavu()
    mono = base.replace('DejaVuSans.ttf', 'DejaVuSansMono.ttf')
    if not Path(mono).exists():
        mono = base
    pdfmetrics.registerFont(TTFont('Body', base))
    pdfmetrics.registerFont(TTFont('Mono', mono))
    cjk = find_cjk()
    if cjk:
        # .ttc collections need a subfont index; simhei.ttf is a plain ttf
        if cjk.lower().endswith('.ttc'):
            pdfmetrics.registerFont(TTFont('CJK', cjk, subfontIndex=0))
        else:
            pdfmetrics.registerFont(TTFont('CJK', cjk))
    return base


# ---------------------------------------------------------------- text prep

# Unicode super/subscripts -> ASCII (AGENTS.md rule 27: PDF-safe form)
SUP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁻': '-', '⁺': '+',
}
SUB = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
}


def ascii_fold(t):
    """Fold Unicode super/subscripts to ASCII so they render everywhere."""
    for k, v in SUP.items():
        t = t.replace(k, v)
    for k, v in SUB.items():
        t = t.replace(k, v)
    return t


def esc(t):
    """Escape for reportlab Paragraph markup."""
    t = ascii_fold(t)
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


INLINE_CODE = re.compile(r'`([^`]+)`')
BOLD = re.compile(r'\*\*([^*]+)\*\*')
ITAL = re.compile(r'(?<!\*)\*([^*\n]+)\*(?!\*)')

# CJK ideographs + CJK punctuation + fullwidth forms. DejaVu has none of
# these; without a fallback face they become .notdef and the text is lost.
CJK = re.compile(r'([\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff'
                 r'\uff00-\uffef]+)')


def has_cjk_font():
    return 'CJK' in pdfmetrics.getRegisteredFontNames()


def wrap_cjk(t):
    """Wrap CJK runs in the CJK face so they are not rendered as .notdef."""
    if not has_cjk_font():
        return t
    return CJK.sub(r'<font face="CJK">\1</font>', t)


def inline(t):
    """Markdown inline -> reportlab mini-markup."""
    t = esc(t)
    # protect code spans
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f'\x00{len(spans) - 1}\x00'

    t = INLINE_CODE.sub(stash, t)
    t = BOLD.sub(r'<b>\1</b>', t)
    t = ITAL.sub(r'<i>\1</i>', t)
    for i, s in enumerate(spans):
        # inline code is set in the Mono face, which has a narrower glyph
        # coverage than the Body face -> fold the same way as code blocks
        t = t.replace(f'\x00{i}\x00',
                      f'<font face="Mono" size="7.6">{fold_mono(s)}</font>')
    return wrap_cjk(t)


# -------------------------------------------------------------- code wrapping

# Preformatted does not wrap: a long line is drawn past the frame edge and
# CLIPPED, so its tail silently disappears from the page. Hard-wrap instead,
# preferring a space break so every source character survives.
CODE_WRAP = 108

# DejaVu Sans Mono lacks a few glyphs that DejaVu Sans has (verified:
# U+226A 'much-less-than' is the only one in these documents). A glyph
# missing from the Mono face becomes .notdef - a null byte in the content
# stream and an empty box on the page. Substitute an ASCII equivalent.
MONO_FALLBACK = {
    '≪': '<<',   # much less than
    '≫': '>>',   # much greater than
}


def fold_mono(t):
    for k, v in MONO_FALLBACK.items():
        t = t.replace(k, v)
    return t


def wrap_code_lines(text, width=CODE_WRAP):
    out = []
    for line in text.split('\n'):
        if len(line) <= width:
            out.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        cont = ' ' * min(indent + 2, 12)
        rest = line
        first = True
        while len(rest) > width:
            cut = rest.rfind(' ', 0, width)
            if cut <= 0:
                cut = width
            out.append(rest[:cut].rstrip())
            rest = cont + rest[cut:].lstrip()
            first = False
        out.append(rest)
    return '\n'.join(out)


# ---------------------------------------------------------------- styles

def make_styles():
    body = ParagraphStyle('body', fontName='Body', fontSize=8.6, leading=12.2,
                          spaceAfter=5, alignment=TA_LEFT, textColor=colors.HexColor('#141414'))
    h1 = ParagraphStyle('h1', parent=body, fontSize=15, leading=19, spaceBefore=13,
                        spaceAfter=7, textColor=colors.HexColor('#0b3d63'))
    h2 = ParagraphStyle('h2', parent=body, fontSize=11.6, leading=15, spaceBefore=10,
                        spaceAfter=5, textColor=colors.HexColor('#12507f'))
    h3 = ParagraphStyle('h3', parent=body, fontSize=9.9, leading=13.4, spaceBefore=8,
                        spaceAfter=4, textColor=colors.HexColor('#2b5f88'))
    h4 = ParagraphStyle('h4', parent=body, fontSize=9.1, leading=12.4, spaceBefore=6,
                        spaceAfter=3, textColor=colors.HexColor('#3b6f96'))
    code = ParagraphStyle('code', parent=body, fontName='Mono', fontSize=6.6, leading=8.4,
                          spaceBefore=3, spaceAfter=3, leftIndent=7,
                          backColor=colors.HexColor('#f4f6f8'),
                          borderPadding=3, textColor=colors.HexColor('#1d2733'))
    bullet = ParagraphStyle('bullet', parent=body, leftIndent=12, bulletIndent=3,
                            spaceAfter=2.4)
    cap = ParagraphStyle('cap', parent=body, fontSize=7.4, leading=9.6,
                          textColor=colors.HexColor('#5a6b7b'))
    # F-QUOTE (v1.7): a blockquote is a CALLOUT, not a plain paragraph. Rendering it
    # as body text made the marker literal and flattened the emphasis inside it, so
    # a "> ### heading" callout printed as "### heading" with visible ** markers.
    quote = ParagraphStyle('quote', parent=body, fontSize=8.4, leading=11.8,
                            leftIndent=9, rightIndent=4, spaceBefore=4, spaceAfter=2,
                            textColor=colors.HexColor('#0b3d63'),
                            backColor=colors.HexColor('#f2f6fa'),
                            borderPadding=5)
    quote_h = ParagraphStyle('quote_h', parent=quote, fontSize=9.2, leading=12.4,
                              spaceBefore=4, spaceAfter=3,
                              textColor=colors.HexColor('#0b3d63'))
    return dict(body=body, h1=h1, h2=h2, h3=h3, h4=h4, code=code, bullet=bullet,
                cap=cap, quote=quote, quote_h=quote_h)


# ---------------------------------------------------------------- md -> flow

def md_to_flow(md, st):
    """Convert a markdown document into reportlab flowables."""
    lines = md.split('\n')
    flow = []
    i = 0
    in_code = False
    code_buf = []
    tbl_buf = []

    def flush_table():
        nonlocal tbl_buf
        if not tbl_buf:
            return
        rows = []
        for raw in tbl_buf:
            cells = [c.strip() for c in raw.strip().strip('|').split('|')]
            if all(set(c) <= set('-: ') and c for c in cells):
                continue                      # separator row
            rows.append(cells)
        if not rows:
            tbl_buf = []
            return
        ncol = max(len(r) for r in rows)
        rows = [r + [''] * (ncol - len(r)) for r in rows]
        data = [[Paragraph(inline(c), st['body']) for c in r] for r in rows]
        t = Table(data, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#c3ced9')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef4')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2.4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.4),
            ('FONTSIZE', (0, 0), (-1, -1), 7.4),
        ]))
        flow.append(Spacer(1, 3))
        flow.append(t)
        flow.append(Spacer(1, 4))
        tbl_buf = []

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        # fenced code
        if s.startswith('```'):
            if in_code:
                flow.append(Preformatted(
                    fold_mono(wrap_code_lines(ascii_fold('\n'.join(code_buf)))),
                    st['code']))
                code_buf = []
                in_code = False
            else:
                flush_table()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(ln)
            i += 1
            continue

        # table row
        if s.startswith('|') and s.endswith('|'):
            tbl_buf.append(ln)
            i += 1
            continue
        flush_table()

        # heading
        m = re.match(r'^(#{1,4})\s+(.*)$', s)
        if m:
            lvl = len(m.group(1))
            flow.append(Paragraph(inline(m.group(2)), st[f'h{lvl}']))
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r'-{3,}|\*{3,}|_{3,}', s):
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # bullet
        m = re.match(r'^[-*+]\s+(.*)$', s)
        if m:
            flow.append(Paragraph(inline(m.group(1)), st['bullet'], bulletText='•'))
            i += 1
            continue

        # numbered
        m = re.match(r'^(\d+)\.\s+(.*)$', s)
        if m:
            flow.append(Paragraph(inline(m.group(2)), st['bullet'],
                                  bulletText=f'{m.group(1)}.'))
            i += 1
            continue

        # blockquote -> CALLOUT (F-QUOTE, v1.7). A quote block is gathered as a unit:
        # consecutive '>' lines become ONE logical paragraph, so emphasis that spans
        # a line break still matches; a '> ### heading' inside it becomes a bold
        # callout heading rather than literal '###' text.
        if s.startswith('>'):
            qbuf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                qbuf.append(lines[i].strip().lstrip('>').strip())
                i += 1
            # split the quote into segments at heading lines; each segment is one
            # Paragraph so that a **...** spanning two source lines still renders.
            seg = []
            for qline in qbuf:
                mh = re.match(r'^#{1,6}\s+(.*)$', qline)
                if mh:
                    if seg:
                        flow.append(Paragraph(inline(' '.join(seg)), st['quote']))
                        seg = []
                    flow.append(Paragraph(f'<b>{inline(mh.group(1))}</b>', st['quote_h']))
                elif qline:
                    seg.append(qline)
            if seg:
                flow.append(Paragraph(inline(' '.join(seg)), st['quote']))
            continue

        if not s:
            i += 1
            continue

        # paragraph: gather until blank/structural line.
        # A continuation line may legitimately begin with '*' or '-' (e.g. a
        # line wrapped mid-emphasis such as "*mechanism* - the band is ...").
        # Only treat '*'/'-'/'+' as a list bullet when followed by a space;
        # otherwise the line continues the current paragraph.
        def is_block(t2):
            if (not t2 or t2.startswith(('#', '|', '```', '>'))):
                return True
            if re.match(r'^\d+\.\s', t2):
                return True
            if re.match(r'^[-*+]\s', t2):        # real bullet
                return True
            if re.fullmatch(r'-{3,}|\*{3,}|_{3,}', t2):   # hr
                return True
            return False

        buf = [s]
        j = i + 1
        while j < len(lines):
            t2 = lines[j].strip()
            if is_block(t2):
                break
            buf.append(t2)
            j += 1
        flow.append(Paragraph(inline(' '.join(buf)), st['body']))
        i = j

    flush_table()
    if in_code and code_buf:
        flow.append(Preformatted(
            fold_mono(wrap_code_lines(ascii_fold('\n'.join(code_buf)))),
            st['code']))
    return flow


# ---------------------------------------------------------------- build

def build(md_path, pdf_path, title):
    md = Path(md_path).read_text(encoding='utf-8')
    st = make_styles()
    flow = md_to_flow(md, st)

    # cover
    cover = [
        Spacer(1, 34 * mm),
        Paragraph(f'<b>{inline(title)}</b>', ParagraphStyle(
            'c1', fontName='Body', fontSize=20, leading=25,
            textColor=colors.HexColor('#0b3d63'), alignment=1)),
        Spacer(1, 5 * mm),
        Paragraph('SIDM v19.2-F &nbsp;|&nbsp; Round 5 + n18 + n19 + n20 review response',
                  ParagraphStyle('c2', fontName='Body', fontSize=10.5, leading=14,
                                 textColor=colors.HexColor('#4a6076'), alignment=1)),
        Spacer(1, 3 * mm),
        Paragraph('Branch <b>wip/v19.2-F-init</b>',
                  ParagraphStyle('c3', fontName='Body', fontSize=9, leading=12,
                                 textColor=colors.HexColor('#6b7c8d'), alignment=1)),
        Spacer(1, 14 * mm),
    ]
    # fold the leading H1 out of the body (it is on the cover)
    if flow and hasattr(flow[0], 'text') and flow[0].text.startswith('<b>'):
        flow = flow[1:]

    doc = BaseDocTemplate(pdf_path, pagesize=A4,
                          leftMargin=17 * mm, rightMargin=15 * mm,
                          topMargin=16 * mm, bottomMargin=15 * mm,
                          title=title, author='SIDM v19.2-F project')
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='n')

    def deco(canvas, d):
        canvas.saveState()
        canvas.setFont('Body', 7)
        canvas.setFillColor(colors.HexColor('#7b8b9b'))
        canvas.drawString(17 * mm, 9 * mm, 'SIDM v19.2-F - Round 5 + n18 + n19 + n20 review response')
        canvas.drawRightString(A4[0] - 15 * mm, 9 * mm, f'page {d.page}')
        canvas.setStrokeColor(colors.HexColor('#d3dde6'))
        canvas.setLineWidth(0.4)
        canvas.line(17 * mm, 11.5 * mm, A4[0] - 15 * mm, 11.5 * mm)
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='cover', frames=[frame], onPage=deco),
        PageTemplate(id='body', frames=[frame], onPage=deco),
    ])
    doc.build(cover + [Spacer(1, 2 * mm),
                       Paragraph('&nbsp;', st['body'])] + flow)
    return Path(pdf_path).stat().st_size


if __name__ == '__main__':
    register_fonts()
    OUT = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    JOBS = [
        (sys.argv[2], sys.argv[3], 'Consolidated Fixes Report - v1.11'),
        (sys.argv[4], sys.argv[5], 'Changed Code Companion - v1.9'),
    ]
    for md_path, pdf_path, title in JOBS:
        n = build(md_path, pdf_path, title)
        print(f'OK {pdf_path}  {n} bytes')
