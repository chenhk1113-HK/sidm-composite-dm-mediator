"""Single source of truth for the PDF builder's character re-encode maps.

Introduced by the n24 review round (2026-10-31), item 3: the glyph-coverage
audit (gate layer 14) previously hand-copied the builder's superscript/
subscript strip map ("These MUST mirror build_round5_report_pdfs.py ...",
a comment holding two tables together). That is the copy-paste drift vector
CG-6 closed for the physics scripts; the same pattern in a checker is worse,
because a checker's table is read as evidence. The mirror is now a reference:
the builder and the audit both import these maps, so drift is impossible by
construction.

Maps (behaviour unchanged — these are the builder's documented maps, moved
here verbatim):
  SUP / SUB  : Unicode super/subscript characters -> ASCII forms
               (AGENTS.md rule 27: PDF-safe notation, renders everywhere)
  MONO_FALLBACK : glyphs missing from DejaVu Sans Mono -> ASCII substitutes
               (a Mono-missing glyph renders as .notdef: a null byte in the
               content stream and an empty box on the page)
"""

# Unicode super/subscripts -> ASCII (AGENTS.md rule 27: PDF-safe form)
SUP = {
    '\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3', '\u2074': '4',
    '\u2075': '5', '\u2076': '6', '\u2077': '7', '\u2078': '8', '\u2079': '9',
    '\u207b': '-', '\u207a': '+',
}
SUB = {
    '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3', '\u2084': '4',
    '\u2085': '5', '\u2086': '6', '\u2087': '7', '\u2088': '8', '\u2089': '9',
}

# DejaVu Sans Mono lacks a few glyphs that DejaVu Sans has (verified:
# U+226A 'much-less-than' is the only one in these documents). A glyph
# missing from the Mono face becomes .notdef - a null byte in the content
# stream and an empty box on the page. Substitute an ASCII equivalent.
MONO_FALLBACK = {
    '\u226a': '<<',   # much less than
    '\u226b': '>>',   # much greater than
}


# ------------------------------------------------------------ mono pipeline
# The exact transform a code fence undergoes on its way to the page:
#   ascii_fold  (Unicode super/subscripts -> ASCII caret form)
#   fold_mono   (glyphs missing from DejaVu Sans Mono -> ASCII)
#   wrap_code_lines (Preformatted does not wrap; hard-wrap at CODE_WRAP so
#                    no line is drawn past the frame and clipped)
# Moved here from build_round5_report_pdfs.py (n24 round): audit_pdf_render.py
# must predict the builder's WRAPPED line fragments exactly — a source comment
# longer than CODE_WRAP renders as several PDF lines, and a leak whitelist
# that only knows whole source lines flags every such fragment as a 'heading
# marker leak' (observed on the n24 closeout build). Single source of truth:
# builder and audit import the same functions.

CODE_WRAP = 108


def ascii_fold(t):
    """Fold Unicode super/subscripts to ASCII so they render everywhere."""
    for k, v in SUP.items():
        t = t.replace(k, v)
    for k, v in SUB.items():
        t = t.replace(k, v)
    return t


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
        while len(rest) > width:
            # Search for a break point STRICTLY past the continuation indent:
            # rfind over [0, width) can land on a continuation line's own
            # indent spaces (or a line's leading space), producing an empty
            # fragment and a rest of unchanged length — an infinite loop that
            # hung the builder on any long line without a usable space
            # (found by the n24 closeout's own unit probe, 2026-11-01).
            cut = rest.rfind(' ', len(cont) + 1, width)
            if cut < 0:
                cut = width  # force a hard break; length strictly decreases
            out.append(rest[:cut].rstrip())
            rest = cont + rest[cut:].lstrip()
        out.append(rest)
    return '\n'.join(out)


def render_code_block(text):
    """The exact lines a fenced code block produces in the built PDF:
    fold_mono(wrap_code_lines(ascii_fold(text))) split into lines.
    The builder renders this; the render audit whitelists it."""
    return fold_mono(wrap_code_lines(ascii_fold(text))).split('\n')
