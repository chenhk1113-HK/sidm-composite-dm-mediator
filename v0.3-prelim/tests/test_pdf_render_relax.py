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


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("ALL PASS")
