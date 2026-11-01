"""n24-round containment unit test (2026-11-01): exponent-fold semantics.

The report builder ASCII-folds super/subscripts at BUILD time
(pdf_rencode_maps.SUP/SUB: '10⁻¹²' -> '10-12', 'f_H²σ' -> 'f_H2σ'), so the
rendered PDFs carry the exponent as ONE fused token. audit_pdf_render's
relax_tokens must model BOTH rendering worlds — split fragments for
raised-baseline glyphs, the fused form for the builder fold — and score
them as SEPARATE variants (merging dilutes coverage with stray fragments).
Before this fix the fused spelling was invisible to the audit and eight
correctly-rendered exponent lines on the frozen-good v1.14 PDF were
flagged as missing content.

Tests import the REAL functions from the audit module (module-level after
the 2026-11-01 lift; no re-implemented copies).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import audit_pdf_render as apr


def test_split_variant_unchanged():
    # tail() normalization now applies to fragments too (symmetric pipeline):
    # '-12' loses its glyph-drop leading hyphen exactly as a caret-free token
    # would; the exponent digits are preserved.
    out = apr.relax_tokens(["7.5x10^-12"])
    assert out == ["7.5x10", "12"]


def test_quote_edge_is_stripped_on_both_sides():
    # The n24 bug: source token '"7.5x10^-12' (curly quote glued on) kept the
    # quote in the caret branch while the PDF side stripped it -> a present
    # token read as absent. tail() now runs on every emitted variant.
    src = apr.relax_tokens(['\u201c7.5x10^-12'], fuse=True)
    pdf = apr.relax_tokens(['\u201c7.5x10-12'])
    assert src == pdf == ["7.5x10-12"]


def test_fused_variant_emits_builder_fold():
    out = apr.relax_tokens(["7.5x10^-12"], fuse=True)
    assert out == ["7.5x10-12"]


def test_fused_variant_superscript_letters():
    # canonical() maps unicode superscript ² via the caret expansion; the
    # fold rejoins neighbours and tail() applies '?'->'-' + lowercase on
    # both variants symmetrically — matching the builder-folded PDF token
    # 'f_H2?_HH' exactly.
    out = apr.relax_tokens(["f_H^2?_HH"], fuse=True)
    assert out == ["f_h2-_hh"]
    out2 = apr.relax_tokens(["f_H^2?_HH"])
    assert out2 == ["f_h", "2-_hh"]
    # and the real PDF token relaxes to the identical fused spelling:
    assert apr.relax_tokens(["f_H2?_HH"]) == ["f_h2-_hh"]


def test_coverage_matches_builder_folded_pdf_only_via_fused():
    # PDF-side token stream as extracted from the real folded PDF.
    pdf_tokens = ["reviewer", "b", "claim", "3", "7.5x10-12", "is",
                  "inconsistent", "with", "the", "canonical"]
    tri = apr._trigrams(pdf_tokens)
    tri_set = set(tri)
    src = ["reviewer", "b", "claim", "3", "7.5x10^-12", "is",
           "inconsistent", "with", "the", "canonical"]
    cov_split, miss_split = apr._coverage(apr.relax_tokens(src), tri_set)
    cov_fused, miss_fused = apr._coverage(apr.relax_tokens(src, fuse=True), tri_set)
    assert cov_fused == 1.0 and miss_fused == 0
    assert cov_split < 1.0 and miss_split > 0  # split fails in the folded world


def test_true_absence_still_caught():
    # If the exponent content is genuinely absent from the PDF, NEITHER
    # variant may rescue it.
    pdf_tokens = ["the", "canonical", "value", "is", "inconsistent",
                  "regime", "labels", "differ"]
    tri_set = set(apr._trigrams(pdf_tokens))
    src = ["the", "canonical", "value", "10^-13", "is", "inconsistent",
           "regime", "labels", "differ"]
    cov_s, miss_s = apr._coverage(apr.relax_tokens(src), tri_set)
    cov_f, miss_f = apr._coverage(apr.relax_tokens(src, fuse=True), tri_set)
    assert miss_s > 0 and miss_f > 0
    assert cov_s < 0.90 or cov_f < 0.90




# ---------------------------------------------------------------------------
# n24 addendum (2026-11-01): wrapped-comment whitelist.
# A fenced comment longer than CODE_WRAP is hard-wrapped by the builder into
# several PDF lines. The leak whitelist must know the builder's EXACT
# fragments, and the only safe way to know them is to import the same module
# the builder uses. These tests lock that contract.
# ---------------------------------------------------------------------------

def _wrapping_fragments():
    from pdf_rencode_maps import render_code_block, CODE_WRAP
    comment = ("# (pdf_rencode_maps.SUP/SUB -- '10-12' is drawn as '10-12' "
               "and 'f_H2' as 'f_H2'), so these PDFs carry the exponent as "
               "ONE fused token whenever the fold applies")
    assert len(comment) > CODE_WRAP
    return render_code_block(comment), comment


def test_wrapped_comment_fragments_start_with_hash_or_cont():
    frags, _ = _wrapping_fragments()
    assert len(frags) >= 2
    assert frags[0].startswith("#")
    # continuation lines carry the builder's indent (>= 2 spaces), never '#'
    assert all(not f.startswith("#") and f.startswith("  ") for f in frags[1:])


def test_wrap_preserves_every_word():
    frags, src = _wrapping_fragments()
    src_words = src.split()
    frag_words = " ".join(frags).split()
    assert frag_words == src_words  # hard-wrap at spaces: no word lost


def test_builder_uses_the_shared_functions_not_local_copies():
    """Anti-drift lock: build_round5_report_pdfs must import the shared
    wrap/fold pipeline, never redefine it locally (the layer-14 drift class)."""
    import build_round5_report_pdfs as b
    import pdf_rencode_maps as m
    assert b.wrap_code_lines is m.wrap_code_lines
    assert b.ascii_fold is m.ascii_fold
    assert b.fold_mono is m.fold_mono
    assert b.CODE_WRAP == m.CODE_WRAP


def test_audit_whitelist_includes_wrapped_fragments():
    """The audit's leak whitelist must accept a builder-wrapped comment
    fragment that starts with '#', not flag it as a heading leak."""
    import audit_pdf_render as a
    frags, src = _wrapping_fragments()
    # Build the probe set exactly as the audit does (its code_probes loop)
    import re
    probes = set()
    for cl in [src]:
        n = a._norm(cl)
        probes.add(n)
        probes.add(re.sub(r"^#+\s*", "", n))
        probes.add(re.sub(r"\s{2,}", " ", n))
        probes.add(re.sub(r"^#+\s*", "", re.sub(r"\s{2,}", " ", n)))
        for frag in a.render_code_block(cl):
            f = a._norm(frag)
            probes.add(f)
            probes.add(re.sub(r"^#+\s*", "", f))
    leaked_like = frags[0].strip()          # the flagged line form
    n = a._norm(leaked_like)
    assert n in probes or re.sub(r"^#+\s*", "", n) in probes


def test_wrap_terminates_on_spaceless_long_line():
    """Regression (n24 closeout probe 2026-11-01): the pre-fix wrap searched
    for a break point over the WHOLE line width, could cut on a continuation
    line's own indent spaces, and looped forever on a >CODE_WRAP line with no
    usable space. Wrap must terminate and produce only non-empty fragments."""
    from pdf_rencode_maps import wrap_code_lines, CODE_WRAP
    line = "# " + "x" * (CODE_WRAP + 44)
    out = wrap_code_lines(line)          # must RETURN (the old code hung)
    frags = out.splitlines()
    assert len(frags) >= 2
    assert all(f.strip() for f in frags)
    # no character lost across the wrap (spaces are where the breaks happen)
    assert "".join(f.replace(" ", "") for f in frags) == line.replace(" ", "")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("ALL PASS")
