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
